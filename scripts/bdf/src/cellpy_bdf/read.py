"""Read a BDF file back into the harmonized-raw schema."""

from pathlib import Path
from typing import Optional, Union

import polars as pl

from cellpy_bdf.mapping import BDF_UNIX_TIME, bdf_mapping
from cellpycore import config
from cellpycore.timestamps import NS_PER_SECOND


def from_bdf_frame(
    frame: pl.DataFrame,
    raw_cols: Optional[config.Cols] = None,
    conversion_factors: Optional[dict[str, float]] = None,
) -> pl.DataFrame:
    """Convert a BDF-named frame back to harmonized-raw column names.

    Args:
        frame: A ``polars.DataFrame`` with BDF-notation columns.
        raw_cols: The raw column-header schema to rename into. Defaults to
            the native ``config.RawCols``.
        conversion_factors: The same factors passed to export (keyed by BDF
            notation); values are divided out here.

    Returns:
        A frame with the recognized columns renamed to harmonized-raw names
        and the epoch timestamp restored to int64 nanoseconds. Unrecognized
        BDF columns are kept as-is.
    """
    if conversion_factors:
        frame = frame.with_columns(
            pl.col(bdf_name) / factor
            for bdf_name, factor in conversion_factors.items()
            if bdf_name in frame.columns
        )
    if BDF_UNIX_TIME in frame.columns:
        frame = frame.with_columns(
            (pl.col(BDF_UNIX_TIME) * NS_PER_SECOND).round(0).cast(pl.Int64)
        )
    inverse = {
        bdf: raw for raw, bdf in bdf_mapping(raw_cols).items() if bdf in frame.columns
    }
    return frame.rename(inverse)


def read_bdf(
    path: Union[str, Path],
    raw_cols: Optional[config.Cols] = None,
    conversion_factors: Optional[dict[str, float]] = None,
) -> pl.DataFrame:
    """Read a BDF file (parquet or csv by suffix) as a harmonized-raw frame.

    The result is suitable for ``Data.from_raw_frame(..., validate=False)``;
    full validation may require bookkeeping columns (``source_uuid`` etc.)
    that BDF does not carry.

    Args:
        path: Input file path; ``.parquet`` or ``.csv`` decides the format.
        raw_cols: The raw column-header schema to rename into. Defaults to
            the native ``config.RawCols``.
        conversion_factors: See :func:`from_bdf_frame`.

    Returns:
        A ``polars.DataFrame`` with harmonized-raw column names.

    Raises:
        ValueError: On an unsupported suffix.
    """
    path = Path(path)
    if path.suffix == ".parquet":
        frame = pl.read_parquet(path)
    elif path.suffix == ".csv":
        frame = pl.read_csv(path)
    else:
        raise ValueError(f"unsupported BDF file suffix: {path.suffix!r}")
    return from_bdf_frame(
        frame, raw_cols=raw_cols, conversion_factors=conversion_factors
    )
