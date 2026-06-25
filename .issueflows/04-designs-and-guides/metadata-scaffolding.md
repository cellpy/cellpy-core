# Metadata scaffolding (`cellpycore.metadata`)

Durable design note for the metadata sub-package added in issue
[#30](https://github.com/cellpy/cellpy-core/issues/30). Companion to
[`test-metadata-and-merging.md`](test-metadata-and-merging.md) (the merging model) and
[`cellpy-core-migration.md`](cellpy-core-migration.md) §4 (the metadata boundary).

## Context

cellpy-core needed a home for test/cell metadata *structures and tooling* without taking on
metadata *population* or heavy persistence dependencies. The boundary rule: **core owns the
shape and the tools; the consumer (e.g. cellpy v2.0) owns the content and persistence.**

## Decision

A `cellpycore.metadata` sub-package with three modules:

- `models.py` — typed data structures:
  - `MetaLevel` / `SourceKind` (`StrEnum`, non-validating reference vocabularies).
  - `CellMeta` — **cell-dependent** metadata (mined from legacy `CellpyMetaCommon`).
  - `TestMeta` — **test-dependent** metadata, one record per `test_id`, mirroring the
    `TestMeta` spec table in `docs/data_format_specifications/harmonized_raw.md`. Carries an
    optional `cell: CellMeta` link.
  - `TestMetaCollection` — keyed (`dict[int, TestMeta]`) container for a merged object.
- `io.py` — Step-2 functions:
  - **Real (stdlib only):** `to_dict`/`from_dict`, `to_json`/`from_json`, `merge_test_meta`.
  - **Stubs (`NotImplementedError`):** `load_archive`/`save_archive` (HDF5),
    `fetch_from_db`/`push_to_db` (DB/API, JSON-LD).
- `__init__.py` — public re-exports.

Guardrails honoured:

- **Non-breaking / additive.** `Data.meta_test_dependent` (the `legacy.MockMetaTestDependent`
  scalar) and `CellpyCellCore.cycle_mode` are untouched. The scalar→keyed move on `Data`
  stays a v2.0 concern. Core does not import or require this package on the hot path.
- **Lean / loader-free.** No new runtime dependencies; HDF5 + JSON-LD are stubbed.
- **Degrades gracefully.** Every field is optional; a bare `TestMeta()` / `CellMeta()` is
  valid.

## Alternatives considered

- **Fold cell fields into `TestMeta`** (no separate `CellMeta`). Rejected for now: the
  cell-vs-test split is real (one cell, many tests) and matches legacy cellpy's
  `CellpyMetaCommon` / `CellpyMetaIndividualTest`. Kept as an optional `TestMeta.cell` link
  rather than a separate normalized table (that normalization is deferred).
- **Real JSON-file persistence for `save/load_archive`.** Rejected: the archive format is
  HDF5 and owned by the consumer; a half-real JSON path would be misleading. Stubs make the
  "not yet implemented" boundary explicit.
- **Denormalized per-row metadata columns.** Already rejected in
  `test-metadata-and-merging.md`; this package is the normalized alternative.

## Deferred / open

- `CellMeta` as a separate normalized table vs the current optional `TestMeta.cell` link.
- Controlled vocabularies for `test_family` / `test_type` / `source_type` (free text today).
- Real HDF5 archive I/O and DB/API (JSON-LD) transport — owned by the consumer.
- Wiring a `TestMetaCollection` onto `Data` (replacing the scalar `meta_test_dependent`) —
  a v2.0 concern, tracked with the engine/merging work.
