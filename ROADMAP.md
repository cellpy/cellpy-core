# cellpy-core roadmap

Planned features and API additions not yet implemented in the library.

## Test-level summaries

- **`build_tests_summary` / `tests` property** — A helper (or cached property on a
  `CellpyCellCore` subclass) that builds a per-test summary frame from cell data.
  Referenced in the `CellpyCellCore` subclassing example in `cell_core.py`; not
  part of the core API yet. But it should be.

## Merging cell tests

- **Merge many test files into one `Data` object** — Legacy cellpy exposes a method for
  merging cell tests (vertical concat of raw frames, aligned metadata, isolated per-test
  grouping via `test_id`). This can be compute-intensive at scale; cellpy-core should
  own the operation rather than leaving it to callers or the full cellpy package.
  Scaffolding exists (`raw.test_id`, composite group keys in the engine,
  `metadata.merge_test_meta`); a first-class **raw + metadata merge API** on `Data` /
  `CellpyCellCore` is still missing. See
  `.issueflows/04-designs-and-guides/test-metadata-and-merging.md`.

DONE

## Incremental summarization

- **Update step/summary tables from new raw rows only** — Summarizers today reprocess the
  entire `data.raw` frame on every call. For live or in-progress tests (e.g. polling
  cycler status), callers should be able to append new raw data and refresh steps /
  summary incrementally instead of recomputing from scratch. Likely needs defined
  merge/append semantics on `Data`, stable row keys (`test_id`, cycle/step boundaries),
  and incremental paths in `make_step_table` / `make_summary` (or companion helpers).


DONE

## Communication protocols & persistence (open decision)

- **Should core ship out-of-the-box I/O beyond compute?** Today `cellpycore.metadata.io`
  provides stdlib (de)serialization and merge helpers, but deliberately stubs archive
  (`load_archive` / `save_archive`) and remote persistence (`fetch_from_db` /
  `push_to_db`) with `NotImplementedError`. The current boundary (see
  `.issueflows/04-designs-and-guides/metadata-scaffolding.md` and
  `cellpy-core-migration.md` §4) is: **core owns shapes and tools; the consumer owns
  content and heavy persistence.**

  **Open question:** Should cellpy-core grow first-class communication protocols — e.g.
  database interaction models, REST/JSON-LD clients, HDF5 archive adapters — or stay
  lean and expose only typed models + serialization hooks for cellpy (or other apps) to
  wire up?

  **If yes:** define which protocols belong in core (metadata only vs raw/step/summary
  frames too), dependency budget (optional extras?), and whether implementations are
  reference-quality or pluggable interfaces.

  **If no:** document the extension pattern (subclass/protocol + stub replacement) and
  keep all network/DB/archive code in cellpy or downstream packages.
