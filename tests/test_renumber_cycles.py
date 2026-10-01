"""Tests for ``summarizers.renumber_cycles`` (issue #359 / Stage 5 S3).

A cycler's cycle counter is repaired so every cycle opens with a chosen step
direction. Synthetic raw frames are built from a per-cycler-cycle pattern of
half-cycle tokens (``"C"`` charge, ``"D"`` discharge, ``"R"`` rest, ``"V"``
cv_charge); the expected result is derived with a plain Python oracle over the
same tokens.
"""

from pathlib import Path

import pandas as pd
import polars as pl
import pytest

from cellpycore import config, summarizers
from cellpycore.cell_core import Data
from cellpycore.config import StepDirection, default_schema
from cellpycore.exceptions import NoDataFound

POINTS_PER_STEP = 4
CAP_PER_POINT = 0.1
HARMONIZED_RAW = Path(__file__).parent / "data" / "cycler_cc_harmonized_raw.parquet"

_TOKEN_DIRECTION = {"C": 1, "V": 1, "D": -1, "R": 0}
_TOKEN_STEP_TYPE = {"C": "charge", "V": "cv_charge", "D": "discharge", "R": "rest"}


def _build_raw(pattern, nhdr, first_cycle=1, test_id=None, dp0=0, with_energy=False):
    """Raw frame from a list of cycler cycles, each a list of half-cycle tokens.

    Step numbers are unique over the whole test (so the step table maps back
    unambiguously). Capacities are cycle-cumulative per the cycler's own
    counter; current/potential are shaped so the built-in classifier labels the
    steps without overrides.
    """
    records = []
    dp = dp0
    step = 0
    for i, tokens in enumerate(pattern):
        cyc = first_cycle + i
        cc = dc = 0.0
        volt = 3.7
        for tok in tokens:
            step += 1
            for k in range(POINTS_PER_STEP):
                if tok == "C":
                    cur, volt, cc = 1.0, volt + 0.1, cc + CAP_PER_POINT
                elif tok == "V":
                    cur, cc = 0.5 - 0.1 * k, cc + CAP_PER_POINT / 2
                elif tok == "D":
                    cur, volt, dc = -1.0, volt - 0.1, dc + CAP_PER_POINT
                else:  # rest: a tiny drift keeps the classifier off the ``ir`` rule
                    cur, volt = 0.0, volt + 0.001
                row = {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.cycle_num: cyc,
                    nhdr.step_num: step,
                    nhdr.current: cur,
                    nhdr.potential: volt,
                    nhdr.cumulative_charge_capacity: cc,
                    nhdr.cumulative_discharge_capacity: dc,
                }
                if with_energy:
                    row[nhdr.cumulative_charge_energy] = cc * 3.7
                    row[nhdr.cumulative_discharge_energy] = dc * 3.7
                if test_id is not None:
                    row[nhdr.test_id] = test_id
                records.append(row)
                dp += 1
    return pl.DataFrame(records)


def _oracle(pattern, opening=StepDirection.CHARGE, first_cycle=1):
    """Expected (new cycle per step, per-cycle charge/discharge totals)."""
    open_sign = 1 if opening == StepDirection.CHARGE else -1
    cycles, totals = [], {}
    prev = None
    cyc = first_cycle
    first = True
    for tokens in pattern:
        for tok in tokens:
            d = _TOKEN_DIRECTION[tok]
            if not first and d == open_sign and prev == -open_sign:
                cyc += 1
            first = False
            if d != 0:
                prev = d
            cycles.append(cyc)
            ch, dch = totals.setdefault(cyc, [0.0, 0.0])
            if tok == "C":
                ch += CAP_PER_POINT * POINTS_PER_STEP
            elif tok == "V":
                ch += CAP_PER_POINT / 2 * POINTS_PER_STEP
            elif tok == "D":
                dch += CAP_PER_POINT * POINTS_PER_STEP
            totals[cyc] = [ch, dch]
    return cycles, totals


def _data(raw, schema):
    data = Data()
    data.raw = raw
    summarizers.make_step_table(data, schema)
    return data


def _step_types(data, schema):
    shdr = schema.step
    steps = data.steps.sort(shdr.datapoint_num_first)
    return steps[shdr.step_type].to_list()


def _check_pattern(pattern, opening=StepDirection.CHARGE, first_cycle=1):
    schema = default_schema()
    nhdr, shdr, chdr = schema.raw, schema.step, schema.cycle
    raw = _build_raw(pattern, nhdr, first_cycle=first_cycle)
    data = _data(raw, schema)
    tokens = [tok for tokens in pattern for tok in tokens]
    assert _step_types(data, schema) == [_TOKEN_STEP_TYPE[t] for t in tokens]

    summarizers.renumber_cycles(data, schema, opening=opening)

    exp_cycles, exp_totals = _oracle(pattern, opening, first_cycle)
    steps = data.steps.sort(shdr.datapoint_num_first)
    assert steps[shdr.cycle_num].to_list() == exp_cycles
    assert _step_types(data, schema) == [_TOKEN_STEP_TYPE[t] for t in tokens]
    # Raw rows carry the same new cycle as their step.
    per_row = [c for c in exp_cycles for _ in range(POINTS_PER_STEP)]
    assert data.raw.sort(nhdr.datapoint_num)[nhdr.cycle_num].to_list() == per_row

    summarizers.make_summary(data, schema)
    summary = data.summary.sort(chdr.cycle_num)
    assert summary[chdr.cycle_num].to_list() == sorted(exp_totals)
    for cyc, ch, dch in zip(
        summary[chdr.cycle_num],
        summary[chdr.charge_capacity],
        summary[chdr.discharge_capacity],
    ):
        assert ch == pytest.approx(exp_totals[cyc][0])
        assert dch == pytest.approx(exp_totals[cyc][1])
    return data


def test_lone_first_discharge_already_correct_is_noop():
    schema = default_schema()
    raw = _build_raw([["D"], ["C", "D"], ["C", "D"]], schema.raw)
    data = _data(raw, schema)
    raw_before, steps_before = data.raw.clone(), data.steps.clone()
    summarizers.make_summary(data, schema)

    summarizers.renumber_cycles(data, schema)

    assert data.raw.equals(raw_before)
    assert data.steps.equals(steps_before)
    assert data.summary is not None  # untouched on a no-op


def test_first_cycle_discharge_charge_discharge_is_split():
    data = _check_pattern([["D", "C", "D"], ["C", "D"], ["C", "D"]])
    chdr = default_schema().cycle
    assert data.summary[chdr.cycle_num].to_list() == [1, 2, 3, 4]


def test_all_cycles_discharge_charge_are_shifted():
    data = _check_pattern([["D", "C"], ["D", "C"], ["D", "C"]])
    chdr = default_schema().cycle
    # [D][C D][C D][C]: the trailing lone charge is kept as its own cycle.
    assert data.summary[chdr.cycle_num].to_list() == [1, 2, 3, 4]
    assert data.summary[chdr.charge_capacity].to_list()[0] == 0.0
    assert data.summary[chdr.discharge_capacity].to_list()[-1] == 0.0


def test_rest_and_cv_attach_to_current_cycle():
    # Rests never open a cycle; CC + CV charge stay in one cycle.
    _check_pattern([["R", "D", "R", "C", "V", "R", "D"], ["R", "C", "V", "D", "R"]])


def test_opening_discharge_mirrors_for_anode_cells():
    # Anode half-cell: a test starting with a lone charge, cycler reports C-D-C.
    data = _check_pattern(
        [["C", "D", "C"], ["D", "C"]], opening=StepDirection.DISCHARGE
    )
    chdr = default_schema().cycle
    assert data.summary[chdr.cycle_num].to_list() == [1, 2, 3]


def test_opening_accepts_plain_string_and_keeps_zero_based_numbering():
    schema = default_schema()
    pattern = [["D", "C"], ["D", "C"]]
    raw = _build_raw(pattern, schema.raw, first_cycle=0)
    data = _data(raw, schema)
    summarizers.renumber_cycles(data, schema, opening="charge")
    exp_cycles, _ = _oracle(pattern, first_cycle=0)
    steps = data.steps.sort(schema.step.datapoint_num_first)
    assert steps[schema.step.cycle_num].to_list() == exp_cycles
    assert exp_cycles[0] == 0


def test_energy_columns_are_reaccumulated_too():
    schema = default_schema()
    nhdr, chdr = schema.raw, schema.cycle
    pattern = [["D", "C"], ["D", "C"]]
    raw = _build_raw(pattern, nhdr, with_energy=True)
    data = _data(raw, schema)
    summarizers.renumber_cycles(data, schema)
    _, exp_totals = _oracle(pattern)
    # Energy is capacity * 3.7 V in the builder; it must follow the new cycles.
    last_rows = (
        data.raw.sort(nhdr.datapoint_num)
        .group_by(nhdr.cycle_num, maintain_order=True)
        .agg(pl.col(nhdr.cumulative_charge_energy).last())
    )
    for cyc, energy in zip(
        last_rows[nhdr.cycle_num], last_rows[nhdr.cumulative_charge_energy]
    ):
        assert energy == pytest.approx(exp_totals[cyc][0] * 3.7)
    summarizers.make_summary(data, schema)
    assert chdr.charge_capacity in data.summary.columns


def test_multiple_tests_are_renumbered_independently():
    schema = default_schema()
    nhdr, shdr = schema.raw, schema.step
    p0 = [["D", "C"], ["D", "C"]]
    p1 = [["C", "D"], ["C", "D"]]  # already correct, 5-based numbering
    raw = pl.concat(
        [
            _build_raw(p0, nhdr, test_id=0),
            _build_raw(p1, nhdr, first_cycle=5, test_id=1, dp0=1000),
        ]
    )
    data = _data(raw, schema)
    summarizers.renumber_cycles(data, schema)
    steps = data.steps.sort([shdr.test_id, shdr.datapoint_num_first])
    exp0, _ = _oracle(p0)
    exp1, _ = _oracle(p1, first_cycle=5)
    assert steps.filter(pl.col(shdr.test_id) == 0)[shdr.cycle_num].to_list() == exp0
    assert steps.filter(pl.col(shdr.test_id) == 1)[shdr.cycle_num].to_list() == exp1
    raw1 = data.raw.filter(pl.col(nhdr.test_id) == 1)
    assert raw1[nhdr.cycle_num].unique().sort().to_list() == [5, 6]


def test_pandas_in_pandas_out():
    schema = default_schema()
    raw = _build_raw([["D", "C"], ["D", "C"]], schema.raw).to_pandas()
    data = _data(raw, schema)
    summarizers.renumber_cycles(data, schema)
    assert isinstance(data.raw, pd.DataFrame)
    assert data.raw[schema.raw.cycle_num].max() == 3
    summarizers.make_summary(data, schema, test_mode=config.TestMode.NORMAL)
    assert data.summary.height == 3


def test_summary_is_dropped_when_cycles_change():
    schema = default_schema()
    raw = _build_raw([["D", "C"], ["D", "C"]], schema.raw)
    data = _data(raw, schema)
    summarizers.make_summary(data, schema)
    summarizers.renumber_cycles(data, schema)
    assert data.summary is None


def test_requires_raw_and_steps():
    schema = default_schema()
    data = Data()
    with pytest.raises(NoDataFound):
        summarizers.renumber_cycles(data, schema)
    data.raw = _build_raw([["C", "D"]], schema.raw)
    with pytest.raises(NoDataFound):
        summarizers.renumber_cycles(data, schema)


def test_rejects_ustep_step_table():
    schema = default_schema()
    data = Data()
    data.raw = _build_raw([["D", "C"], ["D", "C"]], schema.raw)
    summarizers.make_step_table(data, schema, usteps=True)
    with pytest.raises(ValueError, match="usteps"):
        summarizers.renumber_cycles(data, schema)


def test_rejects_unknown_opening():
    schema = default_schema()
    data = _data(_build_raw([["C", "D"]], schema.raw), schema)
    with pytest.raises(ValueError):
        summarizers.renumber_cycles(data, schema, opening="sideways")


@pytest.mark.skipif(not HARMONIZED_RAW.exists(), reason="harmonized fixture missing")
def test_harmonized_fixture_noop_and_recount():
    """The anode half-cell fixture is [D C] x 17 + [D] on the cycler counter.

    Opening on discharge matches that counter (byte-identical no-op); opening
    on charge regroups it as [D] + [C D] x 17 with capacity conserved.
    """
    schema = default_schema()
    shdr, chdr = schema.step, schema.cycle
    data = Data()
    data.raw = pl.read_parquet(HARMONIZED_RAW)
    summarizers.make_step_table(data, schema)
    raw_before = data.raw.clone()
    summarizers.make_summary(data, schema, test_mode=config.TestMode.INVERTED)
    summary_before = data.summary

    summarizers.renumber_cycles(data, schema, opening=StepDirection.DISCHARGE)
    assert data.raw.equals(raw_before)

    types_before = sorted(data.steps[shdr.step_type].to_list())
    summarizers.renumber_cycles(data, schema, opening=StepDirection.CHARGE)
    summarizers.make_summary(data, schema)
    summary = data.summary.sort(chdr.cycle_num)
    assert summary.height == summary_before.height == 18
    assert summary[chdr.charge_capacity][0] == pytest.approx(0.0, abs=1e-9)
    assert sorted(data.steps[shdr.step_type].to_list()) == types_before
    for col in (chdr.charge_capacity, chdr.discharge_capacity):
        assert summary[col].sum() == pytest.approx(summary_before[col].sum())
    # Every cycle after the first pairs one charge with the following discharge.
    first = data.steps.sort(shdr.datapoint_num_first).filter(
        pl.col(shdr.step_type).is_in(["charge", "discharge"])
    )
    per_cycle = first.group_by(shdr.cycle_num, maintain_order=True).agg(
        pl.col(shdr.step_type)
    )
    assert per_cycle[shdr.step_type].to_list()[0] == ["discharge"]
    assert all(
        seq == ["charge", "discharge"]
        for seq in per_cycle[shdr.step_type].to_list()[1:]
    )
