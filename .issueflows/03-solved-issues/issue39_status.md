# Issue #39 status: finalize cellpy-core integration roadmap

- [x] Done

## What was done (2026-06-28)

- Reviewed the roadmap (`cellpy-core-integration-roadmap.md`) and all companion design
  docs; produced the gap analysis (see `issue39_plan.md`).
- Created six cellpy-core GitHub issues for the remaining work:
  - #40 — Finalize STEP-12 (core): promote `CellpyUnits` to a unit-spec module + parity tests
  - #41 — Per-test metadata: add `test_id` to `StepCols`/`CycleCols` + composite group keys
  - #42 — Engine: reset-granularity normalization for cumulative raw inputs
  - #43 — Native schema: add `ref_potential`/`ref_voltage` support
  - #44 — Release: tag cellpy-core (and decide PyPI publish)
  - #45 — Cleanup (blocked): remove `create_selector`/`summary_selector_exluder`
- Updated the roadmap doc: fixed the stale Implementation Flow placeholder, added the
  "Remaining work (STEP-13+)" section (anchored to design docs + issues #40–#45), and
  refreshed the status-at-a-glance note.

## Remaining work

None for #39 itself. The spawned issues (#40–#45) carry the forward implementation work.
cellpy-side delegation (units converters, seam) remains tracked on jepegit/cellpy.
