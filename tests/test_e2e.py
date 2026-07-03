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
)

DATA_DIR = Path(__file__).parent / "data"
HARMONIZED_RAW = DATA_DIR / "arbin_cc_harmonized_raw.parquet"

# Golden numbers mirrored from cellpy's own suite (see test_golden.py).
ARBIN_N_STEPS = 103
ARBIN_N_CYCLES = 18
ARBIN_CYC1_DATA_POINT = 1457

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
    data = Data.from_raw_frame(harmonized_raw)
    make_step_table(data, nom_cap=1.0)
    make_summary(data)
    return data


def test_native_pipeline_matches_golden_counts(processed):
    schema = default_schema()
    assert processed.has_steps and processed.has_summary
    assert processed.steps.height == ARBIN_N_STEPS
    assert processed.summary.height == ARBIN_N_CYCLES

    cyc1 = processed.summary.filter(pl.col(schema.cycle.cycle_num) == 1)
    assert cyc1[schema.cycle.datapoint_num_last].item() == ARBIN_CYC1_DATA_POINT


def test_native_pipeline_step_types_and_capacities(processed):
    schema = default_schema()
    step_types = set(processed.steps[schema.step.step_type].to_list())
    assert {"charge", "discharge"} <= step_types

    # Cycle-end capacities are positive and CE is finite for every *complete*
    # cycle (the final cycle of the fixture is truncated mid-cycle).
    s = processed.summary.filter(pl.col(schema.cycle.cycle_num) < ARBIN_N_CYCLES)
    assert (s[schema.cycle.charge_capacity] > 0).all()
    assert (s[schema.cycle.discharge_capacity] > 0).all()
    assert s[schema.cycle.coulombic_efficiency].is_finite().all()


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
    assert plain.height == ARBIN_N_CYCLES

    non_cv = _summary(["cv_"])
    assert non_cv.equals(plain)

    dcap = schema.cycle.discharge_capacity
    no_discharge = _summary(["discharge"])
    assert no_discharge.height == ARBIN_N_CYCLES
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
    assert steps_a.height == steps_b.height == ARBIN_N_STEPS
