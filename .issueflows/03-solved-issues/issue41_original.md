# Issue #41: Per-test metadata: add test_id to StepCols/CycleCols + composite group keys

Source: https://github.com/cellpy/cellpy-core/issues/41

## Original issue text

Forward work from `.issueflows/04-designs-and-guides/test-metadata-and-merging.md` ("Not yet implemented (needs its own issue)"). Enables a single `Data` object to hold many merged test files without silently mixing cycles across tests.

## Scope (cellpy-core)

- Add `test_id` to `config.StepCols` and `config.CycleCols` (it already exists on `RawCols`, `config.py:519`).
- Group all per-step / per-cycle engine aggregation by the composite key `(test_id, cycle_num, step_num, ...)`, never `cycle_num` alone, so merged objects don't collide. Default `test_id = 0` for a single unmerged test (graceful, behaviour-preserving).
- Keep goldens (STEP-06, `tests/test_golden.py`) byte-identical for the single-test fixture; add a synthetic merged-object test proving cross-test isolation.

## Deferred (documented tail, NOT in this issue)

Replacing the scalar `Data.meta_test_dependent` (`cell_core.py:26`, two `# TODO: v2.0` markers at `cell_core.py:115`/`:134`) with the keyed `TestMetaCollection` is the **v2.0 / consumer opt-in** move per `cellpy-core-migration.md` §4. The metadata scaffolding (`cellpycore.metadata`, STEP-10) already exists; this issue only lands the `test_id` plumbing into the table schemas + group keys.

## Anchors

- `test-metadata-and-merging.md` (decision: hybrid compact key + normalized TestMeta table).
- Metadata scaffolding: STEP-10, `metadata-scaffolding.md`.
