import logging
from dataclasses import asdict
from typing import Optional, Sequence, TypeVar, Union

import polars as pl

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


# Per-step aggregate statistics produced for every raw signal column. The
# arithmetic mean is named ``mean`` natively (the legacy bridge renames it to
# ``avr``). ``delta`` is computed separately (it needs first + last).
_STATS = ("mean", "std", "min", "max", "first", "last")

# Mapping of native raw signal columns -> native step-table base name. The
# cumulative (per-cycle) capacities/energies become the step-table capacity
# aggregates; per-step capacity is the in-step ``delta``.
_SIGNAL_BASES = (
    ("datapoint_num", "datapoint_num"),
    ("test_time", "test_time"),
    ("step_time", "step_time"),
    ("current", "current"),
    ("potential", "potential"),
    ("cumulative_charge_capacity", "charge_capacity"),
    ("cumulative_discharge_capacity", "discharge_capacity"),
    ("internal_resistance", "internal_resistance"),
)


def _delta_expr(base: str) -> pl.Expr:
    """Per-step delta in percent (mirrors legacy cellpy's ``delta``).

    ``100 * last`` when the step starts at zero, else
    ``100 * (last - first) / abs(first)``.
    """
    first = pl.col(f"{base}_first")
    last = pl.col(f"{base}_last")
    return (
        pl.when(first == 0.0)
        .then(100.0 * last)
        .otherwise(100.0 * (last - first) / first.abs())
        .alias(f"{base}_delta")
    )


def _classify_from_specifications(step_specifications, short: bool, nhdr) -> pl.Expr:
    """Build a step-type expression from explicit step specifications."""
    expr = pl.lit("")
    for row in step_specifications.itertuples():
        if short:
            mask = pl.col(nhdr.step_num) == row.step
        else:
            mask = (pl.col(nhdr.step_num) == row.step) & (
                pl.col(nhdr.cycle_num) == row.cycle
            )
        expr = pl.when(mask).then(pl.lit(row.type)).otherwise(expr)
    return expr


def _classify_steps(
    bases: set,
    step_specifications,
    short: bool,
    override_step_types: Optional[dict],
    override_raw_limits: Optional[dict],
    raw_limits: dict,
    nhdr,
) -> pl.Expr:
    """Return a polars expression classifying each step into a step type.

    Mirrors legacy cellpy's threshold logic; later rules win (so e.g. ``ir``
    overrides ``rest``). Returns ``""`` for steps that match no rule.
    """
    if step_specifications is not None:
        return _classify_from_specifications(step_specifications, short, nhdr)

    # Need the current/potential/capacity aggregates to classify; if the raw
    # frame lacks them, leave every step uncategorized.
    required = {"current", "potential", "charge_capacity", "discharge_capacity"}
    if not required <= bases:
        return pl.lit("")

    orl = override_raw_limits or {}
    current_hard = orl.get("current_hard") or raw_limits["current_hard"]
    stable_current_soft = (
        orl.get("stable_current_soft") or raw_limits["stable_current_soft"]
    )
    stable_voltage_hard = (
        orl.get("stable_voltage_hard") or raw_limits["stable_voltage_hard"]
    )
    stable_charge_hard = (
        orl.get("stable_charge_hard") or raw_limits["stable_charge_hard"]
    )

    cur_mean = pl.col("current_mean")
    cur_min = pl.col("current_min")
    cur_max = pl.col("current_max")
    cur_delta = pl.col("current_delta")
    v_delta = pl.col("potential_delta")
    ch_delta = pl.col("charge_capacity_delta")
    dch_delta = pl.col("discharge_capacity_delta")

    m_no_cur = (cur_max.abs() + cur_min.abs()) < current_hard / 2
    m_v_down = v_delta < -stable_voltage_hard
    m_v_up = v_delta > stable_voltage_hard
    m_v_stable = v_delta.abs() < stable_voltage_hard
    m_cur_down = cur_delta < -stable_current_soft
    m_cur_neg = cur_mean < -current_hard
    m_cur_pos = cur_mean > current_hard
    m_ch_changed = ch_delta.abs() > stable_charge_hard
    m_dch_changed = dch_delta.abs() > stable_charge_hard
    m_no_change = (
        (v_delta == 0) & (cur_delta == 0) & (ch_delta == 0) & (dch_delta == 0)
    )

    # Order matters: later rules override earlier ones (matches legacy cellpy).
    rules = [
        (m_no_cur & m_v_stable, "rest"),
        (m_no_cur & m_v_up, "ocvrlx_up"),
        (m_no_cur & m_v_down, "ocvrlx_down"),
        (m_dch_changed & m_cur_neg, "discharge"),
        (m_ch_changed & m_cur_pos, "charge"),
        (m_v_stable & m_cur_neg & m_cur_down, "cv_discharge"),
        (m_v_stable & m_cur_pos & m_cur_down, "cv_charge"),
        (m_no_change, "ir"),
    ]
    expr = pl.lit("")
    for mask, label in rules:
        expr = pl.when(mask).then(pl.lit(label)).otherwise(expr)

    if override_step_types:
        for step_no, stype in override_step_types.items():
            expr = (
                pl.when(pl.col(nhdr.step_num) == step_no)
                .then(pl.lit(stype))
                .otherwise(expr)
            )
    return expr


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

    raw = data.raw
    # The engine is polars-native; accept a pandas frame for convenience.
    if not isinstance(raw, pl.DataFrame):
        raw = pl.from_pandas(raw)

    if from_data_point is not None:
        raw = raw.filter(pl.col(nhdr.datapoint_num) >= from_data_point)

    # Sort by datapoint so per-step first()/last() are well-defined.
    raw = raw.sort(nhdr.datapoint_num)

    # Resolve which native raw signals are present (mapping each to its
    # step-table base name). Cumulative capacities/energies feed the capacity
    # aggregates; the per-step capacity is the in-step ``delta``.
    raw_for_base = {
        "datapoint_num": nhdr.datapoint_num,
        "test_time": nhdr.test_time,
        "step_time": nhdr.step_time,
        "current": nhdr.current,
        "potential": nhdr.potential,
        "cumulative_charge_capacity": nhdr.cumulative_charge_capacity,
        "cumulative_discharge_capacity": nhdr.cumulative_discharge_capacity,
        "internal_resistance": nhdr.internal_resistance,
    }
    signals = [
        (raw_for_base[raw_attr], base)
        for raw_attr, base in _SIGNAL_BASES
        if raw_for_base[raw_attr] in raw.columns
    ]

    # sub-step is a constant 1 for now (real sub-step support comes later).
    sub_col = nhdr.step_num + "__sub"
    raw = raw.with_columns(pl.lit(1).alias(sub_col))

    if skip_steps is not None:
        logging.debug(f"omitting steps {skip_steps}")
        raw = raw.filter(~pl.col(nhdr.step_num).is_in(skip_steps))

    by = [nhdr.cycle_num, nhdr.step_num, sub_col]
    if usteps:
        raw = raw.with_columns(
            (pl.col(nhdr.step_num).diff().fill_null(1) != 0)
            .cast(pl.Int64)
            .cum_sum()
            .alias("ustep")
        )
        by = by + ["ustep"]

    agg_exprs = []
    for col, base in signals:
        for stat in _STATS:
            agg_exprs.append(getattr(pl.col(col), stat)().alias(f"{base}_{stat}"))

    steps = raw.group_by(by, maintain_order=True).agg(agg_exprs)
    steps = steps.with_columns([_delta_expr(base) for _, base in signals])
    # Mirror pandas groupby key ordering (ascending) for stable row positions.
    steps = steps.sort(by)

    # Per-step C-rate (legacy ``rate_avr`` = abs(current_avr / nom_cap)); the
    # nominal capacity is supplied by the caller (by value).
    if add_c_rate:
        _nom_cap = nom_cap if nom_cap is not None else 1.0
        steps = steps.with_columns(
            (pl.col("current_mean") / _nom_cap)
            .round(DIGITS_C_RATE)
            .abs()
            .alias(shdr.c_rate)
        )

    bases = {base for _, base in signals}
    step_type = _classify_steps(
        bases,
        step_specifications,
        short,
        override_step_types,
        override_raw_limits,
        raw_limits,
        nhdr,
    )
    steps = steps.with_columns(
        step_type.alias(shdr.step_type),
        pl.lit(None, dtype=pl.Utf8).alias(shdr.sub_step_type),
        pl.lit("").alias("info"),
    )

    n_uncategorized = steps.filter(pl.col(shdr.step_type) == "").height
    if n_uncategorized:
        logger.warning(
            f"found {n_uncategorized}:{steps.height} non-categorized steps "
            "(please, check your raw-limits)"
        )

    # Rename group-key columns to the (native) step schema names.
    steps = steps.rename(
        {
            nhdr.cycle_num: shdr.cycle_num,
            nhdr.step_num: shdr.step_num,
            sub_col: shdr.sub_step_num,
        }
    )

    if sort_rows and "test_time_first" in steps.columns:
        logger.debug("sorting the step rows")
        steps = steps.sort("test_time_first")

    if from_data_point is not None:
        return steps
    data.steps = steps
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
