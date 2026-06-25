"""Metadata scaffolding for cellpy-core (issue #30).

This sub-package provides the *shape and tools* for test-/cell-level metadata,
without requiring that metadata be populated on the core ``Data`` object. See
``.issueflows/04-designs-and-guides/metadata-scaffolding.md`` for the design and
``docs/data_format_specifications/harmonized_raw.md`` for the authoritative field
list.

Two levels of metadata:

- ``CellMeta`` — cell-dependent (constant for a physical cell across tests).
- ``TestMeta`` — test-dependent (one record per test run, keyed by ``test_id``).

``TestMetaCollection`` holds many ``TestMeta`` records for a merged object. The
``io`` helpers give a working stdlib (de)serialization + merge surface; the HDF5
archive and DB/API (JSON-LD) functions are deliberate stubs.

Example:
    >>> from cellpycore.metadata import TestMeta, to_json, from_json
    >>> meta = TestMeta(test_id=0, cell_name="cell_001")
    >>> from_json(TestMeta, to_json(meta)) == meta
    True
"""

from cellpycore.metadata.models import (
    CellMeta,
    MetaLevel,
    SourceKind,
    TestMeta,
    TestMetaCollection,
)
from cellpycore.metadata.io import (
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

__all__ = [
    "CellMeta",
    "MetaLevel",
    "SourceKind",
    "TestMeta",
    "TestMetaCollection",
    "to_dict",
    "from_dict",
    "to_json",
    "from_json",
    "merge_test_meta",
    "load_archive",
    "save_archive",
    "fetch_from_db",
    "push_to_db",
]
