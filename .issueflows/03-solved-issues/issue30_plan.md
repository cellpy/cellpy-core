# Plan for issue #30: module for handling meta data

## Goal

Add a new `cellpycore.metadata` sub-package that provides the **scaffolding** for
test-/cell-level metadata: typed data structures (Step 1) plus dummy/stub functions for
(de)serialization, archive load/save, and DB/API exchange (Step 2). This is design +
scaffolding only — **not** a final implementation, and it must not change how the core
engine runs today.

## Constraints

- **Honour the metadata boundary** (`.issueflows/04-designs-and-guides/cellpy-core-migration.md`
  §4): core owns the *shape and the tools* (schemas, dataclasses, (de)serialization, merge
  helpers, `test_id` plumbing). Core must **not require populated metadata** on `Data`, and
  must keep working when metadata is absent. Attaching real metadata to `Data` stays a v2.0
  / upstream opt-in.
- **Non-breaking.** Leave `Data.meta_test_dependent` (the `legacy.MockMetaTestDependent`
  scalar) and the `CellpyCellCore.cycle_mode` property untouched. The new package is
  standalone scaffolding; the scalar→keyed move on `Data` is explicitly a later (v2.0)
  concern (`cell_core.py:113-141`, `test-metadata-and-merging.md`). No edits to
  `cell_core.py` / `summarizers.py` in this issue.
- **Stay lean / loader-free.** No new runtime dependencies. HDF5 archive and DB/API
  (JSON-LD) functions are **stubs** (raise `NotImplementedError` with a clear message);
  only stdlib `json` is used for the dict/JSON round-trip. Pulling in `h5py`/`pytables`/an
  RDF lib is deferred to whoever implements real persistence.
- Follow project conventions: Google-style docstrings, `StrEnum` + `@dataclass` mirroring
  `config.py`, thread-safe (pure data + pure functions, no shared mutable module state).
- Align field names with the existing **TestMeta spec** in
  `docs/data_format_specifications/harmonized_raw.md` (the authoritative field list).

### Prior art

- `legacy.Meta` / `legacy.MockMetaTestDependent` (`src/cellpycore/legacy.py:236-242`) —
  convention: the current placeholder scalar hung off `Data.meta_test_dependent`. New work:
  **coexist** (leave it as-is; the new package does not replace it this issue).
- `config.RawCols.test_id` (`src/cellpycore/config.py:514`) — convention: compact per-row
  grouping key, `0` for a single unmerged test. New work: `TestMeta.test_id` **mirrors** it
  (one `TestMeta` record per `test_id`); a `TestMetaCollection` is keyed by it.
- TestMeta spec table (`docs/data_format_specifications/harmonized_raw.md:91-131`) —
  convention: authoritative field set + types/units. New work: `TestMeta` dataclass mirrors
  these fields field-for-field.
- Old cellpy `CellpyMetaCommon` (cell/material/geometry) + `CellpyMetaIndividualTest`
  (`cellpy/cellpy/parameters/internal_settings.py:136-222`) — convention: existing
  cell-vs-test metadata split with `update`/`digest`/`to_frame` helpers. New work: **mine**
  field names for `CellMeta` (cell-dependent) and `TestMeta` (test-dependent); reimplement
  clean dataclasses in core rather than importing cellpy (core must not depend on cellpy).
- `config.StepType` / `CycleType` / `StepMode` `StrEnum`s (`config.py:78-196`) — convention:
  non-validating reference vocabularies. New work: `SourceKind` (`file`/`db`/`api`) and a
  `MetaLevel` enum **mirror** that style.

## Approach

Two metadata levels, two dataclasses, keyed collection, stub I/O:

1. **Data structures (Step 1)** — `metadata/models.py`:
   - `MetaLevel(StrEnum)` = `CELL` / `TEST`; `SourceKind(StrEnum)` = `FILE` / `DB` / `API`.
   - `@dataclass CellMeta` — **cell-dependent** (constant across tests on the same cell):
     mass, tot_mass, nom_cap, nom_cap_specifics, material, active-electrode area/loading/
     thickness, electrolyte/electrode/separator types, cell_type, experiment_type, ...
     (mined from `CellpyMetaCommon`). All fields `Optional`, default `None`.
   - `@dataclass TestMeta` — **test-dependent** (one per `test_id`): the spec fields
     (`test_id`, `uuid`, `cell_name`, `test_family`, `test_type`, `cycle_mode`,
     `source_kind`, `source_type`, `source_uri`, `source_uuid`, `raw_file_names`,
     `schedule_file_name`, `creator`, `channel`, `tester_id`, `start_datetime`, `time_zone`,
     `loaded_datetime`, `comment`) + an optional `cell: Optional[CellMeta]` reference so the
     cell/test split is captured without forcing a separate table. `test_id: int = 0`.
   - `@dataclass TestMetaCollection` — a thin keyed container (`dict[int, TestMeta]`) for the
     "many merged test files" case: `add`, `get`, `__iter__`, `__len__`, `test_ids`.
2. **Dummy functions (Step 2)** — `metadata/io.py`:
   - `to_dict(meta)` / `from_dict(cls, d)` — working stdlib round-trip (`dataclasses.asdict`
     + reconstruction); used by everything else.
   - `to_json(meta)` / `from_json(cls, s)` — working stdlib `json` round-trip.
   - `merge_test_meta(collection, others, *, renumber=True)` — combine collections keyed by
     `test_id`, reassigning ids on collision (the merging story from
     `test-metadata-and-merging.md`).
   - `load_archive(path)` / `save_archive(meta, path)` — **stubs** (HDF5 cellpy archive):
     `raise NotImplementedError("HDF5 metadata archive I/O is scaffolding ...")`.
   - `fetch_from_db(locator)` / `push_to_db(meta, locator)` — **stubs** (DB/API, JSON-LD):
     `raise NotImplementedError("DB/API (JSON-LD) metadata exchange is scaffolding ...")`,
     with a docstring sketch of the intended JSON-LD shape.
3. **Public surface** — `metadata/__init__.py` re-exports the dataclasses, enums, and the
   serialization/merge/stub functions so consumers do `from cellpycore.metadata import
   TestMeta, CellMeta, ...`.

## Files to touch

- `src/cellpycore/metadata/__init__.py` — new; public exports + module docstring.
- `src/cellpycore/metadata/models.py` — new; enums + `CellMeta` / `TestMeta` /
  `TestMetaCollection`.
- `src/cellpycore/metadata/io.py` — new; serialize/deserialize + merge helpers + HDF5 and
  DB/API stubs.
- `tests/test_metadata.py` — new; round-trip, merge, and stub-raises tests.
- `.issueflows/04-designs-and-guides/metadata-scaffolding.md` — new; short durable design
  note (two-level model, boundary decision, what is real vs stub, deferred questions). Links
  back to `test-metadata-and-merging.md` and this issue.
- `docs/data_format_specifications/harmonized_raw.md` — small note that `TestMeta`/`CellMeta`
  now have a code home in `cellpycore.metadata` (spec stays authoritative for fields).

## Test strategy

- New `tests/test_metadata.py` (run with `uv run pytest` or `pytest` in the activated env):
  - `TestMeta` / `CellMeta` construct with all-default (no required population) — the
    "degrade gracefully" guard.
  - `to_dict`/`from_dict` and `to_json`/`from_json` round-trip preserves values (incl. the
    nested `cell`).
  - `TestMetaCollection` keying + `merge_test_meta` renumbers colliding `test_id`s.
  - `load_archive` / `save_archive` / `fetch_from_db` / `push_to_db` raise
    `NotImplementedError`.
- Re-run the full suite to confirm nothing else moved (the package is additive).

## Open questions

1. **CellMeta split.** The spec defers whether cell/material fields live in `TestMeta` or a
   sibling `CellMeta` (`harmonized_raw.md:124-131`). Plan proposes **both** dataclasses with
   `TestMeta.cell` as an optional link. OK, or fold everything into `TestMeta` for now?
2. **Stub depth for HDF5 / DB.** Plan keeps these as `NotImplementedError` stubs (no new
   deps). Acceptable, or do you want a minimal working JSON-file `save_archive`/`load_archive`
   (no HDF5) so there is *some* real persistence to exercise?
3. **Controlled vocabularies.** `test_family` / `test_type` / `source_type` kept as free-text
   `str` for now (consistent with the deferred-vocabulary decisions in the spec). Agree?
4. **Module split granularity.** 3 modules (`models` / `io` / `__init__`). Fine, or prefer a
   flatter single `metadata.py`? (Issue explicitly asks for a *package* folder, so a folder
   it is; this is just about how many files inside.)
