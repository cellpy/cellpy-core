"""(De)serialization, merging, and persistence scaffolding for metadata.

This is the **Step 2** scaffolding for issue #30. The serialization and merge
helpers are real (stdlib only); the archive (HDF5) and DB/API (JSON-LD) functions
are deliberate **stubs** that raise ``NotImplementedError``.

Rationale (see ``.issueflows/04-designs-and-guides/cellpy-core-migration.md`` §4):
core provides the *shape and the tools* and stays lean and loader-free. Real HDF5
or RDF/JSON-LD persistence would pull in heavy dependencies and policy decisions
that belong to the consumer (e.g. cellpy v2.0); they are stubbed here so the future
suite has a stable surface to build against.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from typing import Type, TypeVar, Union

from cellpycore.metadata.models import (
    CellMeta,
    SourceKind,
    TestMeta,
    TestMetaCollection,
)

Meta = Union[CellMeta, TestMeta]
M = TypeVar("M", CellMeta, TestMeta)


def to_dict(meta: Meta) -> dict:
    """Convert a metadata record to a plain ``dict``.

    Nested ``CellMeta`` (on ``TestMeta.cell``) is converted recursively. Enum
    values are stored as their plain string value so the result is trivially
    JSON-serializable.

    Args:
        meta: A ``CellMeta`` or ``TestMeta`` instance.

    Returns:
        A plain ``dict`` representation.
    """
    return asdict(meta)


def from_dict(cls: Type[M], data: dict) -> M:
    """Reconstruct a metadata record from a ``dict``.

    Unknown keys are ignored so the round-trip is tolerant of extra fields. The
    nested ``cell`` mapping and the ``source_kind`` enum are coerced back to their
    types.

    Args:
        cls: The target class (``CellMeta`` or ``TestMeta``).
        data: A mapping as produced by ``to_dict``.

    Returns:
        An instance of ``cls``.
    """
    field_names = {f.name for f in fields(cls)}
    kwargs = {k: v for k, v in data.items() if k in field_names}

    if cls is TestMeta:
        cell = kwargs.get("cell")
        if isinstance(cell, dict):
            kwargs["cell"] = from_dict(CellMeta, cell)
        source_kind = kwargs.get("source_kind")
        if source_kind is not None:
            kwargs["source_kind"] = SourceKind(source_kind)

    return cls(**kwargs)


def to_json(meta: Meta, *, indent: Union[int, None] = 2) -> str:
    """Serialize a metadata record to a JSON string (stdlib only)."""
    return json.dumps(to_dict(meta), indent=indent)


def from_json(cls: Type[M], text: str) -> M:
    """Deserialize a metadata record from a JSON string produced by ``to_json``."""
    return from_dict(cls, json.loads(text))


def merge_test_meta(
    *collections: TestMetaCollection, renumber: bool = True
) -> TestMetaCollection:
    """Merge several ``TestMetaCollection`` objects into a new one.

    This is the "merge many test files" path: each input collection contributes
    its records, and colliding ``test_id`` keys are resolved by assigning the next
    free id (when ``renumber`` is True). The inputs are left untouched; the merged
    records are shallow copies with their ``test_id`` updated as needed.

    Args:
        *collections: The collections to merge, in priority order (earlier ones
            keep their ``test_id`` on collision; later ones get renumbered).
        renumber: If True (default), reassign colliding ``test_id`` keys. If False,
            raise on a collision.

    Returns:
        A new ``TestMetaCollection`` holding all records.

    Raises:
        KeyError: If ``renumber`` is False and two records share a ``test_id``.
    """
    import dataclasses

    merged = TestMetaCollection()
    for collection in collections:
        for meta in collection:
            if meta.test_id in merged:
                if not renumber:
                    raise KeyError(
                        f"duplicate test_id {meta.test_id} while merging "
                        f"(pass renumber=True to reassign)"
                    )
                meta = dataclasses.replace(meta, test_id=merged.next_free_id())
            merged.add(meta)
    return merged


def load_archive(path) -> TestMetaCollection:
    """Load metadata from a cellpy archive file (HDF5). **Stub.**

    Intended to read the per-test metadata table from a cellpy ``.h5`` archive
    (the format used by legacy cellpy). Not implemented here: HDF5 I/O and the
    archive layout are the consumer's responsibility (e.g. cellpy v2.0), and core
    stays loader-free.

    Args:
        path: Path to the cellpy archive file.

    Raises:
        NotImplementedError: Always; this is scaffolding.
    """
    raise NotImplementedError(
        "HDF5 metadata archive loading is scaffolding for issue #30; the real "
        "loader belongs to the consuming library (e.g. cellpy v2.0)."
    )


def save_archive(meta: Union[TestMeta, TestMetaCollection], path) -> None:
    """Save metadata to a cellpy archive file (HDF5). **Stub.**

    Args:
        meta: The metadata to persist.
        path: Destination archive path.

    Raises:
        NotImplementedError: Always; this is scaffolding.
    """
    raise NotImplementedError(
        "HDF5 metadata archive saving is scaffolding for issue #30; the real "
        "writer belongs to the consuming library (e.g. cellpy v2.0)."
    )


def fetch_from_db(locator: str) -> TestMeta:
    """Fetch test metadata from a database / API. **Stub.**

    Intended to retrieve a test record over a DB connection or an API, most likely
    exchanging JSON-LD (e.g. a node like
    ``{"@context": ..., "@type": "Test", "test_id": 0, ...}``). Not implemented
    here: the transport, auth, and JSON-LD context belong to the consumer.

    Args:
        locator: A DB/API locator (e.g. ``"db://cellpydb/tests/123"``).

    Raises:
        NotImplementedError: Always; this is scaffolding.
    """
    raise NotImplementedError(
        "DB/API (JSON-LD) metadata fetching is scaffolding for issue #30; the "
        "real transport belongs to the consuming library."
    )


def push_to_db(meta: Union[TestMeta, TestMetaCollection], locator: str) -> None:
    """Push test metadata to a database / API (JSON-LD). **Stub.**

    Args:
        meta: The metadata to send.
        locator: A DB/API locator.

    Raises:
        NotImplementedError: Always; this is scaffolding.
    """
    raise NotImplementedError(
        "DB/API (JSON-LD) metadata pushing is scaffolding for issue #30; the real "
        "transport belongs to the consuming library."
    )
