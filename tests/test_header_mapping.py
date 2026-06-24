"""Round-trip / totality tests for the authoritative header mapping.

These lock the native ``config.Cols`` <-> legacy ``Headers*`` mapping declared in
``cellpycore.header_mapping`` so the translation is provably **lossless and total**
(every column on each side either maps to the other side or is listed in a
documented exception set) and so the legacy bridge cannot silently drift away
from it.

Granularity note: the mapping is compared over column-name *strings* (the field
values). The step table is compared at *base-signal* granularity (statistic
columns ``<signal>_<stat>`` are reduced to ``<signal>``), because the engine emits
per-signal statistics that share one declared base correspondence.
"""

import dataclasses

from cellpycore import config, header_mapping
from cellpycore.cell_core import OldCellpyCellCore
from cellpycore.legacy import HeadersNormal, HeadersStepTable, HeadersSummary


# --- helpers ----------------------------------------------------------------
def _native_values(cols_cls) -> set:
    """Distinct column-name strings declared on a native ``config.Cols`` class."""
    return {getattr(cols_cls, name) for name in cols_cls.__annotations__}


def _legacy_values(headers_cls) -> set:
    """Distinct column-name strings declared on a legacy ``Headers*`` dataclass."""
    return {f.default for f in dataclasses.fields(headers_cls)}


_STAT_NATIVE = set(header_mapping.STAT_SUFFIXES)


def _step_signal(value: str) -> str:
    """Reduce a step column ``<signal>_<stat>`` to its base ``<signal>``."""
    head, _, tail = value.rpartition("_")
    if head and tail in _STAT_NATIVE:
        return head
    return value


# --- bijection / round-trip -------------------------------------------------
def test_stat_suffixes_bijective():
    legacy_stats = list(header_mapping.STAT_SUFFIXES.values())
    assert len(legacy_stats) == len(set(legacy_stats))


def _assert_pairs_bijective(pairs):
    natives = [n for n, _ in pairs]
    legacies = [legacy for _, legacy in pairs]
    assert len(natives) == len(set(natives)), "native names not unique"
    assert len(legacies) == len(set(legacies)), "legacy names not unique"


def test_pair_lists_are_bijective():
    _assert_pairs_bijective(header_mapping.RAW_PAIRS)
    _assert_pairs_bijective(header_mapping.STEP_BASE_PAIRS)
    _assert_pairs_bijective(header_mapping.STEP_SCALAR_PAIRS)
    _assert_pairs_bijective(header_mapping.CYCLE_PAIRS)


def test_step_round_trip_identity():
    n2l = header_mapping.native_to_legacy_step()
    l2n = header_mapping.legacy_to_native_step()
    assert n2l, "expected a non-empty step rename"
    for native, legacy in n2l.items():
        assert l2n[legacy] == native


def test_summary_round_trip_identity():
    n2l = header_mapping.native_to_legacy_summary()
    l2n = header_mapping.legacy_to_native_summary()
    assert n2l
    for native, legacy in n2l.items():
        assert l2n[legacy] == native


# --- raw totality -----------------------------------------------------------
def test_raw_native_totality():
    native_vals = _native_values(config.RawCols)
    mapped = {n for n, _ in header_mapping.RAW_PAIRS}
    assert mapped <= native_vals
    assert mapped.isdisjoint(header_mapping.NATIVE_ONLY_RAW)
    assert mapped | header_mapping.NATIVE_ONLY_RAW == native_vals


def test_raw_legacy_totality():
    legacy_vals = _legacy_values(HeadersNormal)
    mapped = {legacy for _, legacy in header_mapping.RAW_PAIRS}
    assert mapped <= legacy_vals
    assert mapped.isdisjoint(header_mapping.LEGACY_ONLY_RAW)
    assert mapped | header_mapping.LEGACY_ONLY_RAW == legacy_vals


# --- step totality (base-signal granularity) --------------------------------
def test_step_native_totality():
    native_signals = {_step_signal(v) for v in _native_values(config.StepCols)}
    mapped = {n for n, _ in header_mapping.STEP_BASE_PAIRS} | {
        n for n, _ in header_mapping.STEP_SCALAR_PAIRS
    }
    assert mapped <= native_signals
    assert mapped.isdisjoint(header_mapping.NATIVE_ONLY_STEP)
    assert mapped | header_mapping.NATIVE_ONLY_STEP == native_signals


def test_step_legacy_totality():
    legacy_vals = _legacy_values(HeadersStepTable)
    mapped = {legacy for _, legacy in header_mapping.STEP_BASE_PAIRS} | {
        legacy for _, legacy in header_mapping.STEP_SCALAR_PAIRS
    }
    assert mapped <= legacy_vals
    assert mapped.isdisjoint(header_mapping.LEGACY_ONLY_STEP)
    assert mapped | header_mapping.LEGACY_ONLY_STEP == legacy_vals


# --- cycle / summary totality ----------------------------------------------
def test_cycle_native_totality():
    native_vals = _native_values(config.CycleCols)
    mapped = {n for n, _ in header_mapping.CYCLE_PAIRS}
    assert mapped <= native_vals
    assert mapped.isdisjoint(header_mapping.NATIVE_ONLY_CYCLE)
    assert mapped | header_mapping.NATIVE_ONLY_CYCLE == native_vals


def test_cycle_legacy_totality():
    legacy_vals = _legacy_values(HeadersSummary)
    mapped = {legacy for _, legacy in header_mapping.CYCLE_PAIRS}
    assert mapped <= legacy_vals
    assert mapped.isdisjoint(header_mapping.LEGACY_ONLY_CYCLE)
    assert mapped | header_mapping.LEGACY_ONLY_CYCLE == legacy_vals


# --- spot-checks (guard against accidental pair edits) ----------------------
def test_known_translations():
    assert header_mapping.legacy_to_native_raw() == {
        "data_point": "datapoint_num",
        "test_time": "test_time",
        "step_time": "step_time",
        "cycle_index": "cycle_num",
        "step_index": "step_num",
        "current": "current",
        "voltage": "potential",
        "charge_capacity": "cumulative_charge_capacity",
        "discharge_capacity": "cumulative_discharge_capacity",
        "internal_resistance": "internal_resistance",
    }
    step = header_mapping.native_to_legacy_step()
    assert step["current_mean"] == "current_avr"
    assert step["potential_first"] == "voltage_first"
    assert step["c_rate"] == "rate_avr"
    summary = header_mapping.native_to_legacy_summary()
    assert summary["cycle_num"] == "cycle_index"
    assert summary["potential_end_charge"] == "end_voltage_charge"
    assert summary["ir_charge"] == "ir_charge"  # identity pass-through


# --- bridge parity (the bridge must use the authoritative mapping) ----------
def test_bridge_uses_header_mapping():
    core = OldCellpyCellCore(initialize=False)
    legacy_raw_cols = list(_legacy_values(HeadersNormal))
    assert core._legacy_to_native_raw_rename(
        legacy_raw_cols
    ) == header_mapping.legacy_to_native_raw(legacy_raw_cols)
    assert (
        core._native_to_legacy_step_rename()
        == header_mapping.native_to_legacy_step()
    )
    assert (
        core._legacy_to_native_step_rename()
        == header_mapping.legacy_to_native_step()
    )
    assert (
        core._native_to_legacy_summary_rename()
        == header_mapping.native_to_legacy_summary()
    )
    assert (
        core._legacy_to_native_summary_rename()
        == header_mapping.legacy_to_native_summary()
    )
