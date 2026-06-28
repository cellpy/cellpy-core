# Issue #39 plan: finalize cellpy-core integration roadmap

Source issue: https://github.com/cellpy/cellpy-core/issues/39

## Goal

Close out the roadmap planning: review the integration roadmap, capture the remaining
gaps as a finalized durable record in the roadmap doc, and open a focused, ranked set of
**cellpy-core** GitHub issues for the leftover work. cellpy-side work stays tracked on
jepegit/cellpy.

## Gap analysis

Roadmap (`.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md`) has 12
steps, 10 done. Not closed: STEP-06 (golden fixtures, continuous) and STEP-12 (unit
boundary, partly). Forward work that existed in the design docs but was not tracked as an
open cellpy-core issue:

- **STEP-12 core side** — `CellpyUnits` still lives in `legacy.py`, not a first-class
  unit-spec module; converter-parity / pint-optional guard tests not pinned. (cellpy's
  duplicate converters are cellpy-side, out of scope.)
- **Per-test metadata wiring** (`test-metadata-and-merging.md`) — `test_id` is on
  `RawCols` but not `StepCols`/`CycleCols`; engine groups by `cycle_num` not
  `(test_id, cycle_num, step_num)`; scalar `meta_test_dependent` (`cell_core.py:26`,
  `# TODO: v2.0` at `:115`/`:134`) not yet keyed to `TestMetaCollection`.
- **Reset-granularity normalization** — accept step-/test-cumulative raw from other cyclers
  (deferred in `step-table-polars-migration.md`).
- **`ref_potential`/`ref_voltage`** native `RawCols` gap (deferred; absent in golden data).
- **Selector dead-code removal** — `create_selector`/`summary_selector_exluder`, gated on
  cellpy migrating off them (`selector-dead-code-deferral.md`).
- **Release path** — tag/publish cellpy-core so cellpy can pin a release ref instead of
  `@main`.
- **Doc nit** — "Implementation Flow" placeholder text was stale (a mermaid diagram
  already existed).

## Decisions

- New issues target **cellpy-core only**; cellpy-side delegation stays on jepegit/cellpy.
- **Update the roadmap doc itself** as the durable finalized record, then create issues
  from it.
- Issue set: created the full ranked set (A–F).
- Issue B keeps the scalar→keyed `meta_test_dependent` replacement as a documented v2.0
  deferral; only lands `test_id` on the table schemas + composite group keys.
- No milestone/labels attached (none exist on #39).

## Issues created (final list)

| Item | Issue | Status |
|------|-------|--------|
| Finalize STEP-12 (core): promote `CellpyUnits` to a unit-spec module + converter-parity / pint-optional tests | [#40](https://github.com/cellpy/cellpy-core/issues/40) | actionable |
| Per-test metadata: add `test_id` to `StepCols`/`CycleCols` + composite group keys | [#41](https://github.com/cellpy/cellpy-core/issues/41) | actionable |
| Engine: reset-granularity normalization for cumulative raw inputs | [#42](https://github.com/cellpy/cellpy-core/issues/42) | future |
| Native schema: add `ref_potential`/`ref_voltage` support | [#43](https://github.com/cellpy/cellpy-core/issues/43) | future |
| Release: tag cellpy-core (and decide PyPI publish) | [#44](https://github.com/cellpy/cellpy-core/issues/44) | future |
| Cleanup: remove `create_selector`/`summary_selector_exluder` once cellpy migrates off | [#45](https://github.com/cellpy/cellpy-core/issues/45) | blocked |

Not created: STEP-06 golden-fixture oracle (continuous activity, extended per-port).

## Files touched

- `.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md` — fixed the stale
  Implementation Flow placeholder; added the "Remaining work (STEP-13+)" section with
  design-doc anchors and issue numbers #40–#45; refreshed the status-at-a-glance note.
- `.issueflows/01-current-issues/issue39_plan.md` — this file.

No source/code edits (this is a planning/meta issue).

## Test strategy

No code change in #39 itself, so no test run required. Each spawned issue carries its own
test criteria (parity tests via `uv run pytest`, golden oracle in `tests/test_golden.py`).
Roadmap edits are docs-only.
