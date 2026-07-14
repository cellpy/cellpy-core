"""Totality / round-trip tests for the legacy ⇄ core metadata field mapping.

Same discipline as ``tests/test_header_mapping.py``: every legacy field is
either mapped or listed in a documented exception, every core field is either a
mapping target or listed core-only — adding a field on either side fails these
tests until it is deliberately categorized. The legacy inventories are pinned
in the module (core cannot import cellpy); cellpy's contract tests guard the
pins against the real legacy dataclasses.
"""

import dataclasses

import pytest

from cellpycore.legacy import meta_mapping
from cellpycore.metadata.models import CellMeta, TestMeta


def _core_field_names(model_cls) -> set:
    return {f.name for f in dataclasses.fields(model_cls)}


# --- totality -----------------------------------------------------------------
def test_legacy_common_totality():
    mapped = {legacy for legacy, _ in meta_mapping.COMMON_TO_CELL_PAIRS} | {
        legacy for legacy, _ in meta_mapping.COMMON_TO_TEST_PAIRS
    }
    legacy_only = set(meta_mapping.LEGACY_ONLY)
    assert not (mapped & legacy_only)
    assert mapped | legacy_only == meta_mapping.LEGACY_COMMON_FIELDS


def test_legacy_individual_totality():
    mapped = {legacy for legacy, _ in meta_mapping.INDIVIDUAL_TO_TEST_PAIRS}
    assert mapped == meta_mapping.LEGACY_INDIVIDUAL_FIELDS


def test_cell_meta_totality():
    targets = {core for _, core in meta_mapping.COMMON_TO_CELL_PAIRS}
    assert not (targets & meta_mapping.CORE_ONLY_CELL)
    assert targets | meta_mapping.CORE_ONLY_CELL == _core_field_names(CellMeta)


def test_test_meta_totality():
    targets = {core for _, core in meta_mapping.COMMON_TO_TEST_PAIRS} | {
        core for _, core in meta_mapping.INDIVIDUAL_TO_TEST_PAIRS
    }
    assert not (targets & meta_mapping.CORE_ONLY_TEST)
    assert targets | meta_mapping.CORE_ONLY_TEST == _core_field_names(TestMeta)


def test_no_target_collisions_between_common_and_individual():
    common_targets = {core for _, core in meta_mapping.COMMON_TO_TEST_PAIRS}
    individual_targets = {core for _, core in meta_mapping.INDIVIDUAL_TO_TEST_PAIRS}
    assert not (common_targets & individual_targets)


def test_pair_tables_bijective():
    for pairs in (
        meta_mapping.COMMON_TO_CELL_PAIRS,
        meta_mapping.COMMON_TO_TEST_PAIRS,
        meta_mapping.INDIVIDUAL_TO_TEST_PAIRS,
    ):
        legacy_side = [legacy for legacy, _ in pairs]
        core_side = [core for _, core in pairs]
        assert len(set(legacy_side)) == len(legacy_side)
        assert len(set(core_side)) == len(core_side)


def test_legacy_only_destinations_documented():
    for legacy_field, destination in meta_mapping.LEGACY_ONLY.items():
        assert destination, f"{legacy_field} needs a documented destination"


# --- coerce_test_id ------------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, 0),
        (3, 3),
        ("7", 7),
        (2.0, 2),
        ([4, 9], 4),
        ((5,), 5),
        ([], 0),
    ],
)
def test_coerce_test_id(value, expected):
    assert meta_mapping.coerce_test_id(value) == expected


def test_coerce_test_id_default():
    assert meta_mapping.coerce_test_id(None, default=42) == 42


@pytest.mark.parametrize("bad", ["banana", object(), [None], True])
def test_coerce_test_id_rejects_uninterpretable(bad):
    with pytest.raises(ValueError, match="test_ID"):
        meta_mapping.coerce_test_id(bad)


# --- legacy_meta_to_core ---------------------------------------------------------
def test_legacy_meta_to_core_translates_and_rehomes():
    common = {
        "material": "silicon",
        "mass": 2.5,
        "comment": "hello",
        # re-homed fields (legacy filed these under "common"):
        "cell_name": "cell_01",
        "start_datetime": "2026-07-14T12:00:00",
        "time_zone": "Europe/Oslo",
        "tester_ID": "arbin-42",
        "tester_calibration_date": "2026-01-01",
        # legacy-only (must be ignored):
        "raw_id": "abc",
        "cellpy_file_version": 8,
        "file_errors": None,
    }
    individual = {
        "channel_index": "3",
        "creator": "jepe",
        "schedule_file_name": "protocol.sdu",
        "test_type": "cycling",
        "voltage_lim_low": 0.05,
        "voltage_lim_high": 1.0,
        "cycle_mode": "anode",
        "test_ID": [2, 5],
    }
    cell, test = meta_mapping.legacy_meta_to_core(common, individual)

    assert cell.material == "silicon"
    assert cell.mass == 2.5
    assert cell.comment == "hello"
    assert cell.volume is None  # core-only, never filled from legacy

    assert test.cell_name == "cell_01"
    assert test.start_datetime == "2026-07-14T12:00:00"
    assert test.time_zone == "Europe/Oslo"
    assert test.tester_id == "arbin-42"
    assert test.tester_calibration_date == "2026-01-01"
    assert test.channel == "3"
    assert test.creator == "jepe"
    assert test.schedule_file_name == "protocol.sdu"
    assert test.test_type == "cycling"
    assert test.voltage_lim_low == 0.05
    assert test.voltage_lim_high == 1.0
    assert test.cycle_mode == "anode"
    assert test.test_id == 2  # first of the legacy list

    # provenance stays untouched (framework's job, not the mapping's)
    assert test.uuid is None
    assert test.source_uri is None
    assert test.cell is None


def test_legacy_meta_to_core_accepts_attribute_objects_and_none():
    class LegacyCommon:
        material = "graphite"
        mass = 1.0
        cell_name = "c2"

    cell, test = meta_mapping.legacy_meta_to_core(LegacyCommon(), None)
    assert cell.material == "graphite"
    assert cell.mass == 1.0
    assert test.cell_name == "c2"
    assert test.test_id == 0

    cell_empty, test_empty = meta_mapping.legacy_meta_to_core(None, None)
    assert cell_empty == CellMeta()
    assert test_empty == TestMeta()
