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
from cellpycore.config import Schema
from cellpycore.legacy import HeadersNormal, HeadersStepTable, HeadersSummary

DATA_DIR = Path(__file__).parent / "data"
ARBIN_RAW = DATA_DIR / "arbin_cc_raw.parquet"
ARBIN_STEPS = DATA_DIR / "arbin_cc_steps_expected.parquet"
ARBIN_SUMMARY = DATA_DIR / "arbin_cc_summary_expected.parquet"
ARBIN_SMALL_RAW = DATA_DIR / "arbin_small_raw.parquet"

# Golden numbers mirrored from cellpy's own suite (tests/test_cell_readers.py),
# verified to be reproduced by cellpy-core's engine on the same raw data.
ARBIN_N_STEPS = 103
ARBIN_N_CYCLES = 18
ARBIN_CYC1_DATA_POINT = 1457


def _legacy_schema() -> Schema:
    return Schema(raw=HeadersNormal(), cycle=HeadersSummary(), step=HeadersStepTable())


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
    not ARBIN_RAW.is_file(),
    reason="vendored parquet fixtures missing (run dev/regenerate_test_data.py)",
)


def test_arbin_step_table_matches_cellpy_goldens():
    """cellpy-core reproduces cellpy's published step/cycle goldens on real data."""
    schema = _legacy_schema()
    steps = _step_table(ARBIN_RAW)

    assert len(steps) == ARBIN_N_STEPS
    assert int(steps[schema.step.cycle].max()) == ARBIN_N_CYCLES

    point_last = f"{schema.step.point}_last"
    cyc1_last = steps.loc[steps[schema.step.cycle] == 1, point_last].max()
    assert int(cyc1_last) == ARBIN_CYC1_DATA_POINT


def test_arbin_step_table_matches_snapshot():
    """Lock the current engine output so the polars rewrite (issue #13) stays faithful.

    Regenerate the snapshot intentionally with ``dev/regenerate_test_data.py`` if
    a change to the step table is expected.
    """
    steps = _step_table(ARBIN_RAW)
    expected = pd.read_parquet(ARBIN_STEPS)
    assert_frame_equal(
        steps,
        expected.reset_index(drop=True),
        check_dtype=False,
    )


def test_arbin_summary_matches_cellpy_goldens():
    """The per-cycle summary has one row per cycle and the expected cyc-1 datapoint."""
    schema = _legacy_schema()
    summary = _summary(ARBIN_RAW)

    assert len(summary) == ARBIN_N_CYCLES
    assert int(summary[schema.raw.data_point_txt].iloc[0]) == ARBIN_CYC1_DATA_POINT


@pytest.mark.skipif(not ARBIN_SUMMARY.is_file(), reason="summary fixture missing")
def test_arbin_summary_matches_snapshot():
    """Lock the current summary output as the regression oracle for the issue #13
    summary-path rewrite.

    This snapshot is cellpy-core's own current (pandas/legacy) summary output;
    cross-library byte-parity with cellpy is addressed separately (Phase 4).
    Regenerate intentionally with ``dev/regenerate_test_data.py`` if a change to
    the summary is expected.
    """
    summary = _summary(ARBIN_RAW)
    expected = pd.read_parquet(ARBIN_SUMMARY)
    assert_frame_equal(
        summary,
        expected.reset_index(drop=True),
        check_dtype=False,
    )


@pytest.mark.skipif(not ARBIN_SMALL_RAW.is_file(), reason="small fixture missing")
def test_small_step_table_runs_on_real_data():
    """Smoke test: a tiny (47-row, 3-step) real raw frame flows through the engine.

    Note: this fixture's ``step 2`` is a degenerate synthetic slice (non-monotonic
    duplicated ``data_point``, mixed current signs, zero capacity-delta), so the
    engine leaves its ``type`` blank. That matches legacy cellpy classification and
    is a fixture artifact, not an engine defect; we only assert the structural
    result here.
    """
    schema = _legacy_schema()
    steps = _step_table(ARBIN_SMALL_RAW)
    assert len(steps) == 3
    assert schema.step.type in steps.columns
    assert int(steps[schema.step.cycle].max()) == 1
