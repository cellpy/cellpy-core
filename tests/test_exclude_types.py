"""Tests for native exclude-types summary support (issue #54).

``summarizers.make_summary(exclude_step_types=[...])`` subtracts the excluded
steps' per-cycle capacity deltas from the cycle-end summary values, replacing
the capability of the removed pandas ``summary_selector_exluder`` (issue #45).
The parity oracle below is that removed implementation's math, ported to native
column names (capacities only, which is all that survives in the native
summary).
"""

import pandas as pd
import polars as pl
import pytest
from pandas.testing import assert_frame_equal

from cellpycore import summarizers
from cellpycore.cell_core import Data
from cellpycore.config import RawCols, Schema, default_schema

_OVERRIDE_STEP_TYPES = {1: "charge", 2: "cv_charge", 3: "discharge", 4: "cv_discharge"}


def _build_cv_raw(nhdr: RawCols, cv_cycles=(1, 2)) -> pd.DataFrame:
    """2 cycles of charge / cv_charge / discharge / cv_discharge raw data.

    Capacities are cycle-cumulative. Cycles listed in ``cv_cycles`` get the two
    CV steps; the others end at charge cc=0.5 / discharge dc=0.4.
    """
    records = []
    dp = 0
    for cyc in (1, 2):
        with_cv = cyc in cv_cycles
        cc_top = 0.6 if with_cv else 0.5

        def _row(step, k, cur, volt, cc, dc):
            return {
                nhdr.datapoint_num: dp,
                nhdr.test_time: float(dp),
                nhdr.step_time: float(k),
                nhdr.step_num: step,
                nhdr.cycle_num: cyc,
                nhdr.current: cur,
                nhdr.potential: volt,
                nhdr.cumulative_charge_capacity: cc,
                nhdr.cumulative_discharge_capacity: dc,
                nhdr.internal_resistance: 0.0,
            }

        for k in range(5):  # charge: cc 0.1..0.5
            records.append(_row(1, k, 1.0, 3.5 + 0.01 * k, 0.1 * (k + 1), 0.0))
            dp += 1
        if with_cv:
            for k in range(5):  # cv_charge: cc 0.52..0.60, current tapers
                records.append(_row(2, k, 0.5 - 0.1 * k, 4.0, 0.5 + 0.02 * (k + 1), 0.0))
                dp += 1
        for k in range(5):  # discharge: dc 0.08..0.4
            records.append(_row(3, k, -1.0, 3.9 - 0.01 * k, cc_top, 0.08 * (k + 1)))
            dp += 1
        if with_cv:
            for k in range(5):  # cv_discharge: dc 0.42..0.50, current tapers
                records.append(
                    _row(4, k, -0.5 + 0.1 * k, 3.0, cc_top, 0.4 + 0.02 * (k + 1))
                )
                dp += 1
    return pd.DataFrame(records)


def _data_with_steps(raw: pd.DataFrame, schema: Schema) -> Data:
    data = Data()
    data.raw = raw
    summarizers.make_step_table(
        data, schema, override_step_types=_OVERRIDE_STEP_TYPES
    )
    return data


def _pandas_oracle(
    raw: pd.DataFrame, steps: pd.DataFrame, exclude_types, schema: Schema
) -> pd.DataFrame:
    """The removed ``summary_selector_exluder`` math on native names.

    Selects the cycle-end raw rows, then subtracts the excluded steps' summed
    per-cycle ``last - first`` capacity deltas (left-merge + ``fillna(0.0)``),
    exactly as the pandas implementation removed in issue #45 did.
    """
    nhdr, shdr = schema.raw, schema.step

    finals = (
        steps.sort_values(shdr.datapoint_num_last)
        .groupby(shdr.cycle_num)[shdr.datapoint_num_last]
        .last()
        .values
    )
    selected = raw[raw[nhdr.datapoint_num].isin(finals)].copy()

    q = None
    for prefix in exclude_types:
        _q = ~steps[shdr.step_type].str.startswith(prefix)
        q = _q if q is None else q & _q

    delta = steps.loc[~q, [shdr.cycle_num]].copy()
    delta["__ch"] = (
        steps.loc[~q, shdr.charge_capacity_last]
        - steps.loc[~q, shdr.charge_capacity_first]
    )
    delta["__dch"] = (
        steps.loc[~q, shdr.discharge_capacity_last]
        - steps.loc[~q, shdr.discharge_capacity_first]
    )
    delta = delta.groupby(shdr.cycle_num).sum().reset_index()

    selected = selected.merge(
        delta, how="left", left_on=nhdr.cycle_num, right_on=shdr.cycle_num
    ).fillna(0.0)
    selected[nhdr.cumulative_charge_capacity] -= selected["__ch"]
    selected[nhdr.cumulative_discharge_capacity] -= selected["__dch"]
    return selected


def test_exclude_cv_matches_pandas_oracle():
    """exclude_step_types=["cv_"] reproduces the removed pandas implementation."""
    schema = default_schema()
    nhdr, chdr = schema.raw, schema.cycle
    raw = _build_cv_raw(nhdr)
    data = _data_with_steps(raw, schema)

    summarizers.make_summary(data, schema, exclude_step_types=["cv_"])
    summary = data.summary

    oracle = _pandas_oracle(raw, data.steps.to_pandas(), ["cv_"], schema)

    got = summary.select(
        [chdr.cycle_num, chdr.charge_capacity, chdr.discharge_capacity]
    ).to_pandas()
    expected = oracle[
        [
            nhdr.cycle_num,
            nhdr.cumulative_charge_capacity,
            nhdr.cumulative_discharge_capacity,
        ]
    ].reset_index(drop=True)
    expected.columns = got.columns
    assert_frame_equal(got, expected, check_dtype=False)

    # sanity: the CV contributions really were removed (cv_charge adds 0.08
    # from its first recorded row, cv_discharge 0.08, per cycle)
    assert summary[chdr.charge_capacity].to_list() == pytest.approx([0.52, 0.52])
    assert summary[chdr.discharge_capacity].to_list() == pytest.approx([0.42, 0.42])


def test_derived_columns_use_corrected_capacities():
    """CE / coulombic difference are computed from the corrected capacities."""
    schema = default_schema()
    chdr = schema.cycle
    data = _data_with_steps(_build_cv_raw(schema.raw), schema)
    summarizers.make_summary(data, schema, exclude_step_types=["cv_"])
    s = data.summary

    cc = s[chdr.charge_capacity].to_list()
    dc = s[chdr.discharge_capacity].to_list()
    assert s[chdr.coulombic_efficiency].to_list() == pytest.approx(
        [100.0 * d / c for c, d in zip(cc, dc)]
    )
    assert s[chdr.coulombic_difference].to_list() == pytest.approx(
        [c - d for c, d in zip(cc, dc)]
    )


def test_exclude_none_and_empty_leave_summary_untouched():
    """None (default) and [] are byte-identical to the plain summary."""
    schema = default_schema()
    baseline = _data_with_steps(_build_cv_raw(schema.raw), schema)
    summarizers.make_summary(baseline, schema)

    for exclude in (None, []):
        data = _data_with_steps(_build_cv_raw(schema.raw), schema)
        summarizers.make_summary(data, schema, exclude_step_types=exclude)
        assert data.summary.equals(baseline.summary)


def test_unmatched_prefix_gives_zero_correction():
    """A prefix matching no step yields the uncorrected summary (fill_null path)."""
    schema = default_schema()
    baseline = _data_with_steps(_build_cv_raw(schema.raw), schema)
    summarizers.make_summary(baseline, schema)

    data = _data_with_steps(_build_cv_raw(schema.raw), schema)
    summarizers.make_summary(data, schema, exclude_step_types=["taper_"])
    assert data.summary.equals(baseline.summary)


def test_cycle_without_excluded_step_is_uncorrected():
    """Only cycles containing an excluded step get a correction."""
    schema = default_schema()
    nhdr, chdr = schema.raw, schema.cycle
    data = _data_with_steps(_build_cv_raw(nhdr, cv_cycles=(1,)), schema)
    summarizers.make_summary(data, schema, exclude_step_types=["cv_"])
    s = data.summary.sort(chdr.cycle_num)

    # cycle 1 has CV steps (corrected); cycle 2 has none (cycle-end kept)
    assert s[chdr.charge_capacity].to_list() == pytest.approx([0.52, 0.5])
    assert s[chdr.discharge_capacity].to_list() == pytest.approx([0.42, 0.4])


def test_only_cv_prefix_semantics():
    """exclude ["charge", "discharge"] drops the plain steps, keeps cv_ ones.

    This locks the ``startswith`` semantics of the removed implementation (its
    ``selector_type="only-cv"`` mapping): ``cv_charge`` does not start with
    ``"charge"``, so only the plain charge / discharge contributions go.
    """
    schema = default_schema()
    chdr = schema.cycle
    data = _data_with_steps(_build_cv_raw(schema.raw), schema)
    summarizers.make_summary(
        data, schema, exclude_step_types=["charge", "discharge"]
    )
    s = data.summary.sort(chdr.cycle_num)

    # plain charge contributes 0.4 (first row 0.1 -> last 0.5), plain
    # discharge 0.32 (0.08 -> 0.4); the cv contributions stay in.
    assert s[chdr.charge_capacity].to_list() == pytest.approx([0.2, 0.2])
    assert s[chdr.discharge_capacity].to_list() == pytest.approx([0.18, 0.18])


def test_merged_tests_corrections_stay_isolated():
    """In a merged two-test frame the correction never leaks across test_id."""
    schema = default_schema()
    nhdr, chdr = schema.raw, schema.cycle

    # test 0 has CV steps, test 1 does not; overlapping cycle numbers.
    raw0 = _build_cv_raw(nhdr, cv_cycles=(1, 2))
    raw0[nhdr.test_id] = 0
    raw1 = _build_cv_raw(nhdr, cv_cycles=())
    raw1[nhdr.test_id] = 1
    raw1[nhdr.datapoint_num] += len(raw0)
    merged = pd.concat([raw0, raw1], ignore_index=True)

    data = _data_with_steps(merged, schema)
    summarizers.make_summary(data, schema, exclude_step_types=["cv_"])
    s = data.summary.sort([chdr.test_id, chdr.cycle_num])

    assert s.filter(pl.col(chdr.test_id) == 0)[
        chdr.charge_capacity
    ].to_list() == pytest.approx([0.52, 0.52])
    # test 1 has no CV steps at all: cycle-end values untouched
    assert s.filter(pl.col(chdr.test_id) == 1)[
        chdr.charge_capacity
    ].to_list() == pytest.approx([0.5, 0.5])
