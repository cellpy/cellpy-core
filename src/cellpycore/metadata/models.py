"""Typed data structures for cellpy-core test/cell metadata (scaffolding).

This module defines the *shape* of the metadata that cellpy-core understands. It
follows the metadata-boundary decision in
``.issueflows/04-designs-and-guides/cellpy-core-migration.md`` (§4): core owns the
schema and tooling, but never *requires* that metadata be populated. Every field
defaults to an empty / ``None`` value so a bare ``TestMeta()`` or ``CellMeta()`` is
valid, and the core summary/step engine keeps working when no metadata is attached.

There are two levels of metadata (see issue #30 and
``.issueflows/04-designs-and-guides/test-metadata-and-merging.md``):

- **cell-dependent** (`CellMeta`): constant for a physical cell across tests
  (masses, nominal capacity, geometry, electrode / electrolyte types, ...).
- **test-dependent** (`TestMeta`): one record per test run, keyed by ``test_id``
  (the same compact key carried on every harmonized-raw row, see
  ``cellpycore.config.RawCols.test_id``). A single (possibly merged) object holds
  many tests via a ``TestMetaCollection`` keyed by ``test_id``.

The authoritative field list lives in
``docs/data_format_specifications/harmonized_raw.md`` ("Test metadata (TestMeta)");
the dataclasses here mirror it. Field names are also mined from legacy cellpy's
``cellpy.parameters.internal_settings.CellpyMetaCommon`` /
``CellpyMetaIndividualTest`` so the two libraries stay aligned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional


class MetaLevel(StrEnum):
    """The level a piece of metadata applies to.

    Attributes:
        CELL: Cell-dependent metadata (constant across tests on the same cell).
        TEST: Test-dependent metadata (one record per test run).
    """

    CELL = "cell"
    TEST = "test"


class SourceKind(StrEnum):
    """Where the test data was obtained from.

    This is a non-validating reference vocabulary (mirroring the style of the
    ``config`` enums): other values are still allowed by the free-text fields,
    but these cover the expected sources.

    Attributes:
        FILE: Loaded from a raw data file on disk.
        DB: Read from a database.
        API: Fetched through an API (e.g. JSON-LD).
    """

    FILE = "file"
    DB = "db"
    API = "api"


@dataclass
class CellMeta:
    """Cell-dependent metadata (constant for a physical cell across tests).

    Mined from legacy ``cellpy.parameters.internal_settings.CellpyMetaCommon``
    (cell / material / geometry fields). All fields are optional; an empty
    ``CellMeta()`` is valid scaffolding and carries no obligation to be populated.

    Attributes:
        material: Active-material name / identifier.
        mass: Active-material mass.
        tot_mass: Total material mass.
        nom_cap: Nominal capacity.
        nom_cap_specifics: How ``nom_cap`` is specified (e.g. gravimetric).
        active_electrode_area: Active-electrode area.
        active_electrode_thickness: Active-electrode thickness.
        active_electrode_loading: Active-electrode loading (e.g. mAh/cm2).
        electrolyte_volume: Electrolyte volume.
        electrolyte_type: Electrolyte type.
        active_electrode_type: Active-electrode type.
        counter_electrode_type: Counter-electrode type.
        reference_electrode_type: Reference-electrode type.
        separator_type: Separator type.
        cell_type: Cell type / format.
        experiment_type: Experiment type.
        active_electrode_current_collector: Active-electrode current collector.
        reference_electrode_current_collector: Reference-electrode current
            collector.
        comment: Free-text comment.
    """

    material: Optional[str] = None
    mass: Optional[float] = None
    tot_mass: Optional[float] = None
    nom_cap: Optional[float] = None
    nom_cap_specifics: Optional[str] = None
    active_electrode_area: Optional[float] = None
    active_electrode_thickness: Optional[float] = None
    active_electrode_loading: Optional[float] = None
    electrolyte_volume: Optional[float] = None
    electrolyte_type: Optional[str] = None
    active_electrode_type: Optional[str] = None
    counter_electrode_type: Optional[str] = None
    reference_electrode_type: Optional[str] = None
    separator_type: Optional[str] = None
    cell_type: Optional[str] = None
    experiment_type: Optional[str] = None
    active_electrode_current_collector: Optional[str] = None
    reference_electrode_current_collector: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class TestMeta:
    """Test-dependent metadata, one record per test run (keyed by ``test_id``).

    Mirrors the "Test metadata (TestMeta)" table in
    ``docs/data_format_specifications/harmonized_raw.md`` and the test-dependent
    fields of legacy ``CellpyMetaIndividualTest``. ``cell`` optionally links the
    cell-dependent metadata so the two-level split is captured without forcing a
    separate table.

    All fields are optional (``test_id`` defaults to ``0``, the single-unmerged-test
    convention), so a bare ``TestMeta()`` is valid scaffolding.

    Attributes:
        test_id: Compact per-test grouping key; matches ``raw.test_id``. ``0`` for
            a single, unmerged test.
        uuid: Stable, globally-unique id for this test run.
        cell_name: Human-readable cell / test name.
        test_family: Broad classification of the overall test (free text).
        test_type: Detailed classification within a family (free text).
        cycle_mode: ``"anode"`` / ``"cathode"`` / ``"full"``.
        source_kind: Where the data came from (see ``SourceKind``).
        source_type: Cycler / instrument type (e.g. ``"Neware"``).
        source_uri: File path or DB/API locator for the source.
        source_uuid: Original identifier from the source; matches ``raw.source_uuid``.
        raw_file_names: Original raw file(s) backing this test.
        schedule_file_name: Cycler schedule / protocol file.
        creator: Who produced / imported the test.
        channel: Tester channel id.
        tester_id: Tester / server identity.
        voltage_lim_low: Lower voltage limit used for the test.
        voltage_lim_high: Upper voltage limit used for the test.
        start_datetime: Test start time (ISO 8601 string).
        time_zone: Time zone for naive timestamps.
        loaded_datetime: When the data was imported (ISO 8601 string).
        comment: Free text.
        cell: Optional cell-dependent metadata for this test.
    """

    # Named ``TestMeta`` to match the spec, but it is data, not a pytest case;
    # this flag stops pytest from trying to collect it as a test class.
    __test__ = False

    test_id: int = 0
    uuid: Optional[str] = None
    cell_name: Optional[str] = None
    test_family: Optional[str] = None
    test_type: Optional[str] = None
    cycle_mode: Optional[str] = None
    source_kind: Optional[SourceKind] = None
    source_type: Optional[str] = None
    source_uri: Optional[str] = None
    source_uuid: Optional[str] = None
    raw_file_names: list[str] = field(default_factory=list)
    schedule_file_name: Optional[str] = None
    creator: Optional[str] = None
    channel: Optional[str] = None
    tester_id: Optional[str] = None
    voltage_lim_low: Optional[float] = None
    voltage_lim_high: Optional[float] = None
    start_datetime: Optional[str] = None
    time_zone: Optional[str] = None
    loaded_datetime: Optional[str] = None
    comment: Optional[str] = None
    cell: Optional[CellMeta] = None


@dataclass
class TestMetaCollection:
    """A keyed collection of ``TestMeta`` records (one per ``test_id``).

    This is the "many merged test files" container: merging raw data is a vertical
    concat on a tiny ``test_id`` column, and the test-level descriptors are stored
    once per test here instead of being repeated on every raw row.

    Attributes:
        records: Mapping of ``test_id`` to its ``TestMeta`` record.
    """

    __test__ = False

    records: dict[int, TestMeta] = field(default_factory=dict)

    def add(self, meta: TestMeta, *, replace: bool = False) -> None:
        """Add a record, keyed by its ``test_id``.

        Args:
            meta: The record to add.
            replace: If ``False`` (default), raise on a duplicate ``test_id``.
                If ``True``, overwrite the existing record.

        Raises:
            KeyError: If ``meta.test_id`` already exists and ``replace`` is False.
        """
        if not replace and meta.test_id in self.records:
            raise KeyError(f"test_id {meta.test_id} already present")
        self.records[meta.test_id] = meta

    def get(self, test_id: int) -> Optional[TestMeta]:
        """Return the record for ``test_id`` (or ``None`` if absent)."""
        return self.records.get(test_id)

    @property
    def test_ids(self) -> list[int]:
        """The sorted ``test_id`` keys currently held."""
        return sorted(self.records)

    def next_free_id(self) -> int:
        """Return the smallest non-negative ``test_id`` not yet used."""
        existing = set(self.records)
        candidate = 0
        while candidate in existing:
            candidate += 1
        return candidate

    def __iter__(self):
        return iter(self.records.values())

    def __len__(self) -> int:
        return len(self.records)

    def __contains__(self, test_id: object) -> bool:
        return test_id in self.records
