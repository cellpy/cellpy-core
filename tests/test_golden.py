"""Golden / regression tests on real cycling data vendored as parquet.

The fixtures under ``tests/data/`` are snapshots of cellpy's canonical test
files (see ``tests/data/README.md`` for provenance and regeneration). They give
the pandas->polars engine rewrite (issue #13) a real-data regression oracle and
pin cross-library parity with cellpy's own golden numbers.

cellpy-core is the *core* engine and deliberately does not depend on instrument
loaders, so the raw frames are read straight from parquet (already in the legacy
``HeadersNormal`` column naming the engine currently consumes).
"""

from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from cellpycore.cell_core import Data, OldCellpyCellCore
from cellpycore.config import legacy_schema

DATA_DIR = Path(__file__).parent / "data"
CYCLER_CC_RAW = DATA_DIR / "cycler_cc_raw.parquet"
CYCLER_CC_STEPS = DATA_DIR / "cycler_cc_steps_expected.parquet"
CYCLER_CC_SUMMARY = DATA_DIR / "cycler_cc_summary_expected.parquet"
CYCLER_SMALL_RAW = DATA_DIR / "cycler_small_raw.parquet"
# cellpy's own committed step-type golden (testdata/data/steps.csv), vendored as
# an *independent* cross-library reference: it predates the cellpy->cellpy-core
# engine integration, so matching it proves true cross-repo parity (issue #13
# Phase 4), not a self-snapshot.
CYCLER_CC_STEPTYPES_CELLPY = DATA_DIR / "cycler_cc_steptypes_cellpy.csv"

# Golden numbers mirrored from cellpy's own suite (tests/test_cell_readers.py),
# verified to be reproduced by cellpy-core's engine on the same raw data.
CYCLER_CC_N_STEPS = 103
CYCLER_CC_N_CYCLES = 18
CYCLER_CC_CYC1_DATA_POINT = 1457


def _step_table(raw_path: Path) -> pd.DataFrame:
    # The engine is polars-native; cellpy drives it through the legacy bridge
    # (OldCellpyCellCore), which takes/returns pandas frames in legacy naming.
    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = pd.read_parquet(raw_path)
    result = core.make_core_step_table(data, nom_cap=1.0)
    return result.steps.reset_index(drop=True)


def _summary(raw_path: Path) -> pd.DataFrame:
    # Per-cycle summary, driven through the legacy bridge (pandas/legacy naming).
    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = pd.read_parquet(raw_path)
    core.make_core_step_table(data, nom_cap=1.0)
    core.make_core_summary(data, find_ir=True, find_end_voltage=True)
    return data.summary.reset_index(drop=True)


pytestmark = pytest.mark.skipif(
    not CYCLER_CC_RAW.is_file(),
    reason="vendored parquet fixtures missing (run dev/regenerate_test_data.py)",
)


def test_cycler_cc_step_table_matches_cellpy_goldens():
    """cellpy-core reproduces cellpy's published step/cycle goldens on real data."""
    schema = legacy_schema()
    steps = _step_table(CYCLER_CC_RAW)

    assert len(steps) == CYCLER_CC_N_STEPS
    assert int(steps[schema.step.cycle].max()) == CYCLER_CC_N_CYCLES

    point_last = f"{schema.step.point}_last"
    cyc1_last = steps.loc[steps[schema.step.cycle] == 1, point_last].max()
    assert int(cyc1_last) == CYCLER_CC_CYC1_DATA_POINT


def test_cycler_cc_step_table_matches_snapshot():
    """Lock the current engine output so the polars rewrite (issue #13) stays faithful.

    Regenerate the snapshot intentionally with ``dev/regenerate_test_data.py`` if
    a change to the step table is expected.
    """
    steps = _step_table(CYCLER_CC_RAW)
    expected = pd.read_parquet(CYCLER_CC_STEPS)
    assert_frame_equal(
        steps,
        expected.reset_index(drop=True),
        check_dtype=False,
    )


def test_cycler_cc_summary_matches_cellpy_goldens():
    """The per-cycle summary has one row per cycle and the expected cyc-1 datapoint."""
    schema = legacy_schema()
    summary = _summary(CYCLER_CC_RAW)

    assert len(summary) == CYCLER_CC_N_CYCLES
    assert int(summary[schema.raw.data_point_txt].iloc[0]) == CYCLER_CC_CYC1_DATA_POINT


@pytest.mark.skipif(not CYCLER_CC_SUMMARY.is_file(), reason="summary fixture missing")
def test_cycler_cc_summary_matches_snapshot():
    """Lock the current summary output as the regression oracle for the issue #13
    summary-path rewrite.

    This snapshot is cellpy-core's own current (pandas/legacy) summary output;
    cross-library byte-parity with cellpy is addressed separately (Phase 4).
    Regenerate intentionally with ``dev/regenerate_test_data.py`` if a change to
    the summary is expected.
    """
    summary = _summary(CYCLER_CC_RAW)
    expected = pd.read_parquet(CYCLER_CC_SUMMARY)
    assert_frame_equal(
        summary,
        expected.reset_index(drop=True),
        check_dtype=False,
    )


@pytest.mark.skipif(
    not CYCLER_CC_STEPTYPES_CELLPY.is_file(), reason="cellpy step-type golden missing"
)
def test_cycler_cc_step_types_match_cellpy_reference():
    """Cross-repo parity (Phase 4): cellpy-core reproduces cellpy's own committed
    step-type classification golden (``cellpy/testdata/data/steps.csv``) exactly.

    This golden is an independent reference (cellpy-computed, predating the
    cellpy->cellpy-core engine integration), so a byte-match validates the
    classifier across repositories rather than against a self-snapshot.
    """
    schema = legacy_schema()
    steps = _step_table(CYCLER_CC_RAW)

    reference = pd.read_csv(CYCLER_CC_STEPTYPES_CELLPY, sep=";")
    got = steps[[schema.step.cycle, schema.step.type]].copy()
    got[schema.step.cycle] = got[schema.step.cycle].astype(int)
    got["step"] = steps[schema.step.step].astype(int).to_numpy()
    got = got[[schema.step.cycle, "step", schema.step.type]].reset_index(drop=True)

    expected = reference[["cycle", "step", "type"]].copy()
    expected["cycle"] = expected["cycle"].astype(int)
    expected["step"] = expected["step"].astype(int)
    expected["type"] = expected["type"].fillna("")

    got.columns = ["cycle", "step", "type"]
    got["type"] = got["type"].fillna("")

    assert_frame_equal(
        got.sort_values(["cycle", "step"]).reset_index(drop=True),
        expected.sort_values(["cycle", "step"]).reset_index(drop=True),
    )


def test_step_time_delta_never_negative():
    """Regression guard for the 1.0.3 misclassification bug (obs doc §2.1).

    In cellpy 1.0.3, cycle 9 / step 21 got an empty type and a *negative*
    ``step_time_delta`` (-0.00046 s) because its first/last/delta aggregates were
    taken from wrongly-ordered rows. The polars engine orders correctly, so a
    step's duration can never be negative. Assert that invariant on real data so
    the bug class cannot silently return.
    """
    steps = _step_table(CYCLER_CC_RAW)

    delta_col = "step_time_delta"
    assert delta_col in steps.columns
    deltas = steps[delta_col].dropna()
    negative = deltas[deltas < 0]
    assert negative.empty, f"negative {delta_col} values: {negative.to_list()}"


@pytest.mark.skipif(not CYCLER_SMALL_RAW.is_file(), reason="small fixture missing")
def test_cycler_small_step_table_runs_on_real_data():
    """Smoke test: a tiny real raw frame flows through the engine.

    This fixture is actually a *merged* object holding three ``test_id`` values
    (1, 2, 3), all at ``cycle_index == 1`` with overlapping ``step_index``. With
    the composite ``(test_id, cycle_num, step_num)`` group key (issue #41) the
    steps of the three tests stay isolated instead of collapsing on the shared
    ``(cycle, step)`` pairs: test 1 has 1 step, tests 2 and 3 have 3 steps each,
    so 7 step rows in total. (Before the composite key this incorrectly returned
    3 rows.)
    """
    schema = legacy_schema()
    steps = _step_table(CYCLER_SMALL_RAW)
    assert len(steps) == 7
    assert schema.step.type in steps.columns
    assert int(steps[schema.step.cycle].max()) == 1
