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

from cellpycore import summarizers
from cellpycore.cell_core import Data
from cellpycore.config import Schema
from cellpycore.legacy import HeadersNormal, HeadersStepTable, HeadersSummary

DATA_DIR = Path(__file__).parent / "data"
ARBIN_RAW = DATA_DIR / "arbin_cc_raw.parquet"
ARBIN_STEPS = DATA_DIR / "arbin_cc_steps_expected.parquet"
ARBIN_SMALL_RAW = DATA_DIR / "arbin_small_raw.parquet"

# Golden numbers mirrored from cellpy's own suite (tests/test_cell_readers.py),
# verified to be reproduced by cellpy-core's engine on the same raw data.
ARBIN_N_STEPS = 103
ARBIN_N_CYCLES = 18
ARBIN_CYC1_DATA_POINT = 1457


def _legacy_schema() -> Schema:
    return Schema(raw=HeadersNormal(), cycle=HeadersSummary(), step=HeadersStepTable())


def _step_table(raw_path: Path) -> pd.DataFrame:
    data = Data()
    data.raw = pd.read_parquet(raw_path)
    result = summarizers.make_step_table(data, schema=_legacy_schema(), nom_cap=1.0)
    return result.steps.reset_index(drop=True)


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


@pytest.mark.skipif(not ARBIN_SMALL_RAW.is_file(), reason="small fixture missing")
def test_small_step_table_runs_on_real_data():
    """Smoke test: a tiny (47-row, 3-step) real raw frame flows through the engine.

    Note: on this tiny frame the engine currently leaves one step's ``type`` blank
    (an edge case to revisit during the issue #13 rewrite); we only assert the
    structural result here.
    """
    schema = _legacy_schema()
    steps = _step_table(ARBIN_SMALL_RAW)
    assert len(steps) == 3
    assert schema.step.type in steps.columns
    assert int(steps[schema.step.cycle].max()) == 1
