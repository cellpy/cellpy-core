# Issue #56 — plan

## Goal

Add a user-facing "Using cellpy-core standalone" guide to `docs/` so slim consumers
(anyone with a polars frame in the native `config.RawCols` schema) can get step
tables and per-cycle summaries without full cellpy. Link it from the README.

## Approach

- New `docs/standalone-use.md` covering:
  - Recommended entry point: native `CellpyCellCore` + `Data.from_raw_frame`
    (#55 landed, so the example uses the validating front door, not bare
    `core.data.raw = ...`).
  - Full pipeline example: `make_core_step_table` (nom_cap, raw_limits) →
    `make_core_summary` (current_conversion_factor, exclude_step_types) →
    optional `add_scaled_summary_columns` (specific_converters).
  - Class-free alternative: `summarizers.make_step_table` + `summarizers.make_summary`
    with the default schema, and when the class is worth it (cycle_mode → TestMode,
    IR/C-rate orchestration).
  - Caller contract: step table before summary; no metadata required; units by
    value (pint only via the optional `units` extra); raw-shape assumptions
    (`epoch_time_utc` int64 ns UTC, cycle-cumulative capacities →
    `normalize_capacity_granularity` for step-/test-cumulative inputs, `test_id`
    optional); legacy cruft only on the `OldCellpyCellCore` bridge.
  - Links to `docs/data_format_specifications/harmonized_raw.md` and
    `docs/data-object-definition.md`.
- README: add a short Documentation section linking the guide (and install note —
  package is on PyPI as `cellpycore` since v0.1.1, README still says GitHub-only;
  fix that line while touching it).

## Files to touch

- `docs/standalone-use.md` (new)
- `README.md` (link + install line)
- `.issueflows/01-current-issues/issue56_*.md` (tracking)
- `HISTORY.md`, `pyproject.toml` (at close: patch bump + promote)

## Test strategy

Docs-only change — no engine code touched. Re-run `uv run pytest` (107 tests) to
confirm the suite stays green; verify the example snippets against the real
signatures in `cell_core.py` / `summarizers.py` (done while writing).

## Design docs consulted

`cellpy-core-integration-roadmap.md`, `cellpy-core-migration.md` §4,
`release-procedure.md` (for the close/release steps).
