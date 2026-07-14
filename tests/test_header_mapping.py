"""Round-trip / totality tests for the authoritative header mapping.

These lock the native ``config.Cols`` <-> legacy ``Headers*`` mapping declared in
``cellpycore.legacy.mapping`` so the translation is provably **lossless and total**
(every column on each side either maps to the other side or is listed in a
documented exception set) and so the legacy bridge cannot silently drift away
from it.

Granularity note: the mapping is compared over column-name *strings* (the field
values). The step table is compared at *base-signal* granularity (statistic
columns ``<signal>_<stat>`` are reduced to ``<signal>``), because the engine emits
per-signal statistics that share one declared base correspondence.
"""

import dataclasses

from cellpycore import config
from cellpycore.cell_core import OldCellpyCellCore
from cellpycore.legacy import HeadersNormal, HeadersStepTable, HeadersSummary, mapping


# --- helpers ----------------------------------------------------------------
def _native_values(cols_cls) -> set:
    """Distinct column-name strings declared on a native ``config.Cols`` class."""
    return {getattr(cols_cls, name) for name in cols_cls.__annotations__}


def _legacy_values(headers_cls) -> set:
    """Distinct column-name strings declared on a legacy ``Headers*`` dataclass."""
    return {f.default for f in dataclasses.fields(headers_cls)}


_STAT_NATIVE = set(mapping.STAT_SUFFIXES)


def _step_signal(value: str) -> str:
    """Reduce a step column ``<signal>_<stat>`` to its base ``<signal>``."""
    head, _, tail = value.rpartition("_")
    if head and tail in _STAT_NATIVE:
        return head
    return value


# --- bijection / round-trip -------------------------------------------------
def test_stat_suffixes_bijective():
    legacy_stats = list(mapping.STAT_SUFFIXES.values())
    assert len(legacy_stats) == len(set(legacy_stats))


def _assert_pairs_bijective(pairs):
    natives = [n for n, _ in pairs]
    legacies = [legacy for _, legacy in pairs]
    assert len(natives) == len(set(natives)), "native names not unique"
    assert len(legacies) == len(set(legacies)), "legacy names not unique"


def test_pair_lists_are_bijective():
    _assert_pairs_bijective(mapping.RAW_PAIRS)
    _assert_pairs_bijective(mapping.STEP_BASE_PAIRS)
    _assert_pairs_bijective(mapping.STEP_SCALAR_PAIRS)
    _assert_pairs_bijective(mapping.CYCLE_PAIRS)


def test_step_round_trip_identity():
    n2l = mapping.native_to_legacy_step()
    l2n = mapping.legacy_to_native_step()
    assert n2l, "expected a non-empty step rename"
    for native, legacy in n2l.items():
        assert l2n[legacy] == native


def test_summary_round_trip_identity():
    n2l = mapping.native_to_legacy_summary()
    l2n = mapping.legacy_to_native_summary()
    assert n2l
    for native, legacy in n2l.items():
        assert l2n[legacy] == native


# --- raw totality -----------------------------------------------------------
def test_raw_native_totality():
    native_vals = _native_values(config.RawCols)
    mapped = {n for n, _ in mapping.RAW_PAIRS}
    assert mapped <= native_vals
    assert mapped.isdisjoint(mapping.NATIVE_ONLY_RAW)
    assert mapped | mapping.NATIVE_ONLY_RAW == native_vals


def test_raw_legacy_totality():
    legacy_vals = _legacy_values(HeadersNormal)
    mapped = {legacy for _, legacy in mapping.RAW_PAIRS}
    assert mapped <= legacy_vals
    assert mapped.isdisjoint(mapping.LEGACY_ONLY_RAW)
    assert mapped | mapping.LEGACY_ONLY_RAW == legacy_vals


# --- step totality (base-signal granularity) --------------------------------
def test_step_native_totality():
    native_signals = {_step_signal(v) for v in _native_values(config.StepCols)}
    mapped = {n for n, _ in mapping.STEP_BASE_PAIRS} | {
        n for n, _ in mapping.STEP_SCALAR_PAIRS
    }
    assert mapped <= native_signals
    assert mapped.isdisjoint(mapping.NATIVE_ONLY_STEP)
    assert mapped | mapping.NATIVE_ONLY_STEP == native_signals


def test_step_legacy_totality():
    legacy_vals = _legacy_values(HeadersStepTable)
    mapped = {legacy for _, legacy in mapping.STEP_BASE_PAIRS} | {
        legacy for _, legacy in mapping.STEP_SCALAR_PAIRS
    }
    assert mapped <= legacy_vals
    assert mapped.isdisjoint(mapping.LEGACY_ONLY_STEP)
    assert mapped | mapping.LEGACY_ONLY_STEP == legacy_vals


# --- cycle / summary totality ----------------------------------------------
def test_cycle_native_totality():
    native_vals = _native_values(config.CycleCols)
    mapped = {n for n, _ in mapping.CYCLE_PAIRS}
    assert mapped <= native_vals
    assert mapped.isdisjoint(mapping.NATIVE_ONLY_CYCLE)
    assert mapped | mapping.NATIVE_ONLY_CYCLE == native_vals


def test_cycle_legacy_totality():
    legacy_vals = _legacy_values(HeadersSummary)
    mapped = {legacy for _, legacy in mapping.CYCLE_PAIRS}
    assert mapped <= legacy_vals
    assert mapped.isdisjoint(mapping.LEGACY_ONLY_CYCLE)
    assert mapped | mapping.LEGACY_ONLY_CYCLE == legacy_vals


# --- spot-checks (guard against accidental pair edits) ----------------------
def test_known_translations():
    assert mapping.legacy_to_native_raw() == {
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
    step = mapping.native_to_legacy_step()
    assert step["current_mean"] == "current_avr"
    assert step["potential_first"] == "voltage_first"
    assert step["c_rate"] == "rate_avr"
    summary = mapping.native_to_legacy_summary()
    assert summary["cycle_num"] == "cycle_index"
    assert summary["potential_end_charge"] == "end_voltage_charge"
    assert summary["ir_charge"] == "ir_charge"  # identity pass-through


# --- bridge parity (the bridge must use the authoritative mapping) ----------
def test_bridge_uses_header_mapping():
    core = OldCellpyCellCore(initialize=False)
    legacy_raw_cols = list(_legacy_values(HeadersNormal))
    assert core._legacy_to_native_raw_rename(
        legacy_raw_cols
    ) == mapping.legacy_to_native_raw(legacy_raw_cols)
    assert core._native_to_legacy_step_rename() == mapping.native_to_legacy_step()
    assert core._legacy_to_native_step_rename() == mapping.legacy_to_native_step()
    assert core._native_to_legacy_summary_rename() == mapping.native_to_legacy_summary()
    assert core._legacy_to_native_summary_rename() == mapping.legacy_to_native_summary()


# --- attribute-level mapping + postfix expansion (issue #116) -----------------

import pytest  # noqa: E402

_LEGACY_ATTR_CLASSES = {
    "raw": HeadersNormal,
    "step": HeadersStepTable,
    "cycle": HeadersSummary,
}


def _legacy_attr_names(headers_cls) -> set:
    return {f.name for f in dataclasses.fields(headers_cls)}


def test_legacy_attr_totality():
    """Every legacy attribute is either mapped or documented unmapped."""
    for frame, headers_cls in _LEGACY_ATTR_CLASSES.items():
        mapped = set(mapping.LEGACY_ATTR_TO_SCHEMA[frame])
        unmapped = set(mapping.LEGACY_ATTR_UNMAPPED[frame])
        assert not (mapped & unmapped), f"{frame}: overlap {mapped & unmapped}"
        assert mapped | unmapped == _legacy_attr_names(headers_cls), (
            f"{frame}: attribute set drifted"
        )


def test_legacy_attr_targets_exist_on_native_classes():
    raw_fields = set(config.RawCols.__annotations__)
    cycle_fields = set(config.CycleCols.__annotations__)
    step_bases = {native for native, _ in mapping.STEP_BASE_PAIRS} | {
        native for native, _ in mapping.STEP_SCALAR_PAIRS
    }
    for attr, target in mapping.LEGACY_ATTR_TO_SCHEMA["raw"].items():
        assert target in raw_fields, f"raw.{attr} -> {target} not on RawCols"
    for attr, target in mapping.LEGACY_ATTR_TO_SCHEMA["cycle"].items():
        assert target in cycle_fields, f"cycle.{attr} -> {target} not on CycleCols"
    for attr, target in mapping.LEGACY_ATTR_TO_SCHEMA["step"].items():
        assert target in step_bases, f"step.{attr} -> {target} not a step signal"


def test_legacy_attr_matches_value_mapping():
    """The attribute table agrees with the value-based pair tables."""
    raw_value_map = mapping.legacy_to_native_raw()
    hn = HeadersNormal()
    for attr, target in mapping.LEGACY_ATTR_TO_SCHEMA["raw"].items():
        assert raw_value_map[getattr(hn, attr)] == target, attr

    summary_value_map = mapping.legacy_to_native_summary()
    hs = HeadersSummary()
    for attr, target in mapping.LEGACY_ATTR_TO_SCHEMA["cycle"].items():
        assert summary_value_map[getattr(hs, attr)] == target, attr

    step_base = {legacy: native for native, legacy in mapping.STEP_BASE_PAIRS}
    step_scalar = {legacy: native for native, legacy in mapping.STEP_SCALAR_PAIRS}
    ht = HeadersStepTable()
    for attr, target in mapping.LEGACY_ATTR_TO_SCHEMA["step"].items():
        legacy_value = getattr(ht, attr)
        resolved = step_base.get(legacy_value, step_scalar.get(legacy_value))
        assert resolved == target, attr


def test_duplicate_value_attrs_map_to_same_target():
    for frame, pairs in mapping.DUPLICATE_VALUE_ATTRS.items():
        table = mapping.LEGACY_ATTR_TO_SCHEMA[frame]
        for first, second in pairs:
            assert table[first] == table[second], (first, second)


def test_legacy_attr_to_native_resolves_and_raises():
    assert mapping.legacy_attr_to_native("raw", "voltage_txt") == "potential"
    assert mapping.legacy_attr_to_native("step", "voltage") == "potential"
    assert (
        mapping.legacy_attr_to_native("cycle", "end_voltage_charge")
        == "potential_end_charge"
    )
    with pytest.raises(KeyError, match="legacy-only"):
        mapping.legacy_attr_to_native("raw", "power_txt")
    with pytest.raises(KeyError, match="unknown legacy attribute"):
        mapping.legacy_attr_to_native("raw", "nope")
    with pytest.raises(KeyError, match="unknown frame"):
        mapping.legacy_attr_to_native("bogus", "voltage_txt")


def test_expand_specific_columns_matches_bridge_inline_behavior():
    base = mapping.native_to_legacy_summary()
    out = mapping.expand_specific_columns(
        base,
        ["test_cumulated_charge_capacity", "unmapped_col"],
        ["gravimetric", "areal"],
    )
    # mapped column: legacy name carries the postfix
    assert (
        out["test_cumulated_charge_capacity_gravimetric"]
        == "cumulated_charge_capacity_gravimetric"
    )
    # unmapped column: falls back to the native name
    assert out["unmapped_col_areal"] == "unmapped_col_areal"
    # base entries are preserved and the input is not mutated
    assert out["cycle_num"] == "cycle_index"
    assert "test_cumulated_charge_capacity_gravimetric" not in base
