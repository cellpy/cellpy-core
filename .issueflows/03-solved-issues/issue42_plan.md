# Issue #42 plan — reset-granularity normalization for cumulative raw inputs

## Goal

Let the engine accept raw capacity/energy columns that are **step-cumulative** or
**test-cumulative** and normalize them to the mandated **cycle-cumulative** convention
before aggregation. Cycle-cumulative input stays an exact no-op (goldens unchanged).

## Constraints

- Cycle-cumulative is the mandated raw convention (`harmonized_raw.md` §Capacity convention,
  `step-table-polars-migration.md` issue #13). Only cycle-cumulative Arbin path is exercised
  today → keep it byte-identical.
- Engine is polars-native, schema-injected, thread-safe (no module globals). Match that.
- No auto-detection of granularity (fragile). Caller declares it explicitly; default = cycle.
- KISS: one small function + one enum + tests. No new module.

### Prior art
- `summarizers._ensure_test_id` / `_group_keys` (module `summarizers.py`) — reuse for the
  per-test composite grouping. Mirror convention.
- `summarizers.make_step_table` / `make_summary` — both read the four `cumulative_*` raw
  columns (`RawCols.cumulative_charge/discharge_capacity`, `..._energy`). The normalized frame
  must feed both.
- Enum style: `config.TestMode` / `StepType` (StrEnum) — mirror for the new granularity enum.
- Toolbox `.issueflows/00-tools/` — empty, nothing to reuse.
- Mock builders: `tests/test_schema.py::_build_cumulative_raw` (cycle-cumulative oracle) —
  base the step/test-cumulative fixtures on it.

## Approach

**Granularity-agnostic reconstruction** (works uniformly, no reset-point sniffing):

For each present cumulative column, ordered by `datapoint_num`:
1. `increment(row) = value - value(prev row in the source-granularity reset group)`, with the
   first row of each source group = its own value. Source reset group:
   - `STEP`  → `(test_id, cycle_num, step_num)`
   - `CYCLE` → `(test_id, cycle_num)`  (target; identity)
   - `TEST`  → `(test_id)`
2. `cycle_cumulative = increment.cum_sum().over((test_id, cycle_num))` (target reset boundary).

This is exact for all three inputs and provably identity for `CYCLE` (reconstruct per-cycle
diffs, re-accumulate per cycle = original). Direction-agnostic: an inactive-direction column
that holds constant or zeros contributes zero increments, so prior accumulation is preserved.
Uses polars `diff`/`cum_sum` `over(...)` window expressions (fast, thread-safe).

**Where it lives:** a standalone engine step `normalize_capacity_granularity(data, schema, granularity)`
in `summarizers.py` that rewrites `data.raw` in place and returns `data`. Running it once
up front means both `make_step_table` and `make_summary` consume the normalized raw. When
`granularity == CYCLE` it returns `data` untouched (no frame rewrite → goldens byte-stable).

**Columns:** normalize whichever of the four `cumulative_*` columns are present
(`RawCols.cumulative_charge_capacity`, `cumulative_discharge_capacity`,
`cumulative_charge_energy`, `cumulative_discharge_energy`). Missing ones skipped.

## Files to touch

- `src/cellpycore/config.py` — add `ResetGranularity(StrEnum)` with `CYCLE`/`STEP`/`TEST`
  (Google docstring; note cycle = the mandated raw convention / default).
- `src/cellpycore/summarizers.py` — add `normalize_capacity_granularity(data, schema=None,
  granularity=ResetGranularity.CYCLE)`; reuse `_ensure_test_id` + composite keys; polars
  window impl; pandas-in → pandas-out convenience like the sibling functions.
- `tests/test_schema.py` — add fixtures `_build_step_cumulative_raw` /
  `_build_test_cumulative_raw` (same underlying increments as `_build_cumulative_raw`) and
  tests: STEP→cycle and TEST→cycle each equal the cycle-cumulative frame; CYCLE input is an
  exact no-op.

## Test strategy

- Command: `uv run pytest` (or activate `.venv` then `pytest`).
- New unit tests as above (equivalence of normalized step/test-cumulative to the
  cycle-cumulative oracle; no-op on cycle input).
- Regression: full suite green, esp. `tests/test_golden.py` (goldens must not move — the
  default `CYCLE` path never rewrites the frame).

## Open questions

1. **Wiring into the pipeline.** Recommend keeping it a **standalone step** the caller runs
   before `make_step_table`/`make_summary` (default no-op), rather than adding a kwarg to
   `make_step_table`. Add a thin `CellpyCellCore` convenience method now, or defer wiring
   until a real non-cycle-cumulative consumer exists? (Recommend: ship the engine function +
   tests now, defer method/bridge wiring — matches the issue's "lower priority" framing.)
2. **Energy columns.** Include the two `cumulative_*_energy` columns in the same pass
   (recommended, same semantics) — confirm.
3. **Negative/`null` handling.** Assume clean monotonic-within-group inputs; treat a leading
   `null` as start-of-group. OK to not special-case malformed raw here?
