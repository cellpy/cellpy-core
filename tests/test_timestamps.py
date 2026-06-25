"""Unit tests for the canonical timestamp conversion helpers.

cellpy-core stores absolute timestamps as int64 nanoseconds since the Unix epoch,
UTC (see ``cellpycore.timestamps``). These tests pin the scalar and ``polars``
conversion helpers and their round-trip behaviour.
"""

from datetime import datetime, timezone

import polars as pl
import pytest

from cellpycore.timestamps import (
    NS_PER_SECOND,
    datetime_to_epoch_ns,
    datetime_to_epoch_ns_expr,
    epoch_ns_to_datetime,
    epoch_ns_to_seconds,
    epoch_ns_to_seconds_expr,
    seconds_to_epoch_ns,
)

# A representative spread covering the fixture era (2016) through 2026.
SAMPLE_SECONDS = [1_400_000_000.0, 1_470_414_083.0, 1_715_609_528.5, 1_780_000_000.0]


def test_ns_per_second_constant():
    assert NS_PER_SECOND == 1_000_000_000


@pytest.mark.parametrize("seconds", SAMPLE_SECONDS)
def test_seconds_ns_roundtrip(seconds):
    ns = seconds_to_epoch_ns(seconds)
    assert isinstance(ns, int)
    assert epoch_ns_to_seconds(ns) == pytest.approx(seconds, abs=1e-9)


def test_seconds_to_ns_is_exact_for_whole_seconds():
    assert seconds_to_epoch_ns(1_470_414_083.0) == 1_470_414_083 * NS_PER_SECOND


def test_datetime_naive_is_treated_as_utc():
    naive = datetime(2021, 1, 1, 0, 0, 0)
    aware = datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert datetime_to_epoch_ns(naive) == datetime_to_epoch_ns(aware)
    assert datetime_to_epoch_ns(aware) == 1_609_459_200 * NS_PER_SECOND


def test_datetime_roundtrip_microsecond_resolution():
    dt = datetime(2026, 6, 25, 9, 33, 12, 123_456, tzinfo=timezone.utc)
    ns = datetime_to_epoch_ns(dt)
    assert epoch_ns_to_datetime(ns) == dt


def test_epoch_ns_to_datetime_truncates_sub_microsecond():
    base = datetime(2021, 1, 1, tzinfo=timezone.utc)
    ns = datetime_to_epoch_ns(base) + 789  # sub-microsecond remainder
    assert epoch_ns_to_datetime(ns) == base


def test_datetime_expr_to_epoch_ns_matches_scalar():
    dt = datetime(2016, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
    df = pl.DataFrame({"date_time": [dt]})
    out = df.select(datetime_to_epoch_ns_expr("date_time").alias("ns"))
    assert out["ns"].dtype == pl.Int64
    assert out["ns"][0] == datetime_to_epoch_ns(dt)


def test_epoch_ns_to_seconds_expr_matches_scalar():
    ns_values = [seconds_to_epoch_ns(s) for s in SAMPLE_SECONDS]
    df = pl.DataFrame({"ns": pl.Series(ns_values, dtype=pl.Int64)})
    out = df.select(epoch_ns_to_seconds_expr("ns").alias("seconds"))
    assert out["seconds"].dtype == pl.Float64
    assert out["seconds"].to_list() == pytest.approx(SAMPLE_SECONDS)
