# Issue 30 — Status

Add a `cellpycore.metadata` sub-package with scaffolding for test-/cell-level
metadata (typed structures + dummy/stub I/O). Design + scaffolding only; no change
to how the core engine runs today.

- [x] Done

## What landed (2026-06-25)

Implemented per the confirmed `issue30_plan.md`:

- **`src/cellpycore/metadata/models.py`** — `MetaLevel` / `SourceKind` (`StrEnum`),
  `CellMeta` (cell-dependent, mined from legacy `CellpyMetaCommon`), `TestMeta`
  (test-dependent, mirrors the `TestMeta` spec table + `CellpyMetaIndividualTest`,
  keyed by `test_id`, optional `cell` link), and `TestMetaCollection` (keyed
  container with `add`/`get`/`test_ids`/`next_free_id`). `TestMeta` /
  `TestMetaCollection` carry `__test__ = False` to avoid pytest collection.
- **`src/cellpycore/metadata/io.py`** — real stdlib `to_dict`/`from_dict`,
  `to_json`/`from_json`, `merge_test_meta` (renumbers colliding `test_id`s); stubs
  `load_archive`/`save_archive` (HDF5) and `fetch_from_db`/`push_to_db` (DB/API
  JSON-LD) raising `NotImplementedError`.
- **`src/cellpycore/metadata/__init__.py`** — public re-exports.
- **`tests/test_metadata.py`** — 12 tests (bare-record validity, list-default
  isolation, dict/JSON round-trips, unknown-key tolerance, collection keying +
  duplicate guard, merge renumber / no-renumber, stub `NotImplementedError`).
- **`.issueflows/04-designs-and-guides/metadata-scaffolding.md`** — durable design
  note.
- **`docs/data_format_specifications/harmonized_raw.md`** — pointer noting the
  `TestMeta`/`CellMeta` code home (spec stays authoritative for fields).

## Guardrails honoured

- Non-breaking: `Data.meta_test_dependent` scalar and `cycle_mode` untouched; no
  edits to `cell_core.py` / `summarizers.py`. The package is additive.
- No new runtime dependencies (HDF5 / JSON-LD are stubs; stdlib `json` only).
- Degrades gracefully — every field optional; bare `TestMeta()` / `CellMeta()` valid.

## Tests

- `uv run pytest`: **62 passed** (50 prior + 12 new), no warnings.

## Open questions confirmed (defaults accepted)

Both `CellMeta` + `TestMeta`, `NotImplementedError` stubs for HDF5/DB, free-text
vocabularies, 3 modules. All accepted as written in the plan.

## Deferred (not part of this issue)

- `CellMeta` as a separate normalized table vs the optional `TestMeta.cell` link.
- Real HDF5 archive I/O and DB/API (JSON-LD) transport (consumer-owned, e.g. v2.0).
- Wiring `TestMetaCollection` onto `Data` (replacing the scalar `meta_test_dependent`).
