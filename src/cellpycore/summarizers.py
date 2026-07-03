import logging
import types
from dataclasses import asdict
from typing import Optional, Sequence, TypeVar, Union

import polars as pl

from cellpycore.cell_core import Data
from cellpycore.config import ResetGranularity, Schema, TestMode, default_schema
from cellpycore.extractors import LastIRExtractor, SummaryExtractor
from cellpycore.legacy import CellpyLimits, NoDataFound

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
# standalone cellpy-core use. Read-only view so no caller can mutate the
# process-wide defaults (thread-safety); make_step_table builds a fresh dict
# per call when no limits are passed.
DEFAULT_RAW_LIMITS = types.MappingProxyType(asdict(CellpyLimits()))

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
    ("ref_potential", "ref_potential"),
)


def _require_frame(frame, name: str) -> None:
    """Raise ``NoDataFound`` when a required input frame is missing."""
    if frame is None:
        raise NoDataFound(
            f"data.{name} is missing; the engine needs a populated ``{name}`` frame"
        )


def _require_columns(frame: "pl.DataFrame", required: dict, frame_name: str) -> None:
    """Raise ``ValueError`` naming every required column missing from ``frame``.

    Args:
        frame: The (polars) frame to check.
        required: Mapping of schema attribute name -> resolved column name.
        frame_name: Label used in the error message (e.g. ``"raw"``).
    """
    missing = [
        f"'{col}' (schema attribute ``{attr}``)"
        for attr, col in required.items()
        if col not in frame.columns
    ]
    if missing:
        raise ValueError(
            f"data.{frame_name} is missing required column(s): " + ", ".join(missing)
        )


def _ensure_test_id(frame: "pl.DataFrame", test_id_col: str) -> "pl.DataFrame":
    """Return ``frame`` with a ``test_id`` column, defaulting to ``0`` when absent.

    A single unmerged test has no explicit ``test_id``; materializing a constant
    ``0`` keeps the step/cycle tables carrying the key (and the composite group
    keys well-defined) while being behaviour-preserving.
    """
    if test_id_col in frame.columns:
        return frame
    return frame.with_columns(pl.lit(0, dtype=pl.Int64).alias(test_id_col))


def _group_keys(frame: "pl.DataFrame", base_keys: list, test_id_col: str) -> list:
    """Prepend ``test_id`` to ``base_keys`` when ``frame`` carries that column.

    Grouping / joining on the composite ``(test_id, …)`` key isolates cycles and
    steps across merged tests. Frames without a ``test_id`` column (e.g. the
    rebuilt native steps inside the legacy summary bridge) fall back to the base
    keys, reproducing the pre-merge single-test behaviour exactly.
    """
    if test_id_col in frame.columns:
        return [test_id_col, *base_keys]
    return list(base_keys)


# The four cumulative raw columns (per direction) that carry a reset-granularity
# convention. Whichever are present get normalized to cycle-cumulative.
_CUMULATIVE_ATTRS = (
    "cumulative_charge_capacity",
    "cumulative_discharge_capacity",
    "cumulative_charge_energy",
    "cumulative_discharge_energy",
)


def normalize_capacity_granularity(
    data: Data,
    schema: Optional[Schema] = None,
    granularity: ResetGranularity = ResetGranularity.CYCLE,
) -> Data:
    """Normalize cumulative raw capacity / energy columns to cycle-cumulative.

    The engine mandates **cycle-cumulative** raw capacity / energy (reset at each
    cycle boundary; see ``docs/data_format_specifications/harmonized_raw.md``).
    Cyclers that instead deliver **step-cumulative** (reset per step) or
    **test-cumulative** (never reset) raw can be normalized here before
    aggregation. The transform is granularity-agnostic: for each present column,
    the per-row increment within the *source* reset group is reconstructed and
    re-accumulated over ``(test_id, cycle_num)``, which is provably an identity
    for a ``CYCLE`` input.

    Args:
        data (Data): The data object (its ``raw`` frame is rewritten in place).
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        granularity (ResetGranularity): The reset granularity of the source raw.
            ``ResetGranularity.CYCLE`` (the default and mandated convention)
            returns ``data`` untouched.

    Returns:
        Data: The data object with the cumulative columns normalized to
        cycle-cumulative (the same object; ``raw`` matches the input frame's
        type — polars in, polars out; pandas in, pandas out).
    """
    if granularity == ResetGranularity.CYCLE:
        return data

    if schema is None:
        schema = default_schema()
    nhdr = schema.raw

    raw = data.raw
    # The engine is polars-native; accept a pandas frame for convenience and
    # return the same type the caller supplied.
    was_pandas = not isinstance(raw, pl.DataFrame)
    if was_pandas:
        raw = pl.from_pandas(raw)

    raw = _ensure_test_id(raw, nhdr.test_id)
    raw = raw.sort(nhdr.datapoint_num)

    if granularity == ResetGranularity.STEP:
        source_keys = [nhdr.test_id, nhdr.cycle_num, nhdr.step_num]
    else:  # ResetGranularity.TEST
        source_keys = [nhdr.test_id]
    cycle_keys = [nhdr.test_id, nhdr.cycle_num]

    cols = [
        getattr(nhdr, attr)
        for attr in _CUMULATIVE_ATTRS
        if getattr(nhdr, attr) in raw.columns
    ]
    if cols:
        # Two passes (polars disallows a window expr nested inside another
        # window's aggregation): (1) per-row increment within the source reset
        # group (first row of the group keeps its own value), then (2)
        # re-accumulate over the cycle.
        increments = []
        for col in cols:
            diff = pl.col(col) - pl.col(col).shift(1).over(source_keys)
            increments.append(
                pl.when(diff.is_null()).then(pl.col(col)).otherwise(diff).alias(col)
            )
        raw = raw.with_columns(increments)
        raw = raw.with_columns(
            [pl.col(col).cum_sum().over(cycle_keys).alias(col) for col in cols]
        )

    data.raw = raw.to_pandas() if was_pandas else raw
    return data


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

    # Membership test (not ``or``) so an explicit override of 0 / 0.0 wins
    # instead of silently falling back to the default limit.
    orl = override_raw_limits or {}
    current_hard = (
        orl["current_hard"] if "current_hard" in orl else raw_limits["current_hard"]
    )
    stable_current_soft = (
        orl["stable_current_soft"]
        if "stable_current_soft" in orl
        else raw_limits["stable_current_soft"]
    )
    stable_voltage_hard = (
        orl["stable_voltage_hard"]
        if "stable_voltage_hard" in orl
        else raw_limits["stable_voltage_hard"]
    )
    stable_charge_hard = (
        orl["stable_charge_hard"]
        if "stable_charge_hard" in orl
        else raw_limits["stable_charge_hard"]
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
    m_no_change = (v_delta == 0) & (cur_delta == 0) & (ch_delta == 0) & (dch_delta == 0)

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
    raw_limits: Optional[dict] = None,
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
            Defaults to a fresh copy of ``DEFAULT_RAW_LIMITS``.

    Returns:
        core.Data: The data object with the step table added if from_data_point is None,
          otherwise the step table is returned as a DataFrame.

    Raises:
        NoDataFound: If ``data.raw`` is missing.
        ValueError: If the raw frame lacks required columns (datapoint,
            cycle or step numbers).
    """
    if schema is None:
        schema = default_schema()
    if raw_limits is None:
        raw_limits = asdict(CellpyLimits())
    nhdr = schema.raw
    shdr = schema.step

    _require_frame(data.raw, "raw")
    raw = data.raw
    # The engine is polars-native; accept a pandas frame for convenience.
    if not isinstance(raw, pl.DataFrame):
        raw = pl.from_pandas(raw)
    _require_columns(
        raw,
        {
            "datapoint_num": nhdr.datapoint_num,
            "cycle_num": nhdr.cycle_num,
            "step_num": nhdr.step_num,
        },
        "raw",
    )

    # Ensure a per-test key so the step table always carries ``test_id`` and the
    # group key is composite (``0`` for a single unmerged test).
    raw = _ensure_test_id(raw, nhdr.test_id)

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
        "ref_potential": nhdr.ref_potential,
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
        logger.debug(f"omitting steps {skip_steps}")
        raw = raw.filter(~pl.col(nhdr.step_num).is_in(skip_steps))

    by = [nhdr.test_id, nhdr.cycle_num, nhdr.step_num, sub_col]
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
    rename_keys = {
        nhdr.cycle_num: shdr.cycle_num,
        nhdr.step_num: shdr.step_num,
        sub_col: shdr.sub_step_num,
    }
    if nhdr.test_id != shdr.test_id:
        rename_keys[nhdr.test_id] = shdr.test_id
    steps = steps.rename(rename_keys)

    if sort_rows and "test_time_first" in steps.columns:
        logger.debug("sorting the step rows")
        steps = steps.sort("test_time_first")

    if from_data_point is not None:
        return steps
    data.steps = steps
    return data


def _add_end_potentials(summary: "pl.DataFrame", steps: "pl.DataFrame", schema: Schema):
    """Join per-cycle end-of-charge / end-of-discharge potentials onto ``summary``.

    Mirrors legacy ``end_voltage_to_summary``: the last charge/discharge step in
    each cycle (ordered by ``test_time_first``) contributes its ``potential_last``.
    """
    shdr, chdr = schema.step, schema.cycle
    steps_sorted = steps.sort(shdr.test_time_first)

    group_keys = _group_keys(steps, [shdr.cycle_num], shdr.test_id)
    # Join on the per-test key too, but only when the summary also carries it
    # (aligned with the step frame; see ``use_tid`` in ``make_summary``).
    join_on = (
        [chdr.test_id, chdr.cycle_num]
        if shdr.test_id in steps.columns and chdr.test_id in summary.columns
        else [chdr.cycle_num]
    )

    def _end(prefix: str, out_name: str) -> "pl.DataFrame":
        return (
            steps_sorted.filter(pl.col(shdr.step_type).str.starts_with(prefix))
            .group_by(group_keys, maintain_order=True)
            .agg(pl.col(shdr.potential_last).last().alias(out_name))
        )

    discharge_end = _end("discharge", chdr.potential_end_discharge)
    charge_end = _end("charge", chdr.potential_end_charge)
    summary = summary.join(discharge_end, on=join_on, how="left")
    summary = summary.join(charge_end, on=join_on, how="left")
    return summary


def _subtract_excluded_step_deltas(
    summary: "pl.DataFrame",
    steps: "pl.DataFrame",
    schema: Schema,
    exclude_step_types: Sequence[str],
    use_tid: bool,
) -> "pl.DataFrame":
    """Subtract excluded steps' per-cycle capacity deltas from the summary.

    Ports the exclusion math of the removed pandas ``summary_selector_exluder``
    (issue #54): capacities are cycle-cumulative, so removing steps from the
    summary is not row selection — instead each excluded step's contribution
    (``last - first``, summed per cycle) is subtracted from the cycle-end
    charge / discharge capacities, producing a summary "as if" those steps
    never happened. Steps are excluded when their ``step_type`` starts with any
    of the given prefixes (e.g. ``"cv_"`` matches ``cv_charge`` and
    ``cv_discharge``). Cycles without any excluded step get a zero correction.

    Only the capacity columns are corrected: the legacy implementation also
    adjusted the selected raw rows' current / voltage, but those values feed
    nothing that survives in the native summary (end potentials come from the
    step table).
    """
    shdr, chdr = schema.step, schema.cycle

    mask = pl.any_horizontal(
        [pl.col(shdr.step_type).str.starts_with(p) for p in exclude_step_types]
    )
    group_keys = _group_keys(steps, [shdr.cycle_num], shdr.test_id)
    corrections = (
        steps.filter(mask)
        .group_by(group_keys, maintain_order=True)
        .agg(
            (pl.col(shdr.charge_capacity_last) - pl.col(shdr.charge_capacity_first))
            .sum()
            .alias("__excl_charge"),
            (
                pl.col(shdr.discharge_capacity_last)
                - pl.col(shdr.discharge_capacity_first)
            )
            .sum()
            .alias("__excl_discharge"),
        )
    )

    left_on = [chdr.test_id, chdr.cycle_num] if use_tid else [chdr.cycle_num]
    right_on = [shdr.test_id, shdr.cycle_num] if use_tid else [shdr.cycle_num]
    summary = summary.join(corrections, left_on=left_on, right_on=right_on, how="left")
    summary = summary.with_columns(
        (pl.col(chdr.charge_capacity) - pl.col("__excl_charge").fill_null(0.0)).alias(
            chdr.charge_capacity
        ),
        (
            pl.col(chdr.discharge_capacity) - pl.col("__excl_discharge").fill_null(0.0)
        ).alias(chdr.discharge_capacity),
    )
    return summary.drop(["__excl_charge", "__excl_discharge"])


def make_summary(
    data: Data,
    schema: Optional[Schema] = None,
    final_data_points: Optional[Sequence] = None,
    test_mode: TestMode = TestMode.NORMAL,
    exclude_step_types: Optional[Sequence[str]] = None,
) -> Data:
    """Polars-native per-cycle summary (the clean native ``CycleCols`` subset).

    One row per cycle, built from the cycle-end raw values plus the step table.
    Capacities are cycle-cumulative per direction, so the cycle-end raw value is
    the per-cycle total.

    Args:
        data (Data): The data object (needs ``raw`` and ``steps``).
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        final_data_points: Optional explicit cycle-end datapoints (one per cycle);
            computed from the step table when not given.
        test_mode (TestMode): Cell convention. ``TestMode.NORMAL`` (full-/cathode
            cell, charge first) uses ``CE = 100*discharge/charge`` and
            ``coulombic_difference = charge - discharge``. ``TestMode.INVERTED``
            (anode half-cell, discharge first) flips the reference electrode so
            ``CE = 100*charge/discharge`` and ``coulombic_difference =
            discharge - charge`` (mirrors legacy ``cycle_mode == "anode"``).
        exclude_step_types: Optional step-type prefixes to exclude from the
            summary (e.g. ``["cv_"]`` for a non-CV summary). The excluded
            steps' per-cycle capacity deltas are subtracted from the cycle-end
            values before any derived column is computed (see
            ``_subtract_excluded_step_deltas``). ``None`` (the default) leaves
            the summary untouched.

    Returns:
        Data: The data object with the per-cycle ``summary`` added.

    Raises:
        NoDataFound: If ``data.raw`` or ``data.steps`` is missing.
        ValueError: If the raw or step frame lacks required columns.

    Note:
        The legacy-only summary columns (cumulated CE, shifted capacities, RIC)
        are deliberately **not** produced here; the legacy bridge
        (``OldCellpyCellCore``) adds those for cellpy compatibility.
    """
    if schema is None:
        schema = default_schema()
    nhdr, shdr, chdr = schema.raw, schema.step, schema.cycle

    _require_frame(data.raw, "raw")
    _require_frame(data.steps, "steps")
    raw = data.raw
    if not isinstance(raw, pl.DataFrame):
        raw = pl.from_pandas(raw)
    steps = data.steps
    if not isinstance(steps, pl.DataFrame):
        steps = pl.from_pandas(steps)
    _require_columns(
        raw,
        {
            "datapoint_num": nhdr.datapoint_num,
            "cycle_num": nhdr.cycle_num,
            "test_time": nhdr.test_time,
            "cumulative_charge_capacity": nhdr.cumulative_charge_capacity,
            "cumulative_discharge_capacity": nhdr.cumulative_discharge_capacity,
        },
        "raw",
    )
    _require_columns(
        steps,
        {
            "cycle_num": shdr.cycle_num,
            "datapoint_num_last": shdr.datapoint_num_last,
        },
        "steps",
    )

    raw = _ensure_test_id(raw, nhdr.test_id)

    # Use the per-test key only when both the raw and the step frames carry it, so
    # cumulations/joins stay isolated per test. When the step frame lacks it (e.g.
    # the rebuilt native steps in the legacy summary bridge), fall back to
    # cycle-only behaviour, byte-identical to the single-test path.
    use_tid = nhdr.test_id in raw.columns and shdr.test_id in steps.columns

    # cycle-end datapoint per cycle = the last step's last datapoint
    if final_data_points is None:
        finals = (
            steps.sort(shdr.datapoint_num_last)
            .group_by(
                _group_keys(steps, [shdr.cycle_num], shdr.test_id),
                maintain_order=True,
            )
            .agg(pl.col(shdr.datapoint_num_last).last().alias("__fp"))
        )
        final_data_points = finals["__fp"].to_list()

    sort_keys = [nhdr.test_id, nhdr.cycle_num] if use_tid else [nhdr.cycle_num]
    selected = raw.filter(
        pl.col(nhdr.datapoint_num).is_in(list(final_data_points))
    ).sort(sort_keys)

    select_exprs = [
        pl.col(nhdr.cycle_num).alias(chdr.cycle_num),
        pl.col(nhdr.datapoint_num).alias(chdr.datapoint_num_last),
        pl.col(nhdr.test_time).alias(chdr.last_test_time),
        pl.col(nhdr.cumulative_charge_capacity).alias(chdr.charge_capacity),
        pl.col(nhdr.cumulative_discharge_capacity).alias(chdr.discharge_capacity),
    ]
    if use_tid:
        select_exprs.insert(0, pl.col(nhdr.test_id).alias(chdr.test_id))
    summary = selected.select(select_exprs)

    # Correct the cycle-end capacities before deriving CE / losses / cumulated
    # columns, so every downstream column reflects the exclusion (the removed
    # pandas implementation corrected the selected raw rows at the same stage).
    if exclude_step_types:
        summary = _subtract_excluded_step_deltas(
            summary, steps, schema, exclude_step_types, use_tid
        )

    # Per-test cumulations / shifts: window over ``test_id`` so a merged object
    # never carries capacity/CE from one test into the next.
    def _per_test(expr: pl.Expr) -> pl.Expr:
        return expr.over(chdr.test_id) if use_tid else expr

    cc = pl.col(chdr.charge_capacity)
    dc = pl.col(chdr.discharge_capacity)
    # Coulombic efficiency / difference are referenced to the *first* step of the
    # cycle: charge for NORMAL (cathode/full), discharge for INVERTED (anode).
    # Capacity-loss columns are per-direction and mode-independent.
    if test_mode == TestMode.INVERTED:
        coulombic_efficiency = (100.0 * cc / dc).alias(chdr.coulombic_efficiency)
        coulombic_difference = (dc - cc).alias(chdr.coulombic_difference)
    else:
        coulombic_efficiency = (100.0 * dc / cc).alias(chdr.coulombic_efficiency)
        coulombic_difference = (cc - dc).alias(chdr.coulombic_difference)
    summary = summary.with_columns(
        coulombic_efficiency,
        coulombic_difference,
        (_per_test(cc.shift(1)) - cc).alias(chdr.charge_capacity_loss),
        (_per_test(dc.shift(1)) - dc).alias(chdr.discharge_capacity_loss),
    )
    summary = summary.with_columns(
        _per_test(cc.cum_sum()).alias(chdr.test_cumulated_charge_capacity),
        _per_test(dc.cum_sum()).alias(chdr.test_cumulated_discharge_capacity),
        _per_test(pl.col(chdr.coulombic_difference).cum_sum()).alias(
            chdr.test_cumulated_coulombic_difference
        ),
        _per_test(pl.col(chdr.charge_capacity_loss).cum_sum()).alias(
            chdr.test_cumulated_charge_capacity_loss
        ),
        _per_test(pl.col(chdr.discharge_capacity_loss).cum_sum()).alias(
            chdr.test_cumulated_discharge_capacity_loss
        ),
    )

    summary = _add_end_potentials(summary, steps, schema)
    data.summary = summary
    return data


def generate_specific_summary_columns(
    data: Data,
    mode: str,
    specific_columns: Sequence,
    specific_converter: float,
) -> Data:
    """Generate specific (per mass / area / volume) summary columns.

    Polars-native: for each source column ``col`` present in the summary, add a
    ``{col}_{mode}`` column equal to ``specific_converter * col``.

    The unit conversion is handled by value: the caller computes the conversion
    factor (e.g. via the consumer's own pint-based machinery) and passes it in,
    so this function does no unit handling itself.

    Args:
        data (Data): The data object.
        mode (str): The mode of the data (``"gravimetric"``, ``"areal"`` or
            ``"absolute"``).
        specific_columns (Sequence): The columns to generate specific summary
            columns for. Columns missing from the summary are skipped.
        specific_converter (float): The precomputed conversion factor to multiply
            the absolute columns by to obtain the specific (per mode) values.

    Returns:
        Data: The data object with the specific summary columns added to the summary.
    """
    # The engine is polars-native; accept a pandas frame for convenience.
    summary = data.summary
    if not isinstance(summary, pl.DataFrame):
        summary = pl.from_pandas(summary)
    exprs = [
        (specific_converter * pl.col(col)).alias(f"{col}_{mode}")
        for col in specific_columns
        if col in summary.columns
    ]
    data.summary = summary.with_columns(exprs)
    return data


def _calculate_nominal_capacity_from_cycles(
    summary: DataFrame,
    schema: Schema,
    normalization_cycles: Union[Sequence, int],
    step_txt: str,
) -> float:
    """Calculate nominal capacity from specified normalization cycles.

    Polars-native: averages ``step_txt`` over the rows whose cycle number is in
    ``normalization_cycles``.

    Args:
        summary: The summary ``polars.DataFrame`` containing cycle data.
        schema: The column-header schema to use.
        normalization_cycles: The cycles to use for normalization (``int`` or sequence).
        step_txt: The header string for the capacity column to average.

    Returns:
        float: The calculated nominal capacity (``1.0`` if no reference cycle matches).
    """
    logger.info(
        f"Using these cycles for finding the nominal capacity: {normalization_cycles}"
    )
    if not isinstance(normalization_cycles, (list, tuple)):
        normalization_cycles = [normalization_cycles]

    cap_ref = summary.filter(
        pl.col(schema.cycle.cycle_num).is_in(list(normalization_cycles))
    )[step_txt]
    if cap_ref.len() > 0:
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
    """Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary.

    Polars-native: ``normalized_cycle_index = test_cumulated_charge_capacity / nom_cap``.

    Args:
        data (Data): The data object.
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        nom_cap (float): The nominal capacity (default: 1.0).
        normalization_cycles (Union[Sequence, int, None]): The cycles for
            normalization; when given, ``nom_cap`` is derived from them.
        step_txt (str): The summary capacity column used to derive ``nom_cap``
            from ``normalization_cycles`` (defaults to the native cycle
            charge-capacity column).

    Returns:
        Data: The data object with ``normalized_cycle_index`` added to the summary.
    """
    if schema is None:
        schema = default_schema()
    headers_summary = schema.cycle

    if step_txt is None:
        step_txt = headers_summary.charge_capacity

    # The engine is polars-native; accept a pandas frame for convenience.
    summary = data.summary
    if not isinstance(summary, pl.DataFrame):
        summary = pl.from_pandas(summary)

    if normalization_cycles is not None:
        nom_cap = _calculate_nominal_capacity_from_cycles(
            summary, schema, normalization_cycles, step_txt
        )

    data.summary = summary.with_columns(
        (pl.col(headers_summary.test_cumulated_charge_capacity) / nom_cap).alias(
            headers_summary.normalized_cycle_index
        )
    )
    return data


def c_rates_to_summary(
    data: Data,
    schema: Optional[Schema] = None,
    nom_cap: float = 1.0,
    normalization_cycles: Union[Sequence, int, None] = None,
    step_txt: Optional[str] = None,
    current_conversion_factor: float = 1.0,
) -> Data:
    """Add per-cycle charge / discharge C-rates to the summary.

    Polars-native: takes the first charge (resp. discharge) step's per-step
    C-rate (``c_rate``) in each cycle, scales it by ``current_conversion_factor /
    nom_cap``, and joins it onto the summary as ``charge_c_rate`` /
    ``discharge_c_rate``.

    The current-unit conversion is handled by value: the caller computes the
    factor that converts the raw current unit to the desired output current unit
    and passes it in (default 1.0, i.e. no conversion), so this function does no
    unit handling itself.

    Args:
        data (core.Data): The data object (needs ``summary`` and ``steps``).
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        nom_cap (float): The nominal capacity (default: 1.0).
        normalization_cycles (Union[Sequence, int, None]): The cycles for
            normalization; when given, ``nom_cap`` is derived from them.
        step_txt (str): The summary capacity column used to derive ``nom_cap``
            from ``normalization_cycles`` (defaults to the native cycle
            charge-capacity column).
        current_conversion_factor (float): The precomputed factor to convert the
            raw current unit to the output current unit (default: 1.0).

    Returns:
        core.Data: The data object with the C-rates added to the summary.
    """
    if schema is None:
        schema = default_schema()
    headers_summary = schema.cycle
    headers_steps = schema.step

    logger.debug("Extracting C-rates")

    if step_txt is None:
        step_txt = headers_summary.charge_capacity

    # The engine is polars-native; accept pandas frames for convenience.
    summary = data.summary
    if not isinstance(summary, pl.DataFrame):
        summary = pl.from_pandas(summary)
    steps = data.steps
    if not isinstance(steps, pl.DataFrame):
        steps = pl.from_pandas(steps)

    if normalization_cycles is not None:
        nom_cap = _calculate_nominal_capacity_from_cycles(
            summary, schema, normalization_cycles, step_txt
        )

    group_keys = _group_keys(steps, [headers_steps.cycle_num], headers_steps.test_id)
    use_tid = (
        headers_steps.test_id in steps.columns
        and headers_summary.test_id in summary.columns
    )
    left_on = (
        [headers_summary.test_id, headers_summary.cycle_num]
        if use_tid
        else [headers_summary.cycle_num]
    )
    right_on = (
        [headers_steps.test_id, headers_steps.cycle_num]
        if use_tid
        else [headers_steps.cycle_num]
    )

    def _first_rate(step_type: str, out_name: str) -> "pl.DataFrame":
        # First step of the given type per (test, cycle) (mirrors legacy
        # drop_duplicates keep="first" on the step-table row order).
        return (
            steps.filter(pl.col(headers_steps.step_type) == step_type)
            .group_by(group_keys, maintain_order=True)
            .agg(pl.col(headers_steps.c_rate).first().alias(out_name))
            .with_columns(
                (pl.col(out_name) / nom_cap * current_conversion_factor).alias(out_name)
            )
        )

    charge = _first_rate("charge", headers_summary.charge_c_rate)
    discharge = _first_rate("discharge", headers_summary.discharge_c_rate)

    summary = summary.join(charge, left_on=left_on, right_on=right_on, how="left")
    summary = summary.join(discharge, left_on=left_on, right_on=right_on, how="left")
    data.summary = summary
    return data


def ir_to_summary(
    data: Data,
    schema: Optional[Schema] = None,
    ir_extractor: Optional["SummaryExtractor"] = None,
) -> Data:
    """Add per-cycle internal-resistance columns (``ir_charge`` / ``ir_discharge``).

    The per-cycle IR values are produced by a pluggable
    :class:`~cellpycore.extractors.SummaryExtractor`. The default
    :class:`~cellpycore.extractors.LastIRExtractor` reads the internal resistance
    of the last datapoint of each cycle's last charge / discharge step (issue
    #23, fixing the legacy off-by-one attribution). Cycles for which the extractor
    yields no value (for example a cycle with no charge step) get ``NaN``.

    Args:
        data (Data): The data object (needs ``summary``, ``raw`` and ``steps``).
        schema: The column-header schema to use. Defaults to the native
            cellpy-core schema when not provided.
        ir_extractor: The extractor that derives the per-cycle IR columns.
            Defaults to :class:`~cellpycore.extractors.LastIRExtractor`.

    Returns:
        Data: The data object with ``ir_charge`` / ``ir_discharge`` added.
    """
    if schema is None:
        schema = default_schema()
    if ir_extractor is None:
        ir_extractor = LastIRExtractor()
    headers_summary = schema.cycle

    # The engine is polars-native; accept pandas frames for convenience.
    summary = data.summary
    if not isinstance(summary, pl.DataFrame):
        summary = pl.from_pandas(summary)
    raw = data.raw
    if not isinstance(raw, pl.DataFrame):
        raw = pl.from_pandas(raw)
    steps = data.steps
    if not isinstance(steps, pl.DataFrame):
        steps = pl.from_pandas(steps)

    logger.debug("finding ir")

    per_cycle = ir_extractor(raw=raw, steps=steps, summary=summary, schema=schema)

    join_on = (
        [headers_summary.test_id, headers_summary.cycle_num]
        if headers_summary.test_id in per_cycle.columns
        and headers_summary.test_id in summary.columns
        else headers_summary.cycle_num
    )
    summary = summary.join(per_cycle, on=join_on, how="left")
    # Missing IR (e.g. a cycle without a charge/discharge step) stays NaN rather
    # than the legacy 0.0, so "no measurement" is distinguishable from a real 0.
    summary = summary.with_columns(
        pl.col(headers_summary.ir_charge).fill_null(float("nan")),
        pl.col(headers_summary.ir_discharge).fill_null(float("nan")),
    )
    data.summary = summary
    return data


def _main():
    print("summarizers.py - no main function yet")


if __name__ == "__main__":
    _main()
