# Canonical timestamp representation and conversion helpers

"""Conversion helpers for cellpy-core's canonical absolute-timestamp dtype.

cellpy-core represents **absolute** timestamps (``RawCols.epoch_time_utc`` and the
cycle table's ``first_epoch_time_utc`` / ``last_epoch_time_utc``) as **int64
nanoseconds since the Unix epoch, UTC**. This is exactly the physical representation
used internally by ``polars`` ``Datetime``, ``pandas`` ``datetime64[ns]`` and Arrow
timestamps, so round-trips to those native types are lossless, unlike float epoch
seconds (float64 only has ~0.24 µs resolution near 2026).

This module is deliberately tiny and free of physical-unit machinery: epoch ↔ ns is
dimensionless integer arithmetic, so it lives here rather than in
``cellpycore.units`` (which is pint-based and behind the optional ``units`` extra).

Conventions:
    - The canonical unit is **nanoseconds**, the canonical epoch is the Unix epoch
      (1970-01-01), and the canonical timezone is **UTC**.
    - A *naive* (timezone-less) source timestamp is treated as **UTC**, matching how
      the raw-data converters interpret naive cycler wall-clock timestamps.
    - **Relative** elapsed-time columns (``test_time`` / ``step_time``) are *not*
      absolute timestamps; they remain float **seconds** and are out of scope here.

Note:
    Python ``datetime`` only has microsecond resolution, so ``epoch_ns_to_datetime``
    truncates sub-microsecond nanoseconds. The float-seconds and ns↔ns round-trips
    are exact within int64 range; only the ``datetime`` round-trip is limited to
    microseconds.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import polars as pl

NS_PER_SECOND: int = 1_000_000_000
"""Number of nanoseconds in one second."""

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


def epoch_ns_to_seconds(ns: int) -> float:
    """Convert int64 epoch nanoseconds (UTC) to float epoch seconds (UTC).

    Args:
        ns (int): Nanoseconds since the Unix epoch, UTC.

    Returns:
        float: Seconds since the Unix epoch, UTC. Note that float64 cannot
        represent nanosecond resolution for present-day timestamps, so this is a
        lossy (down-resolution) conversion by design.
    """
    return ns / NS_PER_SECOND


def seconds_to_epoch_ns(seconds: float) -> int:
    """Convert float epoch seconds (UTC) to int64 epoch nanoseconds (UTC).

    Args:
        seconds (float): Seconds since the Unix epoch, UTC.

    Returns:
        int: Nanoseconds since the Unix epoch, UTC (rounded to the nearest ns).
    """
    return round(seconds * NS_PER_SECOND)


def datetime_to_epoch_ns(dt: datetime) -> int:
    """Convert a ``datetime`` to int64 epoch nanoseconds (UTC).

    Args:
        dt (datetime): The timestamp to convert. A naive ``datetime`` (no
            ``tzinfo``) is treated as UTC; an aware ``datetime`` is converted to
            UTC first.

    Returns:
        int: Nanoseconds since the Unix epoch, UTC. Exact to the microsecond
        resolution of ``datetime``.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = dt - _UNIX_EPOCH_UTC
    microseconds = (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
    return microseconds * 1_000


def epoch_ns_to_datetime(ns: int) -> datetime:
    """Convert int64 epoch nanoseconds (UTC) to a timezone-aware UTC ``datetime``.

    Args:
        ns (int): Nanoseconds since the Unix epoch, UTC.

    Returns:
        datetime: A timezone-aware (UTC) ``datetime``. Sub-microsecond
        nanoseconds are truncated (``datetime`` only has microsecond resolution).
    """
    microseconds = ns // 1_000
    return _UNIX_EPOCH_UTC + timedelta(microseconds=microseconds)


def datetime_to_epoch_ns_expr(col: pl.Expr | str) -> pl.Expr:
    """Build a ``polars`` expression converting a ``Datetime`` column to epoch ns.

    Wraps ``polars`` ``dt.epoch("ns")`` so callers (e.g. the raw-data converters)
    do not hard-code the unit string and so the int64-ns convention is centralized.

    Args:
        col (pl.Expr | str): A ``polars`` ``Datetime`` expression, or a column name.

    Returns:
        pl.Expr: An ``Int64`` expression of nanoseconds since the Unix epoch.
    """
    expr = pl.col(col) if isinstance(col, str) else col
    return expr.dt.epoch("ns")


def epoch_ns_to_seconds_expr(col: pl.Expr | str) -> pl.Expr:
    """Build a ``polars`` expression converting epoch ns to float epoch seconds.

    Args:
        col (pl.Expr | str): An ``Int64`` epoch-ns expression, or a column name.

    Returns:
        pl.Expr: A ``Float64`` expression of seconds since the Unix epoch, UTC.
    """
    expr = pl.col(col) if isinstance(col, str) else col
    return expr / NS_PER_SECOND
