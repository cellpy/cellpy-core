import logging
from dataclasses import asdict
from typing import Optional, Sequence, TypeVar, Union


from cellpycore import selectors
from cellpycore.config import Schema, default_schema
from cellpycore.cell_core import Data
from cellpycore.legacy import CellpyLimits

logger = logging.getLogger(__name__)


DataFrame = TypeVar("DataFrame")
Array = TypeVar("Array")


# The summarizer bodies read their column names from an injected ``Schema`` (see
# config.Schema) instead of module-level header globals. This keeps the engine
# schema-agnostic and thread-safe; the legacy bridge (OldCellpyCellCore) injects
# the legacy-named schema, a native CellpyCellCore injects the native one.


# Standalone default step-detection limits, derived from the CellpyLimits
# mirror so they match legacy cellpy. When cellpy drives the engine it passes
# its own instrument ``raw_limits`` by value, so this default only applies to
# standalone cellpy-core use.
DEFAULT_RAW_LIMITS = asdict(CellpyLimits())

# Number of digits used when rounding the per-step C-rate (matches legacy cellpy).
DIGITS_C_RATE = 5


def _ustep(n: Array) -> list:
    # not tested
    """Create u-steps from a pandas Series.

    Args:
        n (Array): The input series.

    Returns:
        list: The u-steps.
    """
    un = []
    c = 0
    dn = n.diff()
    for i in dn:
        if i != 0:
            c += 1
        un.append(c)
    return un


def make_step_table(
    data: Data,
    schema: Optional[Schema] = None,
    step_specifications=None,
    short=False,
    override_step_types=None,
    override_raw_limits=None,
    usteps=False,
    add_c_rate=True,
    nom_cap=None,
    skip_steps=None,
    sort_rows=True,
    from_data_point=None,
    raw_limits: dict = DEFAULT_RAW_LIMITS,
) -> Union[Data, DataFrame]:
    """Create a table (v.5) that contains summary information for each step.

    This function creates a table containing information about the
    different steps for each cycle and, based on that, decides what type of
    step it is (e.g. charge) for each cycle.

    The format of the steps is:

    - index: cycleno - stepno - sub-step-no - ustep
    - Time info: average, stdev, max, min, start, end, delta
    - Logging info: average, stdev, max, min, start, end, delta
    - Current info: average, stdev, max, min, start, end, delta
    - Voltage info: average,  stdev, max, min, start, end, delta
    - Type: (from pre-defined list) - SubType
    - Info: not used.

    Args:
        data (core.Data): The data object.
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        step_specifications (pandas.DataFrame): step specifications
        short (bool): step specifications in short format
        override_step_types (dict): override the provided step types, for example set all
            steps with step number 5 to "charge" by providing {5: "charge"}.
        override_raw_limits (dict): override the instrument limits (resolution), for example set
            'current_hard' to 0.1 by providing {'current_hard': 0.1}.
        usteps (bool): investigate all steps including same steps within
            one cycle (this is useful for e.g. GITT).
        add_c_rate (bool): include a per-step C-rate estimate (rate_avr).
        nom_cap (float): the absolute nominal capacity used to compute the C-rate
            (rate_avr = abs(current_avr / nom_cap)). Supplied by the caller (by
            value) so this function needs no unit handling. Defaults to 1.0.
        skip_steps (list of integers): list of step numbers that should not
            be processed (future feature - not used yet).
        sort_rows (bool): sort the rows after processing.
        from_data_point (int): first data point to use.
        raw_limits (dict): the raw limits (resolution) for the instrument.

    Returns:
        core.Data: The data object with the step table added if from_data_point is None,
          otherwise the step table is returned as a DataFrame.

    """
    if schema is None:
        schema = default_schema()
    nhdr = schema.raw
    shdr = schema.step

    def delta(x):
        # Remark! this will not work if x is a TimeDelta object
        if x.iloc[0] == 0.0:
            # starts from a zero value
            difference = 100.0 * x.iloc[-1]
        else:
            difference_factor = 100.0 * (x.iloc[-1] - x.iloc[0])
            difference_dividend = abs(x.iloc[0])
            difference = difference_factor / difference_dividend

        return difference

    if from_data_point is not None:
        df = data.raw.loc[data.raw[nhdr.data_point_txt] >= from_data_point]
    else:
        df = data.raw
    # df[shdr.internal_resistance_change] = \
    #     df[nhdr.internal_resistance_txt].pct_change()

    # selecting only the most important columns from raw:
    keep = [
        nhdr.data_point_txt,
        nhdr.test_time_txt,
        nhdr.step_time_txt,
        nhdr.step_index_txt,
        nhdr.cycle_index_txt,
        nhdr.current_txt,
        nhdr.voltage_txt,
        nhdr.ref_voltage_txt,
        nhdr.charge_capacity_txt,
        nhdr.discharge_capacity_txt,
        nhdr.internal_resistance_txt,
        # "ir_pct_change"
    ]

    # only use col-names that exist:
    keep = [col for col in keep if col in df.columns]
    df = df[keep]
    # preparing for implementation of sub_steps (will come in the future):
    df = df.assign(**{f"{nhdr.sub_step_index_txt}": 1})

    # using headers as defined in the schema
    rename_dict = {
        nhdr.cycle_index_txt: shdr.cycle,
        nhdr.step_index_txt: shdr.step,
        nhdr.sub_step_index_txt: shdr.sub_step,
        nhdr.data_point_txt: shdr.point,
        nhdr.test_time_txt: shdr.test_time,
        nhdr.step_time_txt: shdr.step_time,
        nhdr.current_txt: shdr.current,
        nhdr.voltage_txt: shdr.voltage,
        nhdr.charge_capacity_txt: shdr.charge,
        nhdr.discharge_capacity_txt: shdr.discharge,
        nhdr.internal_resistance_txt: shdr.internal_resistance,
    }

    df = df.rename(columns=rename_dict)
    by = [shdr.cycle, shdr.step, shdr.sub_step]

    if skip_steps is not None:
        logging.debug(f"omitting steps {skip_steps}")
        df = df.loc[~df[shdr.step].isin(skip_steps)]

    if usteps:
        by.append(shdr.ustep)
        df[shdr.ustep] = _ustep(df[shdr.step])

    logging.debug(f"groupby: {by}")

    # TODO: make sure that all columns are numeric

    gf = df.groupby(by=by)

    # TODO: FutureWarning: The provided callable <function mean at 0x000002BD4D332840>
    #  is currently using SeriesGroupBy.mean. In a future version of pandas, the provided
    #  callable will be used directly. To keep current behavior pass the string "mean" instead.
    df_steps = gf.agg(["mean", "std", "min", "max", "first", "last", delta]).rename(
        columns={"amin": "min", "amax": "max", "mean": "avr"}
    )

    df_steps = df_steps.reset_index()

    # column with C-rates (rate_avr = abs(current_avr / nom_cap)). The nominal
    # capacity is supplied by the caller (by value); no unit conversion is done
    # with the current values here (matching legacy cellpy).
    if add_c_rate:
        _nom_cap = nom_cap if nom_cap is not None else 1.0
        df_steps[shdr.rate_avr] = abs(
            round(
                df_steps.loc[:, (shdr.current, "avr")] / _nom_cap,
                DIGITS_C_RATE,
            )
        )

    df_steps[shdr.type] = ""
    df_steps[shdr.sub_type] = ""
    df_steps[shdr.info] = ""

    if step_specifications is None:
        # TODO: refactor this:
        if override_raw_limits is None:
            override_raw_limits = {}
        current_limit_value_hard = (
            override_raw_limits.get("current_hard", None) or raw_limits["current_hard"]
        )
        stable_current_limit_soft = (
            override_raw_limits.get("stable_current_soft", None)
            or raw_limits["stable_current_soft"]
        )
        stable_voltage_limit_hard = (
            override_raw_limits.get("stable_voltage_hard", None)
            or raw_limits["stable_voltage_hard"]
        )
        stable_charge_limit_hard = (
            override_raw_limits.get("stable_charge_hard", None)
            or raw_limits["stable_charge_hard"]
        )

        mask_no_current_hard = (
            df_steps.loc[:, (shdr.current, "max")].abs()
            + df_steps.loc[:, (shdr.current, "min")].abs()
        ) < current_limit_value_hard / 2

        mask_voltage_down = (
            df_steps.loc[:, (shdr.voltage, "delta")] < -stable_voltage_limit_hard
        )

        mask_voltage_up = (
            df_steps.loc[:, (shdr.voltage, "delta")] > stable_voltage_limit_hard
        )

        mask_voltage_stable = (
            df_steps.loc[:, (shdr.voltage, "delta")].abs() < stable_voltage_limit_hard
        )

        mask_current_down = (
            df_steps.loc[:, (shdr.current, "delta")] < -stable_current_limit_soft
        )

        mask_current_negative = (
            df_steps.loc[:, (shdr.current, "avr")] < -current_limit_value_hard
        )

        mask_current_positive = (
            df_steps.loc[:, (shdr.current, "avr")] > current_limit_value_hard
        )

        mask_charge_changed = (
            df_steps.loc[:, (shdr.charge, "delta")].abs() > stable_charge_limit_hard
        )

        mask_discharge_changed = (
            df_steps.loc[:, (shdr.discharge, "delta")].abs() > stable_charge_limit_hard
        )

        mask_no_change = (
            (df_steps.loc[:, (shdr.voltage, "delta")] == 0)
            & (df_steps.loc[:, (shdr.current, "delta")] == 0)
            & (df_steps.loc[:, (shdr.charge, "delta")] == 0)
            & (df_steps.loc[:, (shdr.discharge, "delta")] == 0)
        )

        # TODO: make an option for only checking unique steps
        #     e.g.
        #     df_x = df_steps.where.steps.are.unique

        # TODO: FutureWarning: Setting an item of incompatible dtype is deprecated and will raise in a future error
        #  of pandas. Value 'rest' has dtype incompatible with float64, please explicitly cast to a
        #  compatible dtype first.

        df_steps.loc[
            mask_no_current_hard & mask_voltage_stable,
            (shdr.type, slice(None)),
        ] = "rest"

        df_steps.loc[
            mask_no_current_hard & mask_voltage_up, (shdr.type, slice(None))
        ] = "ocvrlx_up"

        df_steps.loc[
            mask_no_current_hard & mask_voltage_down, (shdr.type, slice(None))
        ] = "ocvrlx_down"

        df_steps.loc[
            mask_discharge_changed & mask_current_negative,
            (shdr.type, slice(None)),
        ] = "discharge"

        df_steps.loc[
            mask_charge_changed & mask_current_positive,
            (shdr.type, slice(None)),
        ] = "charge"

        df_steps.loc[
            mask_voltage_stable & mask_current_negative & mask_current_down,
            (shdr.type, slice(None)),
        ] = "cv_discharge"

        df_steps.loc[
            mask_voltage_stable & mask_current_positive & mask_current_down,
            (shdr.type, slice(None)),
        ] = "cv_charge"

        # --- internal resistance ----
        df_steps.loc[mask_no_change, (shdr.type, slice(None))] = "ir"
        # assumes that IR is stored in just one row

        # --- sub-step-txt -----------
        df_steps[shdr.sub_type] = None

        # --- CV steps ----

        # "voltametry_charge"
        # mask_charge_changed
        # mask_voltage_up
        # (could also include abs-delta-cumsum current)

        # "voltametry_discharge"
        # mask_discharge_changed
        # mask_voltage_down

        if override_step_types is not None:
            for step, step_type in override_step_types.items():
                df_steps.loc[
                    df_steps[shdr.step] == step,
                    (shdr.type, slice(None)),
                ] = step_type

    else:
        # not tested!
        logger.debug("parsing custom step definition")
        if not short:
            logger.debug("using long format (cycle,step)")
            for row in step_specifications.itertuples():
                df_steps.loc[
                    (df_steps[shdr.step] == row.step)
                    & (df_steps[shdr.cycle] == row.cycle),
                    (shdr.type, slice(None)),
                ] = row.type
                df_steps.loc[
                    (df_steps[shdr.step] == row.step)
                    & (df_steps[shdr.cycle] == row.cycle),
                    (shdr.info, slice(None)),
                ] = row.info
        else:
            logger.debug("using short format (step)")
            for row in step_specifications.itertuples():
                df_steps.loc[
                    df_steps[shdr.step] == row.step,
                    (shdr.type, slice(None)),
                ] = row.type
                df_steps.loc[
                    df_steps[shdr.step] == row.step,
                    (shdr.info, slice(None)),
                ] = row.info

    # check if all the steps got categorizes
    logger.debug("looking for un-categorized steps")
    empty_rows = df_steps.loc[df_steps[shdr.type].isnull()]
    if not empty_rows.empty:
        logger.warning(
            f"found {len(empty_rows)}:{len(df_steps)} non-categorized steps (please, check your raw-limits)"
        )
        # logging.debug(empty_rows)

    # flatten (possible remove in the future),

    logger.debug("flatten columns")
    flat_cols = []
    for col in df_steps.columns:
        if isinstance(col, tuple):
            if col[-1]:
                col = "_".join(col)
            else:
                col = col[0]
        flat_cols.append(col)

    df_steps.columns = flat_cols
    if sort_rows:
        logger.debug("sorting the step rows")
        # TODO: [#index]
        # if this throws a KeyError: 'test_time_first' it probably
        # means that the df contains a non-nummeric 'test_time' column.
        df_steps = df_steps.sort_values(
            by=shdr.test_time + "_first"
        ).reset_index()

    if from_data_point is not None:
        return df_steps
    else:
        data.steps = df_steps
        return data


def generate_absolute_summary_columns(
    data: Data,
    schema: Optional[Schema] = None,
    _first_step_txt: Optional[str] = None,
    _second_step_txt: Optional[str] = None,
) -> Data:
    """Generate absolute summary columns.

    Args:
        data (Data): The data object.
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        _first_step_txt (str): The first step text. Defaults to the raw
            charge-capacity header.
        _second_step_txt (str): The second step text. Defaults to the raw
            discharge-capacity header.
    """
    if schema is None:
        schema = default_schema()
    nhdr = schema.raw
    shdr_sum = schema.cycle

    if _first_step_txt is None:
        _first_step_txt = nhdr.charge_capacity_txt
    if _second_step_txt is None:
        _second_step_txt = nhdr.discharge_capacity_txt

    summary = data.summary

    # Coulombic efficiency
    summary[shdr_sum.coulombic_efficiency] = (
        100 * summary[_second_step_txt] / summary[_first_step_txt]
    )
    summary[shdr_sum.cumulated_coulombic_efficiency] = summary[
        shdr_sum.coulombic_efficiency
    ].cumsum()

    # Capacity columns
    capacity_columns = {
        shdr_sum.charge_capacity: summary[nhdr.charge_capacity_txt],
        shdr_sum.discharge_capacity: summary[nhdr.discharge_capacity_txt],
    }
    summary = summary.assign(**capacity_columns)

    # Cumulated capacity columns
    calculated_from_capacity_columns = {
        shdr_sum.cumulated_charge_capacity: summary[
            shdr_sum.charge_capacity
        ].cumsum(),
        shdr_sum.cumulated_discharge_capacity: summary[
            shdr_sum.discharge_capacity
        ].cumsum(),
        shdr_sum.discharge_capacity_loss: (
            summary[shdr_sum.discharge_capacity].shift(1)
            - summary[shdr_sum.discharge_capacity]
        ),
        shdr_sum.charge_capacity_loss: (
            summary[shdr_sum.charge_capacity].shift(1)
            - summary[shdr_sum.charge_capacity]
        ),
        shdr_sum.coulombic_difference: (
            summary[_first_step_txt] - summary[_second_step_txt]
        ),
    }
    summary = summary.assign(**calculated_from_capacity_columns)

    # Cumulated coulombic difference
    calculated_from_coulombic_efficiency_columns = {
        shdr_sum.cumulated_coulombic_difference: summary[
            shdr_sum.coulombic_difference
        ].cumsum(),
    }
    summary = summary.assign(**calculated_from_coulombic_efficiency_columns)

    # Cumulated capacity loss columns
    calculated_from_capacity_loss_columns = {
        shdr_sum.cumulated_discharge_capacity_loss: summary[
            shdr_sum.discharge_capacity_loss
        ].cumsum(),
        shdr_sum.cumulated_charge_capacity_loss: summary[
            shdr_sum.charge_capacity_loss
        ].cumsum(),
    }
    summary = summary.assign(**calculated_from_capacity_loss_columns)

    # Shifted capacity columns
    individual_edge_movement = summary[_first_step_txt] - summary[_second_step_txt]
    shifted_charge_capacity_column = {
        shdr_sum.shifted_charge_capacity: individual_edge_movement.cumsum(),
    }
    summary = summary.assign(**shifted_charge_capacity_column)

    shifted_discharge_capacity_column = {
        shdr_sum.shifted_discharge_capacity: summary[
            shdr_sum.shifted_charge_capacity
        ]
        + summary[_first_step_txt],
    }
    summary = summary.assign(**shifted_discharge_capacity_column)

    ric = (summary[_first_step_txt].shift(1) - summary[_second_step_txt]) / summary[
        _second_step_txt
    ].shift(1)
    ric_column = {shdr_sum.cumulated_ric: ric.cumsum()}
    summary = summary.assign(**ric_column)
    summary[shdr_sum.cumulated_ric] = ric.cumsum()
    ric_sei = (summary[_first_step_txt] - summary[_second_step_txt].shift(1)) / summary[
        _second_step_txt
    ].shift(1)
    ric_sei_column = {shdr_sum.cumulated_ric_sei: ric_sei.cumsum()}
    summary = summary.assign(**ric_sei_column)
    ric_disconnect = (
        summary[_second_step_txt].shift(1) - summary[_second_step_txt]
    ) / summary[_second_step_txt].shift(1)
    ric_disconnect_column = {
        shdr_sum.cumulated_ric_disconnect: ric_disconnect.cumsum()
    }
    data.summary = summary.assign(**ric_disconnect_column)

    return data


def generate_specific_summary_columns(
    data: Data,
    mode: str,
    specific_columns: Sequence,
    specific_converter: float,
) -> Data:
    """
    Generate specific summary columns.

    The unit conversion is handled by value: the caller computes the conversion
    factor (e.g. via the consumer's own pint-based machinery) and passes it in,
    so this function does no unit handling itself.

    Args:
        data (Data): The data object.
        mode (str): The mode of the data (gravimetric, areal or absolute).
        specific_columns (Sequence): The columns to generate specific summary columns for.
        specific_converter (float): The precomputed conversion factor to multiply
            the absolute columns by to obtain the specific (per mode) values.

    Returns:
        Data: The data object with the specific summary columns added to the summary.
    """
    summary = data.summary
    for col in specific_columns:
        logger.debug(f"generating specific column {col}_{mode}")
        summary[f"{col}_{mode}"] = specific_converter * summary[col]
    data.summary = summary
    return data


def end_voltage_to_summary(data: Data, schema: Optional[Schema] = None) -> Data:
    """
    Add end-voltage columns to the summary.

    Args:
        data (Data): The data object.
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.

    Returns:
        Data: The data object with the end-voltage columns added to the summary.
    """
    if schema is None:
        schema = default_schema()
    headers_summary = schema.cycle
    headers_steps = schema.step

    # TODO: refactor this to use the correct headers and parameters when we have decided on them:
    DISCHARGE_TYPE_PREFIX = "discharge"
    CHARGE_TYPE_PREFIX = "charge"
    header_summary_cycle = headers_summary.cycle_index
    header_steps_cycle = headers_steps.cycle
    header_steps_voltage_last = f"{headers_steps.voltage}_last"

    summary = data.summary
    steps = data.steps

    discharge_steps = steps.loc[
        steps["type"].str.startswith(DISCHARGE_TYPE_PREFIX),
        [header_steps_cycle, header_steps_voltage_last],
    ]
    charge_steps = steps.loc[
        steps["type"].str.startswith(CHARGE_TYPE_PREFIX),
        [header_steps_cycle, header_steps_voltage_last],
    ]
    charge_steps = charge_steps.rename(
        columns={
            header_steps_cycle: header_summary_cycle,
            header_steps_voltage_last: headers_summary.end_voltage_charge,
        }
    )
    discharge_steps = discharge_steps.rename(
        columns={
            header_steps_cycle: header_summary_cycle,
            header_steps_voltage_last: headers_summary.end_voltage_discharge,
        }
    )

    # A cycle can contain several charge/discharge-type steps (e.g. discharge +
    # cv_discharge). Keep only the last one per cycle (matching legacy cellpy's
    # "selecting last" behaviour) so the left-merge does not multiply summary rows.
    discharge_steps = discharge_steps.drop_duplicates(
        subset=[header_summary_cycle], keep="last"
    )
    charge_steps = charge_steps.drop_duplicates(
        subset=[header_summary_cycle], keep="last"
    )

    summary = summary.merge(discharge_steps, on=header_summary_cycle, how="left")
    summary = summary.merge(charge_steps, on=header_summary_cycle, how="left")

    data.summary = summary

    return data


def _calculate_nominal_capacity_from_cycles(
    summary: DataFrame,
    schema: Schema,
    normalization_cycles: Union[Sequence, int],
    step_txt: str,
) -> float:
    """
    Calculate nominal capacity from specified normalization cycles.

    Args:
        summary: The summary DataFrame containing cycle data.
        schema: The column-header schema to use.
        normalization_cycles: The cycles to use for normalization (can be int or sequence).
        step_txt: The header string for the capacity column.

    Returns:
        float: The calculated nominal capacity.
    """
    logger.info(
        f"Using these cycles for finding the nominal capacity: {normalization_cycles}"
    )
    if not isinstance(normalization_cycles, (list, tuple)):
        normalization_cycles = [normalization_cycles]

    cap_ref = summary.loc[
        summary[schema.raw.cycle_index_txt].isin(normalization_cycles),
        step_txt,
    ]
    if not cap_ref.empty:
        nom_cap = cap_ref.mean()
    else:
        logger.info("Empty reference cycle(s)")
        nom_cap = 1.0  # Default fallback value

    return nom_cap


def equivalent_cycles_to_summary(
    data: Data,
    schema: Optional[Schema] = None,
    nom_cap: float = 1.0,
    normalization_cycles: Union[Sequence, int, None] = None,
    step_txt: Optional[str] = None,
) -> Data:
    """
    Add equivalent cycles column to the summary.

    Args:
        data (Data): The data object.
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        nom_cap (float): The nominal capacity (default: 1.0)
        normalization_cycles (Union[Sequence, int, None]): The cycles for normalization (default: None)
        step_txt (str): The header string for the charge or discharge capacity
            (defaults to the raw charge-capacity header)
    """
    if schema is None:
        schema = default_schema()
    headers_summary = schema.cycle

    if step_txt is None:
        step_txt = schema.raw.charge_capacity_txt

    summary = data.summary

    if normalization_cycles is not None:
        nom_cap = _calculate_nominal_capacity_from_cycles(
            summary, schema, normalization_cycles, step_txt
        )

    normalized_cycle_index_column = {
        headers_summary.normalized_cycle_index: summary[
            headers_summary.cumulated_charge_capacity
        ]
        / nom_cap
    }
    summary = summary.assign(**normalized_cycle_index_column)
    data.summary = summary
    return data


def c_rates_to_summary(
    data: Data,
    schema: Optional[Schema] = None,
    nom_cap: float = 1.0,
    normalization_cycles: Union[Sequence, int, None] = None,
    step_txt: Optional[str] = None,
    current_conversion_factor: float = 1.0,
) -> Data:
    """
    Add c-rates to the summary.

    The current-unit conversion is handled by value: the caller computes the
    factor that converts the raw current unit to the desired output current unit
    and passes it in (default 1.0, i.e. no conversion), so this function does no
    unit handling itself.

    Args:
        data (core.Data): The data object.
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        nom_cap (float): The nominal capacity (default: 1.0)
        normalization_cycles (Union[Sequence, int, None]): The cycles for normalization (default: None)
        step_txt (str): The header string for the charge or discharge capacity
            (defaults to the raw charge-capacity header)
        current_conversion_factor (float): The precomputed factor to convert the
            raw current unit to the output current unit (default: 1.0).
    Returns:
        core.Data: The data object with the c-rates added to the summary.
    """
    if schema is None:
        schema = default_schema()
    headers_summary = schema.cycle
    headers_steps = schema.step

    logger.debug("Extracting C-rates")

    if step_txt is None:
        step_txt = schema.raw.charge_capacity_txt

    summary = data.summary
    steps = data.steps

    if normalization_cycles is not None:
        nom_cap = _calculate_nominal_capacity_from_cycles(
            summary, schema, normalization_cycles, step_txt
        )

    def rate_to_cellpy_units(rate):
        return rate * current_conversion_factor

    charge_steps = steps.loc[
        steps[headers_steps.type] == "charge",
        [headers_steps.cycle, headers_steps.rate_avr],
    ].rename(columns={headers_steps.rate_avr: headers_summary.charge_c_rate})

    charge_steps = charge_steps.drop_duplicates(
        subset=[headers_steps.cycle], keep="first"
    )
    charge_steps[headers_summary.charge_c_rate] = rate_to_cellpy_units(
        charge_steps[headers_summary.charge_c_rate] / nom_cap
    )

    summary = summary.merge(
        charge_steps,
        left_on=headers_summary.cycle_index,
        right_on=headers_steps.cycle,
        how="left",
    ).drop(columns=headers_steps.cycle)

    discharge_steps = steps.loc[
        steps[headers_steps.type] == "discharge",
        [headers_steps.cycle, headers_steps.rate_avr],
    ].rename(columns={headers_steps.rate_avr: headers_summary.discharge_c_rate})

    discharge_steps = discharge_steps.drop_duplicates(
        subset=[headers_steps.cycle], keep="first"
    )
    discharge_steps[headers_summary.discharge_c_rate] = rate_to_cellpy_units(
        discharge_steps[headers_summary.discharge_c_rate] / nom_cap
    )
    summary = summary.merge(
        discharge_steps,
        left_on=headers_summary.cycle_index,
        right_on=headers_steps.cycle,
        how="left",
    ).drop(columns=headers_steps.cycle)
    data.summary = summary
    return data


def ir_to_summary(data: Data, schema: Optional[Schema] = None) -> Data:
    # should check:  test.charge_steps = None,
    # test.discharge_steps = None
    # THIS DOES NOT WORK PROPERLY!!!!
    # Found a file where it writes IR for cycle n on cycle n+1
    # This only picks out the data on the last IR step before
    if schema is None:
        schema = default_schema()
    headers_raw = schema.raw
    headers_summary = schema.cycle

    summary = data.summary
    raw = data.raw

    logger.debug("finding ir")
    only_zeros = summary[headers_raw.discharge_capacity_txt] * 0.0
    discharge_steps = selectors.get_step_numbers(
        data,
        schema,
        steptype="discharge",
        allctypes=False,
    )
    charge_steps = selectors.get_step_numbers(
        data,
        schema,
        steptype="charge",
        allctypes=False,
    )
    ir_indexes = []
    ir_values = []
    ir_values2 = []
    for i in summary.index:
        # selecting the appropriate cycle
        cycle = summary.iloc[i][headers_raw.cycle_index_txt]
        step = discharge_steps[cycle]
        if step[0]:
            ir = raw.loc[
                (raw[headers_raw.cycle_index_txt] == cycle)
                & (data.raw[headers_raw.step_index_txt] == step[0]),
                headers_raw.internal_resistance_txt,
            ]
            # This will not work if there are more than one item in step
            ir = ir.values[0]
        else:
            ir = 0
        step2 = charge_steps[cycle]
        if step2[0]:
            ir2 = raw[
                (raw[headers_raw.cycle_index_txt] == cycle)
                & (data.raw[headers_raw.step_index_txt] == step2[0])
            ][headers_raw.internal_resistance_txt].values[0]
        else:
            ir2 = 0
        ir_indexes.append(i)
        ir_values.append(ir)
        ir_values2.append(ir2)
    ir_frame = only_zeros + ir_values
    ir_frame2 = only_zeros + ir_values2
    summary.insert(0, column=headers_summary.ir_discharge, value=ir_frame)
    summary.insert(0, column=headers_summary.ir_charge, value=ir_frame2)
    data.summary = summary
    return data


def _main():
    print("summarizers.py - no main function yet")


if __name__ == "__main__":
    _main()
