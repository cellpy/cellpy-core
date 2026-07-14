"""Parity tests for ``cellpycore.curves`` against the cellpy curve goldens.

The oracle is the Stage-0 curve-snapshot suite from cellpy (jepegit/cellpy#433):
the parquet frames under ``tests/data/curve_goldens/`` are vendored verbatim
from ``cellpy/tests/data/goldens/curve_*/curve.parquet`` (same golden cell as
the step/summary goldens: ``20160805_test001_45_cc``, mass = 1.0 mg,
gravimetric conversion). Regenerate on the cellpy side
(``dev/regenerate_goldens.py`` there), then re-vendor — never edit by hand.

The native pipeline here is: harmonized raw fixture → ``Data.from_raw_frame``
→ ``make_step_table`` → ``cellpycore.curves``. Column names are native
(``CurveCols`` / ``OcvCurveCols``); the comparison maps them onto the golden
legacy names, which is the documented intentional difference.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
import pytest

from cellpycore import Data, curves, make_step_table
from cellpycore.config import TestMode as CoreTestMode  # alias: pytest must not collect
from cellpycore.exceptions import NoDataFound

pytest.importorskip("pint")
from cellpycore.units import CellpyUnits, get_converter_to_specific  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"
HARMONIZED_RAW = DATA_DIR / "cycler_cc_harmonized_raw.parquet"
GOLDEN_DIR = DATA_DIR / "curve_goldens"

pytestmark = pytest.mark.skipif(
    not HARMONIZED_RAW.is_file(),
    reason="vendored parquet fixtures missing (run dev/regenerate_test_data.py)",
)

# The goldens were produced with mass=1.0 (mg), gravimetric mode, Arbin raw
# units (charge in Ah) — the same converter cellpy computed.
ARBIN_RAW_UNITS = CellpyUnits(charge="Ah", current="A", mass="g", voltage="V")

# native -> golden (legacy) column names
CAP_RENAMES = {
    "potential": "voltage",
    "cycle_num": "cycle",
    "capacity": "capacity",
    "direction": "direction",
}
OCV_RENAMES = {
    "cycle_num": "cycle_index",
    "step_num": "step_index",
    "step_time": "step_time",
    "potential": "voltage",
}


@pytest.fixture(scope="module")
def native_data():
    data = Data.from_raw_frame(pl.read_parquet(HARMONIZED_RAW))
    make_step_table(data)
    return data


@pytest.fixture(scope="module")
def converter():
    return get_converter_to_specific(
        mass=1.0, from_units=ARBIN_RAW_UNITS, mode="gravimetric"
    )


def _golden(suite: str) -> pd.DataFrame:
    return pd.read_parquet(GOLDEN_DIR / f"{suite}.parquet")


def _prepare(frame: pd.DataFrame) -> pd.DataFrame:
    """Mirror cellpy's prepare_curve_for_golden: sorted columns, floats."""
    out = frame.copy().reset_index(drop=True)
    for col in out.columns:
        if col in ("cycle_index", "step_index"):
            continue
        if pd.api.types.is_timedelta64_dtype(out[col]):
            out[col] = out[col].dt.total_seconds()
        elif pd.api.types.is_integer_dtype(out[col]):
            out[col] = out[col].astype("float64")
    return out[sorted(out.columns)]


def _assert_parity(native: pl.DataFrame, golden: pd.DataFrame, renames: dict):
    actual = native.to_pandas().rename(columns=renames)
    actual = _prepare(actual)
    expected = _prepare(golden)
    assert list(actual.columns) == list(expected.columns)
    assert len(actual) == len(expected)
    for col in actual.columns:
        np.testing.assert_allclose(
            actual[col].to_numpy(dtype=np.float64),
            expected[col].to_numpy(dtype=np.float64),
            rtol=1e-9,
            atol=1e-12,
            equal_nan=True,
            err_msg=col,
        )


def test_converter_matches_golden_setup(converter):
    # (1 Ah)/(mAh/g)/(1 mg) == 1e6 — the factor the cellpy goldens embody
    assert converter == pytest.approx(1_000_000.0)


def test_get_cap_back_and_forth_c1(native_data, converter):
    frame = curves.get_cap_curve(
        native_data,
        cycle=1,
        method="back-and-forth",
        converter=converter,
        test_mode=CoreTestMode.INVERTED,
    )
    _assert_parity(frame, _golden("curve_get_cap_back_and_forth_c1"), CAP_RENAMES)


def test_get_cap_forth_labeled_c1(native_data, converter):
    frame = curves.get_cap_curve(
        native_data,
        cycle=1,
        method="forth-and-forth",
        categorical_column=True,
        label_cycle_number=True,
        insert_nan=False,
        converter=converter,
        test_mode=CoreTestMode.INVERTED,
    )
    _assert_parity(frame, _golden("curve_get_cap_forth_labeled_c1"), CAP_RENAMES)


def test_get_cap_forth_interpolated_c1(native_data, converter):
    frame = curves.get_cap_curve(
        native_data,
        cycle=1,
        method="forth",
        interpolated=True,
        number_of_points=100,
        converter=converter,
        test_mode=CoreTestMode.INVERTED,
    )
    _assert_parity(frame, _golden("curve_get_cap_forth_interpolated_c1"), CAP_RENAMES)


def test_get_cap_forth_c12(native_data, converter):
    frame = curves.get_cap_curve(
        native_data,
        cycles=[1, 2],
        method="forth",
        label_cycle_number=True,
        insert_nan=False,
        converter=converter,
        test_mode=CoreTestMode.INVERTED,
    )
    _assert_parity(frame, _golden("curve_get_cap_forth_c12"), CAP_RENAMES)


def test_get_ccap_c5(native_data, converter):
    frame = curves.get_charge_curve(native_data, cycle=5, converter=converter)
    golden = _golden("curve_get_ccap_c5")
    _assert_parity(
        frame,
        golden,
        {"potential": "voltage", "capacity": "charge_capacity"},
    )


def test_get_dcap_c5(native_data, converter):
    frame = curves.get_discharge_curve(native_data, cycle=5, converter=converter)
    _assert_parity(
        frame,
        _golden("curve_get_dcap_c5"),
        {"potential": "voltage", "capacity": "discharge_capacity"},
    )


def test_get_ocv_up_c1(native_data):
    frame = curves.get_ocv_curve(native_data, cycles=1, direction="up")
    _assert_parity(frame, _golden("curve_get_ocv_up_c1"), OCV_RENAMES)


def test_get_ccap_null_cycle_raises(native_data, converter):
    with pytest.raises(NoDataFound):
        curves.get_charge_curve(native_data, cycle=999, converter=converter)


def test_get_dcap_null_cycle_raises(native_data, converter):
    with pytest.raises(NoDataFound):
        curves.get_discharge_curve(native_data, cycle=999, converter=converter)


# --- behavioral extras (not covered by the golden matrix) ---------------------
def test_select_step_numbers_placeholder_for_missing_cycle(native_data):
    numbers = curves.select_step_numbers(
        native_data.steps, step_type="charge", cycles=[999]
    )
    assert numbers == {999: [0]}


def test_get_cap_curve_empty_when_no_cycles_match(native_data, converter):
    frame = curves.get_cap_curve(
        native_data, cycles=[999], converter=converter, test_mode=CoreTestMode.INVERTED
    )
    assert frame.height == 0
    assert frame.columns == ["potential", "capacity"]


def test_get_cap_capacity_then_voltage_reorders(native_data, converter):
    frame = curves.get_cap_curve(
        native_data,
        cycle=1,
        capacity_then_voltage=True,
        converter=converter,
        test_mode=CoreTestMode.INVERTED,
    )
    assert frame.columns[:2] == ["capacity", "potential"]
