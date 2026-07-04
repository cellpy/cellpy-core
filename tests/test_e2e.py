"""End-to-end tests for the native pipeline through the public API (issue #66).

The legacy bridge already has a real-data regression oracle (test_golden.py);
these tests cover the *native* path a slim consumer (or cellpy v2) uses:
``Data.from_raw_frame`` -> ``make_step_table`` -> ``make_summary`` (plus the
exclude-types and scaled-columns variants), importing everything from the
top-level ``cellpycore`` package only.

Golden numbers are mirrored from cellpy's own suite (see test_golden.py).
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import polars as pl
import pytest

from cellpycore import (
    CellpyCellCore,
    CycleCols,
    Data,
    RawCols,
    Schema,
    StepCols,
    default_schema,
    make_step_table,
    make_summary,
    merge_data,
    update_data,
)

DATA_DIR = Path(__file__).parent / "data"
HARMONIZED_RAW = DATA_DIR / "cycler_cc_harmonized_raw.parquet"

# Golden numbers mirrored from cellpy's own suite (see test_golden.py).
CYCLER_CC_N_STEPS = 103
CYCLER_CC_N_CYCLES = 18
CYCLER_CC_CYC1_DATA_POINT = 1457

pytestmark = pytest.mark.skipif(
    not HARMONIZED_RAW.is_file(),
    reason="vendored harmonized parquet fixture missing",
)


@pytest.fixture(scope="module")
def harmonized_raw() -> pl.DataFrame:
    return pl.read_parquet(HARMONIZED_RAW)


@pytest.fixture
def processed(harmonized_raw) -> Data:
    """Full native pipeline: validating front door -> steps -> summary."""
    return _process_native(harmonized_raw)


def _process_native(raw: pl.DataFrame) -> Data:
    """Run the native public processing pipeline for an in-memory raw frame."""
    data = Data.from_raw_frame(raw)
    make_step_table(data, nom_cap=1.0)
    make_summary(data)
    return data


def _with_test_id(raw: pl.DataFrame, test_id: int) -> pl.DataFrame:
    """Return ``raw`` with a fixture-compatible ``test_id`` value."""
    raw_cols = default_schema().raw
    return raw.with_columns(
        pl.lit(test_id, dtype=raw.schema[raw_cols.test_id]).alias(raw_cols.test_id)
    )


def _assert_update_matches_oracle(updated: Data, oracle: Data) -> None:
    """Assert an incrementally updated object matches a full recompute oracle."""
    schema = default_schema()
    raw_cols, step_cols, cycle_cols = schema.raw, schema.step, schema.cycle

    assert updated.raw.height == oracle.raw.height
    assert updated.steps.height == oracle.steps.height
    assert updated.summary.height == oracle.summary.height

    source = raw_cols.source_datapoint_num
    assert updated.raw[source].min() == oracle.raw[source].min()
    assert updated.raw[source].max() == oracle.raw[source].max()
    assert updated.raw[source].n_unique() == oracle.raw[source].n_unique()

    step_keys = [step_cols.test_id, step_cols.cycle_num, step_cols.step_num]
    assert (
        updated.steps.sort(step_keys)
        .select(step_keys)
        .equals(oracle.steps.sort(step_keys).select(step_keys))
    )

    summary_keys = [cycle_cols.test_id, cycle_cols.cycle_num]
    got_summary = updated.summary.sort(summary_keys)
    expected_summary = oracle.summary.sort(summary_keys)
    assert got_summary.select(summary_keys).equals(
        expected_summary.select(summary_keys)
    )
    for col in (
        cycle_cols.charge_capacity,
        cycle_cols.discharge_capacity,
        cycle_cols.coulombic_efficiency,
    ):
        assert got_summary[col].to_list() == pytest.approx(
            expected_summary[col].to_list(),
            rel=1e-9,
            nan_ok=True,
        )


def test_native_pipeline_matches_golden_counts(processed):
    schema = default_schema()
    assert processed.has_steps and processed.has_summary
    assert processed.steps.height == CYCLER_CC_N_STEPS
    assert processed.summary.height == CYCLER_CC_N_CYCLES

    cyc1 = processed.summary.filter(pl.col(schema.cycle.cycle_num) == 1)
    assert cyc1[schema.cycle.datapoint_num_last].item() == CYCLER_CC_CYC1_DATA_POINT


def test_native_pipeline_step_types_and_capacities(processed):
    schema = default_schema()
    step_types = set(processed.steps[schema.step.step_type].to_list())
    assert {"charge", "discharge"} <= step_types

    # Cycle-end capacities are positive and CE is finite for every *complete*
    # cycle (the final cycle of the fixture is truncated mid-cycle).
    s = processed.summary.filter(pl.col(schema.cycle.cycle_num) < CYCLER_CC_N_CYCLES)
    assert (s[schema.cycle.charge_capacity] > 0).all()
    assert (s[schema.cycle.discharge_capacity] > 0).all()
    assert s[schema.cycle.coulombic_efficiency].is_finite().all()


def test_merge_public_api_real_fixture_two_tests(harmonized_raw, processed):
    """Merging two processed real fixtures preserves both test tracks."""
    schema = default_schema()
    raw_cols, cycle_cols = schema.raw, schema.cycle
    right = _process_native(_with_test_id(harmonized_raw, 2))

    merged = merge_data(processed, right)

    assert merged.raw.height == 2 * harmonized_raw.height
    assert merged.steps.height == 2 * CYCLER_CC_N_STEPS
    assert merged.summary.height == 2 * CYCLER_CC_N_CYCLES
    assert set(merged.raw[raw_cols.test_id].unique().to_list()) == {1, 2}
    assert set(merged.summary[cycle_cols.test_id].unique().to_list()) == {1, 2}

    right_raw = merged.raw.filter(pl.col(raw_cols.test_id) == 2)
    assert right_raw[raw_cols.datapoint_num].min() == (
        processed.raw[raw_cols.datapoint_num].max()
        + right.raw[raw_cols.datapoint_num].min()
    )
    assert right_raw[raw_cols.datapoint_num].max() == (
        processed.raw[raw_cols.datapoint_num].max()
        + right.raw[raw_cols.datapoint_num].max()
    )
    right_cycles = (
        merged.summary.filter(pl.col(cycle_cols.test_id) == 2)[cycle_cols.cycle_num]
        .unique()
        .sort()
        .to_list()
    )
    assert right_cycles == list(
        range(CYCLER_CC_N_CYCLES + 1, 2 * CYCLER_CC_N_CYCLES + 1)
    )


def test_update_public_and_core_real_fixture_matches_full_recompute(
    harmonized_raw, processed
):
    """Updating a real split fixture matches a full public-pipeline recompute."""
    schema = default_schema()
    raw_cols, cycle_cols = schema.raw, schema.cycle
    base_raw = harmonized_raw.filter(pl.col(raw_cols.source_datapoint_num) < 9000)
    extension_raw = harmonized_raw.filter(pl.col(raw_cols.source_datapoint_num) >= 8900)
    base = _process_native(base_raw)

    updated = update_data(base, extension_raw)
    _assert_update_matches_oracle(updated, processed)

    core_updated = CellpyCellCore(initialize=False).update_core_data(
        base, extension_raw
    )
    _assert_update_matches_oracle(core_updated, processed)
    assert cycle_cols.charge_c_rate in core_updated.summary.columns
    assert cycle_cols.ir_charge in core_updated.summary.columns


def test_exclude_step_types_variant(harmonized_raw):
    """Exclusion keeps one row per cycle and subtracts the excluded deltas.

    The Arbin fixture is constant-current (no cv_ steps), so ``cv_`` exclusion
    must be a no-op while excluding the plain ``discharge`` steps must reduce
    the cycle-end discharge capacities.
    """
    schema = default_schema()

    def _summary(exclude):
        data = Data.from_raw_frame(harmonized_raw)
        make_step_table(data, nom_cap=1.0)
        make_summary(data, exclude_step_types=exclude)
        return data.summary

    plain = _summary(None)
    assert plain.height == CYCLER_CC_N_CYCLES

    non_cv = _summary(["cv_"])
    assert non_cv.equals(plain)

    dcap = schema.cycle.discharge_capacity
    no_discharge = _summary(["discharge"])
    assert no_discharge.height == CYCLER_CC_N_CYCLES
    assert (no_discharge[dcap] <= plain[dcap]).all()
    assert no_discharge[dcap].sum() < plain[dcap].sum()


def test_scaled_summary_columns_variant(processed):
    """add_scaled_summary_columns with explicit by-value converters (no pint)."""
    schema = default_schema()
    core = CellpyCellCore(initialize=False)
    core.data = processed

    converters = {"gravimetric": 500.0, "areal": 0.5, "absolute": 1.0}
    result = core.add_scaled_summary_columns(
        processed,
        nom_cap_abs=1.0,
        normalization_cycles=None,
        specific_converters=converters,
    )

    for mode in converters:
        scaled = f"{schema.cycle.charge_capacity}_{mode}"
        assert scaled in result.summary.columns
    grav = result.summary[f"{schema.cycle.charge_capacity}_gravimetric"]
    absolute = result.summary[f"{schema.cycle.charge_capacity}_absolute"]
    assert grav.to_list() == pytest.approx([500.0 * v for v in absolute.to_list()])


# ---------------------------------------------------------------------------
# Edge cases (review item D7)
# ---------------------------------------------------------------------------


def _tiny_raw(records) -> pl.DataFrame:
    return pl.DataFrame(records)


def _records(cycle, step, stype, dp_start, n=5):
    """n datapoints for one step; stype in {'charge', 'discharge'}."""
    cols = RawCols()
    sign = 1.0 if stype == "charge" else -1.0
    return [
        {
            cols.datapoint_num: dp_start + k,
            cols.test_time: float(dp_start + k),
            cols.step_time: float(k),
            cols.step_num: step,
            cols.cycle_num: cycle,
            cols.current: sign * 1.0,
            cols.potential: 3.5 + sign * 0.01 * k,
            cols.cumulative_charge_capacity: 0.1 * (k + 1) if sign > 0 else 0.0,
            cols.cumulative_discharge_capacity: 0.08 * (k + 1) if sign < 0 else 0.0,
            cols.internal_resistance: 0.0,
        }
        for k in range(n)
    ]


def test_empty_raw_frame_is_handled():
    """An empty (zero-row) raw frame yields empty steps, not a crash."""
    cols = RawCols()
    empty = _tiny_raw(_records(1, 1, "charge", 0)).clear()
    data = Data()
    data.raw = empty
    make_step_table(data, nom_cap=1.0)
    assert data.steps.height == 0
    assert cols.cycle_num in empty.columns  # sanity: schema intact


def test_cycle_without_charge_step():
    """A discharge-only cycle still yields a summary row (CE may be non-finite)."""
    schema = default_schema()
    data = Data()
    data.raw = _tiny_raw(_records(1, 1, "discharge", 0))
    make_step_table(data, nom_cap=1.0)
    make_summary(data)

    assert data.summary.height == 1
    assert data.summary[schema.cycle.discharge_capacity].item() > 0
    assert data.summary[schema.cycle.charge_capacity].item() == 0.0


def test_parallel_step_tables_with_two_schemas(harmonized_raw):
    """Thread-safety smoke: two schemas processed in parallel stay independent."""

    def run(marker: str):
        shdr = StepCols()
        shdr.cycle_num = marker
        schema = Schema(raw=RawCols(), cycle=CycleCols(), step=shdr)
        data = Data.from_raw_frame(harmonized_raw)
        make_step_table(data, schema=schema, nom_cap=1.0)
        return data.steps

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_a = pool.submit(run, "CYCLE_A")
        fut_b = pool.submit(run, "CYCLE_B")
        steps_a, steps_b = fut_a.result(), fut_b.result()

    assert "CYCLE_A" in steps_a.columns and "CYCLE_A" not in steps_b.columns
    assert "CYCLE_B" in steps_b.columns and "CYCLE_B" not in steps_a.columns
    assert steps_a.height == steps_b.height == CYCLER_CC_N_STEPS
