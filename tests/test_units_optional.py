"""Optional-extra guard tests for the unit boundary (STEP-12, issue #40).

The step/summary engine must import and run with ``pint`` **not** installed; pint is
only needed by the ``cellpycore.units`` conversion helpers (the optional ``units``
extra). These tests simulate pint being absent by blocking its import, then assert:

1. importing ``cellpycore`` and running the step + summary engine still works, and
2. the unit helpers raise a clear ``ModuleNotFoundError`` (naming the ``units`` extra)
   only when actually called.
"""

import importlib
import sys
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"
ARBIN_RAW = DATA_DIR / "arbin_cc_raw.parquet"


class _BlockPint:
    """meta_path finder that makes any ``import pint`` raise ModuleNotFoundError."""

    def find_spec(self, name, path=None, target=None):
        if name == "pint" or name.startswith("pint."):
            raise ModuleNotFoundError("No module named 'pint'")
        return None


@pytest.fixture
def pint_absent(monkeypatch):
    from cellpycore import units

    for mod in list(sys.modules):
        if mod == "pint" or mod.startswith("pint."):
            monkeypatch.delitem(sys.modules, mod, raising=False)
    units._get_unit_registry.cache_clear()

    finder = _BlockPint()
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)
        units._get_unit_registry.cache_clear()


def test_cellpycore_imports_without_pint(pint_absent):
    """Importing the package (and re-importing units) must not require pint."""
    importlib.import_module("cellpycore")
    importlib.import_module("cellpycore.units")
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("pint")


@pytest.mark.skipif(
    not ARBIN_RAW.is_file(),
    reason="vendored parquet fixtures missing (run dev/regenerate_test_data.py)",
)
def test_engine_runs_without_pint(pint_absent):
    """The step + summary engine runs end-to-end with pint blocked."""
    import pandas as pd

    from cellpycore.cell_core import Data, OldCellpyCellCore

    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = pd.read_parquet(ARBIN_RAW)
    core.make_core_step_table(data, nom_cap=1.0)
    core.make_core_summary(data, find_ir=True, find_end_voltage=True)

    assert data.has_steps
    assert data.has_summary


def test_unit_helpers_raise_clear_error_without_pint(pint_absent):
    """Calling the pint-backed helpers raises a clear, extra-naming error."""
    from cellpycore import units

    with pytest.raises(ModuleNotFoundError, match="units"):
        units.Q(1.0, "mAh")

    with pytest.raises(ModuleNotFoundError, match="units"):
        units.get_converter_to_specific(_DummyData(), mode="absolute")


class _DummyData:
    """Carries the attributes the converter would read before hitting pint."""

    def __init__(self):
        from cellpycore.units import CellpyUnits

        self.raw_units = CellpyUnits()
        self.mass = 1.0
        self.active_electrode_area = 1.0
        self.volume = 1.0
