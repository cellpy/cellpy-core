"""Regression guard for the harmonized raw fixture.

``tests/data/arbin_cc_harmonized_raw.parquet`` is produced by
``dev/make_harmonized_raw.py`` (it renames the legacy ``arbin_cc_raw.parquet``
into the harmonized schema defined by ``cellpycore.config.RawCols``). These tests
pin that the committed fixture matches the current ``RawCols`` schema and the
known row count, so a drift between the schema and the fixture is caught.
"""

from pathlib import Path

import polars as pl

from cellpycore.config import RawCols
from cellpycore.timestamps import epoch_ns_to_seconds

DATA_DIR = Path(__file__).parent / "data"
HARMONIZED_RAW = DATA_DIR / "arbin_cc_harmonized_raw.parquet"

# Row count of the source Arbin fixture (unchanged by the rename).
EXPECTED_ROWS = 10261


def _rawcols_names() -> set[str]:
    cols = RawCols()
    return {getattr(cols, name) for name in vars(RawCols) if not name.startswith("_")}


def test_harmonized_columns_match_rawcols():
    df = pl.read_parquet(HARMONIZED_RAW)
    assert set(df.columns) == _rawcols_names()


def test_harmonized_row_count_and_key_values():
    df = pl.read_parquet(HARMONIZED_RAW)
    cols = RawCols()
    assert df.height == EXPECTED_ROWS
    # mask defaults to True; source_type is the constant set by the converter.
    assert df[cols.mask].all()
    assert df[cols.source_type].unique().to_list() == ["arbin"]
    # epoch_time_utc must be int64 nanoseconds since the Unix epoch UTC (2016-era
    # source), not null. ~1.47e18 ns; converting back to seconds lands in 2016.
    epoch = df[cols.epoch_time_utc]
    assert epoch.dtype == pl.Int64
    assert epoch.null_count() == 0
    assert epoch.min() > 1_400_000_000 * 1_000_000_000
    # ns -> seconds round-trip places the fixture start in the 2016 era.
    assert 1_400_000_000 < epoch_ns_to_seconds(epoch.min()) < 1_500_000_000
