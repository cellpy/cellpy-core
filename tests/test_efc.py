"""Tests for the Equivalent Full Cycles (EFC) utilities (issue #138).

``throughput_to_raw`` integrates |current|*dt on the raw time-series;
``efc_to_summary`` derives capacity throughput / EFC from the per-cycle
cumulated capacities.
"""

import polars as pl
import pytest

from cellpycore.cell_core import CellpyCellCore, Data, OldCellpyCellCore
from cellpycore.config import default_schema
from cellpycore.summarizers import efc_to_summary, throughput_to_raw
from cellpycore.testing.mock_data import create_raw_data

NOM_CAP = 300.0

schema = default_schema()
RAW = schema.raw
CYC = schema.cycle


def _expected_raw_throughput(raw: pl.DataFrame) -> float:
    """Hand-computed trapezoidal sum(|I| * dt) over the whole frame."""
    current = raw[RAW.current].to_list()
    test_time = raw[RAW.test_time].to_list()
    total = 0.0
    for i in range(1, len(current)):
        dt = max(test_time[i] - test_time[i - 1], 0.0)
        total += (abs(current[i]) + abs(current[i - 1])) / 2.0 * dt
    return total


def _data(current, test_time) -> Data:
    data = Data()
    data.raw = pl.DataFrame({RAW.current: current, RAW.test_time: test_time})
    return data


def test_throughput_to_raw_analytic():
    """1 A held for 3600 s is exactly 1 Ah of throughput, i.e. 0.5 EFC at 1 Ah."""
    data = throughput_to_raw(
        _data([1.0, 1.0], [0.0, 3600.0]),
        nom_cap_abs=1.0,
        conversion_factor=1.0 / 3600.0,  # A*s -> Ah
    )
    assert data.raw[CYC.test_cumulated_capacity_throughput][-1] == pytest.approx(1.0)
    assert data.raw[CYC.equivalent_full_cycles][-1] == pytest.approx(0.5)


def test_throughput_to_raw_is_trapezoidal():
    """A rest followed by a pulse must not charge the rest to the pulse current.

    The interval 0->100 s is at rest; only the 100->200 s ramp counts, and it
    counts as the mean of its endpoints (0.5 A * 100 s), not the right-hand
    value (1 A * 100 s).
    """
    data = throughput_to_raw(_data([0.0, 0.0, 1.0], [0.0, 100.0, 200.0]))
    assert data.raw[CYC.test_cumulated_capacity_throughput].to_list() == pytest.approx(
        [0.0, 0.0, 50.0]
    )


def test_throughput_to_raw_flags_bad_input(caplog):
    """Missing current and backwards time are counted as zero, but not silently."""
    data = throughput_to_raw(_data([1.0, None, 1.0, 1.0], [0.0, 1.0, 2.0, 1.5]))
    assert "missing current" in caplog.text
    assert "negative time delta" in caplog.text
    # Monotonic despite the backwards step (that interval contributes nothing).
    throughput = data.raw[CYC.test_cumulated_capacity_throughput]
    assert (throughput.diff().fill_null(0.0) >= 0.0).all()


def test_throughput_to_raw_windows_per_test():
    """With a test_id column the integral cumulates per test, not window-in-window.

    (Regression: nesting cum_sum().over() around a shift().over() raised
    ``window expression not allowed in aggregation``.)
    """
    data = Data()
    data.raw = pl.DataFrame(
        {
            RAW.test_id: [0, 0, 0, 1, 1, 1],
            RAW.current: [1.0, 1.0, -1.0, 2.0, 2.0, -2.0],
            RAW.test_time: [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
        }
    )
    out = throughput_to_raw(data).raw
    thr = out.group_by(RAW.test_id, maintain_order=True).agg(
        pl.col(CYC.test_cumulated_capacity_throughput).last()
    )[CYC.test_cumulated_capacity_throughput]
    # test 0: 1 A over 2 s = 2; test 1: 2 A over 2 s = 4 (each resets at its start).
    assert thr.to_list() == pytest.approx([2.0, 4.0])


def test_throughput_to_raw_charge_discharge_rest():
    """Charge and discharge both count (|I|); a steady rest adds exactly nothing.

    One cycle sampled every 60 s: +1 A charge for 3600 s (1 Ah), rest, -1 A
    discharge for 3600 s (1 Ah), rest. Steady-rest intervals (0 A at both ends)
    must contribute exactly 0; the only nonzero rest-labelled rows are the step
    edges, which trapezoidal integration splits.
    """
    cur, tt, phase = [1.0], [0.0], ["charge"]
    t = 0.0
    for c, dur, name in [
        (1.0, 3600, "charge"),
        (0.0, 600, "rest"),
        (-1.0, 3600, "discharge"),
        (0.0, 600, "rest"),
    ]:
        for _ in range(dur // 60):
            t += 60.0
            cur.append(c)
            tt.append(t)
            phase.append(name)
    data = Data()
    data.raw = pl.DataFrame({RAW.current: cur, RAW.test_time: tt, "phase": phase})
    out = throughput_to_raw(data, nom_cap_abs=1.0, conversion_factor=1.0 / 3600.0).raw

    d_ah = out[CYC.test_cumulated_capacity_throughput].diff().fill_null(0.0)
    out = out.with_columns(d_ah.alias("_d"))
    # Steady rest (current 0 at both ends of the interval) adds exactly zero.
    steady_rest = out.filter(
        (pl.col(RAW.current) == 0.0) & (pl.col(RAW.current).shift(1) == 0.0)
    )["_d"]
    assert steady_rest.sum() == pytest.approx(0.0)
    assert steady_rest.len() > 0
    # Charge and discharge phases each integrate to ~1 Ah (their steady interiors).
    for name in ("charge", "discharge"):
        got = out.filter(pl.col("phase") == name)["_d"].sum()
        assert got == pytest.approx(1.0, abs=0.02)


def test_throughput_to_raw(mock_data_with_raw: Data):
    data = throughput_to_raw(mock_data_with_raw, nom_cap_abs=NOM_CAP)
    raw = data.raw

    throughput = raw[CYC.test_cumulated_capacity_throughput]
    efc = raw[CYC.equivalent_full_cycles]

    # Non-decreasing, starting at zero.
    assert throughput[0] == 0.0
    assert (throughput.diff().fill_null(0.0) >= 0.0).all()

    # Rest intervals (zero current at both ends) add nothing. Boundary rows are
    # excluded on purpose: trapezoidal integration credits the ramp interval
    # leaving a rest to the mean of its endpoints, which is not zero.
    deltas = throughput.diff().fill_null(0.0)
    rest_deltas = raw.with_columns(deltas.alias("_d")).filter(
        (pl.col(RAW.current) == 0.0) & (pl.col(RAW.current).shift(1) == 0.0)
    )["_d"]
    assert (rest_deltas == 0.0).all()
    assert rest_deltas.len() > 0

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


def test_efc_added_by_scaled_columns_native():
    """EFC is emitted unconditionally by ``add_scaled_summary_columns`` (no flag)."""
    core = CellpyCellCore()
    data = Data()
    data.raw = create_raw_data()
    data = core.make_core_step_table(data)
    data = core.make_core_summary(data)
    data = core.add_scaled_summary_columns(
        data, nom_cap_abs=NOM_CAP, normalization_cycles=None, specifics=["absolute"]
    )
    assert CYC.test_cumulated_capacity_throughput in data.summary.columns
    assert CYC.equivalent_full_cycles in data.summary.columns


def test_efc_added_by_scaled_columns_legacy_bridge():
    """The legacy bridge renames to the legacy header names (jepegit, issue #138)."""
    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = create_raw_data().to_pandas()
    core.make_core_step_table(data, nom_cap=1.0)
    core.make_core_summary(data)
    data = core.add_scaled_summary_columns(
        data, nom_cap_abs=NOM_CAP, normalization_cycles=None, specifics=["absolute"]
    )
    # Legacy names (no ``test_`` prefix on throughput), not the native ones.
    assert "cumulated_capacity_throughput" in data.summary.columns
    assert "equivalent_full_cycles" in data.summary.columns
    assert CYC.test_cumulated_capacity_throughput not in data.summary.columns
