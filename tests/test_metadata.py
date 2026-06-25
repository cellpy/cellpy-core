"""Tests for the metadata scaffolding (issue #30)."""

import pytest

from cellpycore.metadata import (
    CellMeta,
    SourceKind,
    TestMeta,
    TestMetaCollection,
    fetch_from_db,
    from_dict,
    from_json,
    load_archive,
    merge_test_meta,
    push_to_db,
    save_archive,
    to_dict,
    to_json,
)


def test_bare_records_are_valid():
    """Core must degrade gracefully: empty metadata records are valid."""
    cell = CellMeta()
    meta = TestMeta()
    assert cell.mass is None
    assert meta.test_id == 0
    assert meta.raw_file_names == []
    assert meta.cell is None


def test_raw_file_names_are_independent_per_instance():
    """The list default must not be shared between instances."""
    a = TestMeta()
    b = TestMeta()
    a.raw_file_names.append("run1.ndax")
    assert b.raw_file_names == []


def test_dict_round_trip_preserves_values():
    meta = TestMeta(
        test_id=2,
        cell_name="cell_001",
        source_kind=SourceKind.FILE,
        raw_file_names=["run1.ndax"],
        cell=CellMeta(mass=1.23, nom_cap=3.5),
    )
    restored = from_dict(TestMeta, to_dict(meta))
    assert restored == meta
    assert isinstance(restored.cell, CellMeta)
    assert restored.source_kind is SourceKind.FILE


def test_json_round_trip_preserves_values():
    meta = TestMeta(
        test_id=1,
        source_kind=SourceKind.DB,
        cell=CellMeta(material="graphite"),
    )
    restored = from_json(TestMeta, to_json(meta))
    assert restored == meta


def test_from_dict_ignores_unknown_keys():
    restored = from_dict(TestMeta, {"test_id": 5, "not_a_field": "x"})
    assert restored.test_id == 5


def test_collection_keying_and_duplicate_guard():
    coll = TestMetaCollection()
    coll.add(TestMeta(test_id=0))
    coll.add(TestMeta(test_id=1))
    assert len(coll) == 2
    assert coll.test_ids == [0, 1]
    assert 0 in coll
    assert coll.get(1).test_id == 1
    with pytest.raises(KeyError):
        coll.add(TestMeta(test_id=0))
    coll.add(TestMeta(test_id=0, cell_name="replaced"), replace=True)
    assert coll.get(0).cell_name == "replaced"


def test_merge_renumbers_colliding_ids():
    a = TestMetaCollection()
    a.add(TestMeta(test_id=0, cell_name="a0"))
    b = TestMetaCollection()
    b.add(TestMeta(test_id=0, cell_name="b0"))

    merged = merge_test_meta(a, b)
    assert len(merged) == 2
    assert merged.test_ids == [0, 1]
    # earlier collection keeps id 0; later one is renumbered to 1
    assert merged.get(0).cell_name == "a0"
    assert merged.get(1).cell_name == "b0"
    # inputs are untouched
    assert b.get(0).test_id == 0


def test_merge_without_renumber_raises_on_collision():
    a = TestMetaCollection()
    a.add(TestMeta(test_id=0))
    b = TestMetaCollection()
    b.add(TestMeta(test_id=0))
    with pytest.raises(KeyError):
        merge_test_meta(a, b, renumber=False)


@pytest.mark.parametrize(
    "call",
    [
        lambda: load_archive("x.h5"),
        lambda: save_archive(TestMeta(), "x.h5"),
        lambda: fetch_from_db("db://x/tests/1"),
        lambda: push_to_db(TestMeta(), "db://x/tests/1"),
    ],
)
def test_persistence_stubs_raise_not_implemented(call):
    with pytest.raises(NotImplementedError):
        call()
