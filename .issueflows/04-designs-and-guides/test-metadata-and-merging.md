# Test metadata & merging many test files

Durable design note. Captures how `cellpy` / `cellpy-core` should represent **test-level
metadata** so that one object can efficiently hold **many merged test files**. Originated
from a question on the #12 branch (PR #14).

## Problem

A commercial-cell campaign produces many test files (reference-capacity test, rate test,
GITT, …). `cellpy` will merge them into a single object. The current model does **not**
scale to that:

- `Data.meta_test_dependent` is a **single scalar** object per `Data` (e.g. one
  `cycle_mode`). Merging N tests cannot keep N sets of metadata. The
  `# TODO: v2.0 edit this from scalar to list` on `CellpyCellCore.cycle_mode` already
  flags this.
- Native `RawCols` had no compact per-row test key (legacy cellpy carried `test_id`).
- `cycle_num` / `step_num` collide across files, so any per-cycle/per-step aggregation on a
  merged object would silently mix cycles from different tests.

## Decision

**Hybrid model: a compact per-row key in `raw` + a normalized per-test metadata table.**

1. **`raw.test_id`** (added to `harmonized_raw.md` + `RawCols`): a small integer key,
   unique per test within a (possibly merged) object (`0` for a single unmerged test).
   `source_uuid` remains the global/source identity; `test_id` is the cheap grouping key.
2. **A per-test metadata table** (here called `TestMeta`), **one row per `test_id`**, holds
   the test-level descriptors that are constant within a test:
   - `test_family`, `test_type`, `cycle_type` defaults,
   - `cycle_mode`, mass, nominal capacity, areal/volumetric quantities,
   - source file name, `source_uuid`, `source_type`, load timestamp, etc.
   This replaces the scalar `meta_test_dependent` with a keyed collection.
3. **Composite group keys.** All per-cycle / per-step processing groups by
   `(test_id, cycle_num, step_num, sub_step_num, …)`, never `cycle_num` alone. Step/cycle
   tables should therefore also carry `test_id`.

## Why this is efficient

- Merging `raw` = vertical concat; `test_id` is a tiny column (and/or `Categorical`).
- Test-level strings (`test_family`, `test_type`, …) are stored **once per test** in
  `TestMeta`, not repeated on every raw row — O(num_tests) instead of O(num_rows).
- Looking up "which tests are in this object" is just `TestMeta` (no dedup over millions of
  raw rows).
- A row-wise descriptor (when needed) is a cheap join on `test_id`.

### Alternative considered — denormalized per-row columns

Repeat `test_family` / `test_type` / … on every raw row. Works, and in **polars** with
`Categorical` encoding the memory cost is modest, but: no single source of truth for the
test list, dedup needed to read per-test values, and drift risk. Rejected as the primary
model; acceptable only as a convenience projection.

## Status / open points

- `test_id` column: **added** to `harmonized_raw.md` and `config.RawCols` (PR #14).
- `test_family` / `test_type`: currently also present as `raw` columns (added earlier on
  this branch). They are candidates to **move into `TestMeta`** once it exists; keep them in
  `raw` for now to avoid breaking the just-defined spec.
- `TestMeta` class + replacing scalar `meta_test_dependent`, and adding `test_id` to
  `StepCols` / `CycleCols` + composite group keys: **not yet implemented** — needs its own
  issue (ties into the engine rewrite #13 and the UUID/identity strategy in
  `column-headers-review.md` §F).
