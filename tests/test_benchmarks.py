"""Opt-in performance benchmarks for the core engine (issue #66).

Excluded from the default test run (``-m "not benchmark"`` in addopts); run
them explicitly with::

    uv run pytest -m benchmark

pytest-benchmark prints min/mean/stddev per benchmark and can compare runs
(``--benchmark-autosave`` + ``--benchmark-compare``). There is deliberately no
hard timing assertion: CI-gated thresholds are flaky, so these benchmarks are
a repeatable measure, not a pass/fail gate.
"""

from pathlib import Path

import polars as pl
import pytest

from cellpycore import Data, make_step_table, make_summary

DATA_DIR = Path(__file__).parent / "data"
HARMONIZED_RAW = DATA_DIR / "cycler_cc_harmonized_raw.parquet"

pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.skipif(
        not HARMONIZED_RAW.is_file(),
        reason="vendored harmonized parquet fixture missing",
    ),
]


@pytest.fixture(scope="module")
def harmonized_raw() -> pl.DataFrame:
    return pl.read_parquet(HARMONIZED_RAW)


@pytest.fixture(scope="module")
def large_raw(harmonized_raw) -> pl.DataFrame:
    """~40x the cycler fixture (~410k rows): shifts cycle numbers and datapoints
    so the copies stack into one long continuous test."""
    n_copies = 40
    n_cycles = harmonized_raw["cycle_num"].max()
    n_rows = harmonized_raw.height
    parts = [
        harmonized_raw.with_columns(
            (pl.col("cycle_num") + i * n_cycles),
            (pl.col("datapoint_num") + i * n_rows),
        )
        for i in range(n_copies)
    ]
    return pl.concat(parts)


def _steps(raw: pl.DataFrame) -> Data:
    data = Data.from_raw_frame(raw, validate=False)
    make_step_table(data)
    return data


def test_benchmark_make_step_table(benchmark, harmonized_raw):
    result = benchmark(_steps, harmonized_raw)
    assert result.has_steps


def test_benchmark_make_summary(benchmark, harmonized_raw):
    processed = _steps(harmonized_raw)

    def run():
        return make_summary(processed)

    result = benchmark(run)
    assert result.has_summary


def test_benchmark_full_pipeline_large(benchmark, large_raw):
    def run():
        data = _steps(large_raw)
        return make_summary(data)

    result = benchmark(run)
    assert result.has_summary
