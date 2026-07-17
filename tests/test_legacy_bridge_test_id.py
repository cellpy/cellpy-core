"""Legacy bridge preserves ``test_id`` on steps/summary (issue #136)."""

from __future__ import annotations

import pandas as pd
import pytest

from cellpycore.cell_core import Data, OldCellpyCellCore
from cellpycore.config import RawCols
from cellpycore.legacy import HeadersNormal, mapping
from cellpycore.merge import merge_data


def _native_merged_to_legacy_raw() -> pd.DataFrame:
    """Two-test overlapping-cycle raw in legacy ``HeadersNormal`` naming."""
    # Mirror ``tests/test_schema._build_merged_raw`` then rename to legacy.
    nhdr = RawCols()
    records = []
    dp = 0
    for test_id in (0, 1):
        scale = 1.0 if test_id == 0 else 2.0
        for cyc in (1, 2):
            for k in range(5):
                records.append(
                    {
                        nhdr.test_id: test_id,
                        nhdr.datapoint_num: dp,
                        nhdr.test_time: float(dp),
                        nhdr.step_time: float(k),
                        nhdr.step_num: 1,
                        nhdr.cycle_num: cyc,
                        nhdr.current: 1.0,
                        nhdr.potential: 3.5 + 0.01 * k,
                        nhdr.cumulative_charge_capacity: scale * 0.1 * (k + 1),
                        nhdr.cumulative_discharge_capacity: 0.0,
                        nhdr.internal_resistance: 0.0,
                    }
                )
                dp += 1
            for k in range(5):
                records.append(
                    {
                        nhdr.test_id: test_id,
                        nhdr.datapoint_num: dp,
                        nhdr.test_time: float(dp),
                        nhdr.step_time: float(k),
                        nhdr.step_num: 2,
                        nhdr.cycle_num: cyc,
                        nhdr.current: -1.0,
                        nhdr.potential: 3.9 - 0.01 * k,
                        nhdr.cumulative_charge_capacity: scale * 0.5,
                        nhdr.cumulative_discharge_capacity: scale * 0.08 * (k + 1),
                        nhdr.internal_resistance: 0.0,
                    }
                )
                dp += 1
    native = pd.DataFrame(records)
    rename = {
        native_name: legacy_name for native_name, legacy_name in mapping.RAW_PAIRS
    }
    # ``test_id`` is an identity passthrough (same name both sides).
    return native.rename(columns=rename)


def test_bridge_steps_and_summary_carry_test_id():
    """Outbound legacy frames keep ``test_id`` so summary can window per test."""
    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = _native_merged_to_legacy_raw()

    core.make_core_step_table(data, nom_cap=1.0)
    steps = data.steps
    tid = core.step_cols.test_id
    assert tid in steps.columns
    assert set(steps[tid].unique()) == {0, 1}
    assert len(steps) == 8  # 2 tests * 2 cycles * 2 steps

    core.make_core_summary(data, find_ir=False, find_end_voltage=False)
    summary = data.summary
    stid = core.cycle_cols.test_id
    assert stid in summary.columns
    assert set(summary[stid].unique()) == {0, 1}
    assert len(summary) == 4


def test_bridge_legacy_cruft_resets_per_test():
    """``_add_legacy_summary_cruft`` cumsums do not leak across ``test_id``."""
    core = OldCellpyCellCore(initialize=False)
    data = Data()
    data.raw = _native_merged_to_legacy_raw()
    core.make_core_step_table(data, nom_cap=1.0)
    core.make_core_summary(data, find_ir=False, find_end_voltage=False)

    leg = core.cycle_cols
    s = data.summary.sort_values([leg.test_id, leg.cycle_index]).reset_index(drop=True)
    # First cycle of each test: cumulated CE equals that cycle's CE (restart).
    for tid in (0, 1):
        block = s[s[leg.test_id] == tid].reset_index(drop=True)
        assert block.iloc[0][leg.cumulated_coulombic_efficiency] == pytest.approx(
            block.iloc[0][leg.coulombic_efficiency]
        )


def test_merge_data_rejects_legacy_schema():
    """``merge_data`` hard-fails on ``OldCellpyCellCore.schema`` (Headers*)."""
    legacy = OldCellpyCellCore(initialize=False)
    left = Data()
    right = Data()
    left.raw = pd.DataFrame({"data_point": [1], "test_id": [0]})
    right.raw = pd.DataFrame({"data_point": [1], "test_id": [1]})
    with pytest.raises(TypeError, match="native config.Schema"):
        merge_data(left, right, schema=legacy.schema)


def test_headers_expose_test_id():
    """Legacy header dataclasses declare the bridged ``test_id`` field."""
    assert HeadersNormal().test_id_txt == "test_id"
    core = OldCellpyCellCore(initialize=False)
    assert core.step_cols.test_id == "test_id"
    assert core.cycle_cols.test_id == "test_id"
