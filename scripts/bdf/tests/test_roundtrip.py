"""Round-trip tests for the BDF prototype (harmonized-raw -> BDF -> back)."""

import polars as pl
import pytest
from cellpy_bdf import bdf_mapping, export_bdf, read_bdf
from cellpy_bdf.export import to_bdf_frame
from polars.testing import assert_frame_equal

from cellpycore.config import RawCols
from cellpycore.testing.mock_data import create_raw_data


@pytest.fixture
def raw_frame() -> pl.DataFrame:
    return create_raw_data()


def _mapped_subset(frame: pl.DataFrame) -> pl.DataFrame:
    mapped = [c for c in bdf_mapping() if c in frame.columns]
    return frame.select(mapped)


@pytest.mark.parametrize("suffix", [".parquet", ".csv"])
def test_roundtrip_preserves_mapped_columns(raw_frame, tmp_path, suffix):
    path = export_bdf(raw_frame, tmp_path / f"bdf_export{suffix}")
    back = read_bdf(path)
    assert_frame_equal(
        back.select(_mapped_subset(raw_frame).columns),
        _mapped_subset(raw_frame),
        check_column_order=False,
    )


def test_roundtrip_with_conversion_factors(raw_frame, tmp_path):
    factors = {"cycle_charging_capacity_ah": 0.001, "current_ampere": 2.0}
    path = export_bdf(
        raw_frame, tmp_path / "bdf_export.parquet", conversion_factors=factors
    )
    raw_cols = RawCols()

    exported = pl.read_parquet(path)
    expected_ah = raw_frame[raw_cols.cumulative_charge_capacity] * 0.001
    assert exported["cycle_charging_capacity_ah"].equals(
        expected_ah.rename("cycle_charging_capacity_ah")
    )

    back = read_bdf(path, conversion_factors=factors)
    assert_frame_equal(
        back.select(_mapped_subset(raw_frame).columns),
        _mapped_subset(raw_frame),
        check_column_order=False,
    )


def test_export_uses_bdf_notations_and_unix_seconds(raw_frame, tmp_path):
    out = to_bdf_frame(raw_frame)
    assert "current_ampere" in out.columns
    assert "voltage_volt" in out.columns
    assert "cycle_count" in out.columns
    # epoch ns -> unix seconds: mock data starts at 2021-01-01T00:00:00 UTC
    assert out["unix_time_second"].dtype == pl.Float64
    assert out["unix_time_second"][0] == 1609459200.0
    # no harmonized-only bookkeeping columns leak into the BDF file
    assert "source_uuid" not in out.columns


def test_export_fails_without_required_columns(raw_frame, tmp_path):
    crippled = raw_frame.drop(RawCols().current)
    with pytest.raises(ValueError, match="current_ampere"):
        export_bdf(crippled, tmp_path / "bdf.parquet")


def test_readback_feeds_from_raw_frame(raw_frame, tmp_path):
    from cellpycore.cell_core import Data

    path = export_bdf(raw_frame, tmp_path / "bdf.parquet")
    back = read_bdf(path)
    data = Data.from_raw_frame(back, validate=False)
    assert data.raw.height == raw_frame.height


def test_unsupported_suffix(raw_frame, tmp_path):
    with pytest.raises(ValueError, match="suffix"):
        export_bdf(raw_frame, tmp_path / "bdf.xlsx")
    with pytest.raises(ValueError, match="suffix"):
        read_bdf(tmp_path / "bdf.xlsx")
