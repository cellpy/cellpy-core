# Issue #56 — status

- [x] Done

## What was done (2026-07-02)

- Added `docs/standalone-use.md` — the slim-consumer guide:
  - Native `CellpyCellCore` + `Data.from_raw_frame` pipeline (uses the #55
    validating front door, per the issue's housekeeping note).
  - Class-free alternative (`summarizers.make_step_table` / `make_summary`)
    and when the class is worth it.
  - Caller contract (order, no metadata, units by value, raw shape
    assumptions incl. `normalize_capacity_granularity`, legacy cruft only on
    the bridge) plus a "cycle-mode trap" note (placeholder defaults to
    `"anode"`).
  - Links to the harmonized-raw spec and the Data-object doc.
- README: new Documentation section linking the guide; fixed the stale
  "only available on GitHub" install note (package is on PyPI as `cellpycore`).
- Verified both documented pipelines run end-to-end against
  `_helpers.create_raw_data()` mock data; full suite green (107 passed).
- Version bumped 0.1.1 → 0.1.2; `HISTORY.md` `[Unreleased]` promoted to
  `[0.1.2] - 2026-07-02` with a bullet for this issue.

## Remaining work

None — docs-only change, fully resolved.
