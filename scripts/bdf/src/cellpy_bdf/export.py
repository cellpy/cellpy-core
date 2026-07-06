"""Export a harmonized-raw polars frame to a BDF file."""

from pathlib import Path
from typing import Optional, Union

import polars as pl

from cellpy_bdf.mapping import BDF_UNIX_TIME, REQUIRED_BDF_COLUMNS, bdf_mapping
from cellpycore import config
from cellpycore.timestamps import epoch_ns_to_seconds_expr


def to_bdf_frame(
    frame: pl.DataFrame,
    raw_cols: Optional[config.Cols] = None,
    conversion_factors: Optional[dict[str, float]] = None,
) -> pl.DataFrame:
    """Convert a harmonized-raw frame to a BDF-named frame.

    Args:
        frame: A ``polars.DataFrame`` in the harmonized-raw schema.
        raw_cols: The raw column-header schema. Defaults to the native
            ``config.RawCols``.
        conversion_factors: Optional by-value unit-conversion factors keyed by
            **BDF notation** (e.g. ``{"cycle_charging_capacity_ah": 0.001}``
            for mAh raw data). Values are multiplied in on export; missing
            keys default to ``1.0`` (raw data assumed already in BDF units).

    Returns:
        A frame holding only the mapped columns, renamed to BDF notations,
        with ``unix_time_second`` converted from epoch nanoseconds.

    Raises:
        ValueError: If a BDF-required column (current, voltage) is missing.
    """
    mapping = {
        raw: bdf for raw, bdf in bdf_mapping(raw_cols).items() if raw in frame.columns
    }
    missing = [c for c in REQUIRED_BDF_COLUMNS if c not in mapping.values()]
    if missing:
        raise ValueError(f"frame lacks columns for required BDF terms: {missing}")

    out = frame.select(list(mapping)).rename(mapping)
    if BDF_UNIX_TIME in out.columns:
        out = out.with_columns(epoch_ns_to_seconds_expr(BDF_UNIX_TIME))
    if conversion_factors:
        out = out.with_columns(
            pl.col(bdf_name) * factor
            for bdf_name, factor in conversion_factors.items()
            if bdf_name in out.columns
        )
    return out


def export_bdf(
    frame: pl.DataFrame,
    path: Union[str, Path],
    raw_cols: Optional[config.Cols] = None,
    conversion_factors: Optional[dict[str, float]] = None,
) -> Path:
    """Write a harmonized-raw frame to a BDF file (parquet or csv by suffix).

    Args:
        frame: A ``polars.DataFrame`` in the harmonized-raw schema.
        path: Output file path; ``.parquet`` or ``.csv`` decides the format.
        raw_cols: The raw column-header schema. Defaults to the native
            ``config.RawCols``.
        conversion_factors: See :func:`to_bdf_frame`.

    Returns:
        The output path.

    Raises:
        ValueError: On a missing required column or an unsupported suffix.
    """
    path = Path(path)
    out = to_bdf_frame(frame, raw_cols=raw_cols, conversion_factors=conversion_factors)
    if path.suffix == ".parquet":
        out.write_parquet(path)
    elif path.suffix == ".csv":
        out.write_csv(path)
    else:
        raise ValueError(f"unsupported BDF file suffix: {path.suffix!r}")
    return path
