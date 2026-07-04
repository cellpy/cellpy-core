"""Tests for bridge-only legacy pandas selectors (issue #67)."""

from pathlib import Path

import pandas as pd
import pytest

from cellpycore.cell_core import Data, OldCellpyCellCore
from cellpycore.config import legacy_schema
from cellpycore.legacy import HeadersNormal, HeadersStepTable, selectors

DATA_DIR = Path(__file__).parent / "data"
CYCLER_CC_RAW = DATA_DIR / "cycler_cc_raw.parquet"
CYCLER_CC_N_CYCLES = 18

pytestmark_golden = pytest.mark.skipif(
    not CYCLER_CC_RAW.is_file(),
    reason="vendored parquet fixtures missing (run dev/regenerate_test_data.py)",
)


def _minimal_legacy_data() -> tuple[Data, pd.DataFrame]:
    """Tiny legacy-named raw + step tables for unit tests."""
    shdr = HeadersStepTable()
    rhdr = HeadersNormal()
    steptable = pd.DataFrame(
        {
            shdr.cycle: [1, 1, 2, 2],
            shdr.step: [1, 2, 1, 2],
            shdr.type: ["charge", "discharge", "charge", "discharge"],
            shdr.rate_avr: [0.1, 0.1, 0.2, 0.2],
        }
    )
    raw = pd.DataFrame({rhdr.cycle_index_txt: [1, 1, 1, 2, 2, 2]})
    data = Data()
    data.raw = raw
    data.steps = steptable
    return data, steptable


def test_legacy_schema_default_avoids_attribute_error():
    """``schema=None`` must use legacy headers, not native ``default_schema()``."""
    data, steptable = _minimal_legacy_data()

    cycles = selectors.get_cycle_numbers(data, steptable=steptable)
    assert set(cycles) == {1, 2}

    steps = selectors.get_step_numbers(
        data, steptype="charge", cycle_number=1, steptable=steptable
    )
    assert steps == {1: [1]}

    rates = selectors.get_rates(data, steptable=steptable)
    schema = legacy_schema()
    assert set(rates.columns) == {
        schema.step.cycle,
        schema.step.type,
        schema.step.rate_avr,
    }


def test_get_cycle_numbers_from_raw_when_steptable_none():
    data, _ = _minimal_legacy_data()
    cycles = selectors.get_cycle_numbers(data)
    assert set(cycles) == {1, 2}


def test_no_removed_create_selector_functions():
    """The pandas selector pair was removed once cellpy migrated off it (#45)."""
    for name in ("create_selector", "summary_selector_exluder"):
        assert not hasattr(selectors, name), f"selectors.{name} should not exist"


@pytestmark_golden
def test_legacy_selectors_on_golden_step_table():
    """Smoke test on real legacy-shaped step table from the golden fixture."""
    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = pd.read_parquet(CYCLER_CC_RAW)
    core.make_core_step_table(data, nom_cap=1.0)

    cycles = selectors.get_cycle_numbers(data)
    assert len(cycles) == CYCLER_CC_N_CYCLES

    charge_steps = selectors.get_step_numbers(data, steptype="charge", cycle_number=1)
    assert 1 in charge_steps
    assert charge_steps[1] != [0]

    rates = selectors.get_rates(data)
    schema = legacy_schema()
    assert schema.step.rate_avr in rates.columns
