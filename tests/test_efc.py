"""Tests for the Equivalent Full Cycles (EFC) utilities (issue #138).

``throughput_to_raw`` integrates |current|*dt on the raw time-series;
``efc_to_summary`` derives capacity throughput / EFC from the per-cycle
cumulated capacities.
"""

import polars as pl
import pytest

from cellpycore.cell_core import CellpyCellCore, Data
from cellpycore.config import default_schema
from cellpycore.summarizers import efc_to_summary, throughput_to_raw

NOM_CAP = 300.0

schema = default_schema()
RAW = schema.raw
CYC = schema.cycle


def _expected_raw_throughput(raw: pl.DataFrame) -> float:
    """Hand-computed sum(|I| * dt) over the whole frame."""
    current = raw[RAW.current].to_list()
    test_time = raw[RAW.test_time].to_list()
    total = 0.0
    for i in range(1, len(current)):
        dt = max(test_time[i] - test_time[i - 1], 0.0)
        total += abs(current[i]) * dt
    return total


def test_throughput_to_raw(mock_data_with_raw: Data):
    data = throughput_to_raw(mock_data_with_raw, nom_cap_abs=NOM_CAP)
    raw = data.raw

    throughput = raw[CYC.test_cumulated_capacity_throughput]
    efc = raw[CYC.equivalent_full_cycles]

    # Non-decreasing, starting at zero.
    assert throughput[0] == 0.0
    assert (throughput.diff().fill_null(0.0) >= 0.0).all()

    # Rest rows (current == 0) add nothing.
    rest_increment = raw.filter(pl.col(RAW.current) == 0.0)[
        CYC.test_cumulated_capacity_throughput
    ]
    deltas = throughput.diff().fill_null(0.0)
    rest_deltas = raw.with_columns(deltas.alias("_d")).filter(
        pl.col(RAW.current) == 0.0
    )["_d"]
    assert (rest_deltas == 0.0).all()
    assert rest_increment.len() > 0

    # Final value matches the hand-computed integral, EFC is throughput/(2*nom_cap).
    expected = _expected_raw_throughput(raw)
    assert throughput[-1] == pytest.approx(expected)
    assert efc[-1] == pytest.approx(expected / (2.0 * NOM_CAP))


def test_throughput_to_raw_conversion_factor(mock_data_with_raw: Data):
    data = throughput_to_raw(mock_data_with_raw, conversion_factor=2.0)
    doubled = data.raw[CYC.test_cumulated_capacity_throughput][-1]
    assert doubled == pytest.approx(2.0 * _expected_raw_throughput(data.raw))


def test_throughput_to_raw_pandas_round_trip(mock_data_with_raw: Data):
    mock_data_with_raw.raw = mock_data_with_raw.raw.to_pandas()
    data = throughput_to_raw(mock_data_with_raw)
    assert not isinstance(data.raw, pl.DataFrame)
    assert CYC.test_cumulated_capacity_throughput in data.raw.columns
    assert CYC.equivalent_full_cycles in data.raw.columns


def test_efc_to_summary(mock_data_with_raw: Data):
    core = CellpyCellCore()
    data = core.make_core_step_table(mock_data_with_raw)
    data = core.make_core_summary(data)
    data = efc_to_summary(data, nom_cap_abs=NOM_CAP)
    summary = data.summary

    throughput = summary[CYC.test_cumulated_capacity_throughput]
    efc = summary[CYC.equivalent_full_cycles]

    expected = (
        summary[CYC.test_cumulated_charge_capacity]
        + summary[CYC.test_cumulated_discharge_capacity]
    )
    assert throughput.to_list() == pytest.approx(expected.to_list())
    assert efc.to_list() == pytest.approx((expected / (2.0 * NOM_CAP)).to_list())
    assert (throughput.diff().fill_null(0.0) >= 0.0).all()
    assert (efc > 0.0).all()
