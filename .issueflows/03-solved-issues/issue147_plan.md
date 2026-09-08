# Issue #147 — plan

Source: https://github.com/cellpy/cellpy-core/issues/147

## Goal

`CellpyCellCore.update_core_data(data, new_raw=<empty>)` must be a true no-op:
returned frames identical to the input (no `charge_c_rate_right` /
`discharge_c_rate_right` / `ir_*_right` columns).

## Constraints

- Polars-native engine; accept pandas frames for convenience (existing pattern).
- Input `Data` must not be mutated (`update_data` contract; keep the `_copy_data` return).
- Non-empty `new_raw` path unchanged (oracle tests in `tests/test_merge.py` stay green).
- Google-style docstrings; `ruff check` + `ruff format --check` clean.
- Downstream: cellpy `tests/test_incremental_update.py::test_empty_tail_is_noop` is
  `xfail(strict=True)` against this issue. Once cellpy bumps its `cellpycore` pin to a
  release containing this fix, that xfail marker must be removed (cellpy follow-up, out
  of scope here — note in PR body).

### Prior art

- `merge.update_data` (`src/cellpycore/merge.py:221`): already short-circuits on
  `new_raw is None or _frame_is_empty(new_raw)` → `_copy_data(data)`. The bug is that
  `update_core_data` does not honour that short-circuit before `refresh_derived`.
- `merge._frame_is_empty` (`merge.py:389`): polars/pandas-agnostic emptiness check —
  reuse it in `cell_core.py` instead of writing a new one.
- `summarizers.c_rates_to_summary` (`summarizers.py:1172`) and
  `summarizers.ir_to_summary` (`summarizers.py:1274`): both do a bare
  `summary.join(..., how="left")` and are therefore **not idempotent** — calling either
  twice on the same summary yields `*_right` columns. `ir_to_summary` has the identical
  latent defect (only masked because the issue repro has no IR column in raw).
- `tests/test_merge.py::test_update_core_data_refresh_derived` (line 336): existing
  test for the derived-refresh path; new tests go beside it, reusing `_single_test_raw`,
  `_process_raw`, `_schema` helpers.
- Toolbox (`.issueflows/00-tools/`) empty; graphify report not needed (three
  known call sites, all located by grep).

## Approach

Two small changes — a direct no-op fix plus idempotency hardening of the two
summarizers so the same class of bug cannot recur from another caller.

1. **`update_core_data`: return early on empty `new_raw`.**
   After the pandas→polars coercion, if `_frame_is_empty(new_raw)` (or `new_raw is None`),
   return `update_data(...)`'s result directly (it already returns `_copy_data(data)`)
   and skip the whole `refresh_derived` block. Cheapest, and matches the documented
   "empty tail is a no-op" expectation. Docstring: add one sentence stating that an
   empty `new_raw` returns an unmodified copy and skips derived refresh.

2. **Make `c_rates_to_summary` and `ir_to_summary` idempotent.**
   Before the join, drop the target columns if already present:
   `summary = summary.drop([c for c in (charge_c_rate, discharge_c_rate) if c in summary.columns])`
   (same for `ir_charge` / `ir_discharge`). Re-running then overwrites instead of
   producing `*_right`. This is the "either" alternative from the issue; doing both
   keeps the no-op guarantee cheap (1) and removes the footgun for any other caller (2).

Order: 1 → 2 → tests → ruff.

## Files to touch

- `src/cellpycore/cell_core.py` — `update_core_data`: early return on empty `new_raw`
  (import `_frame_is_empty` alongside `update_data` from `cellpycore.merge`); docstring note.
- `src/cellpycore/summarizers.py` — `c_rates_to_summary`, `ir_to_summary`: drop
  pre-existing target columns before the join; one docstring line each ("idempotent:
  existing columns are replaced").
- `tests/test_merge.py` — new tests (see below).
- `CHANGELOG.md` (if present — check at close) — fix entry.

## Test strategy

Run: `uv run pytest` then `uv run ruff check && uv run ruff format --check`.

New tests in `tests/test_merge.py`:

- `test_update_core_data_empty_new_raw_is_noop` — build `base` via `_process_raw`, run
  `cell.update_core_data(base, extension.clear())` (polars empty frame with same
  schema) with default `refresh_derived=True`; assert `updated.summary.columns ==
  base.summary.columns`, no column ends with `_right`, and `raw`/`steps`/`summary`
  `.equals()` the input. Also assert input `base` untouched.
- `test_update_core_data_empty_pandas_new_raw_is_noop` — same with
  `extension.to_pandas().iloc[0:0]` (the cellpy repro shape).
- `test_c_rates_to_summary_idempotent` — call twice on processed data; columns
  unchanged after second call, values equal.
- `test_ir_to_summary_idempotent` — same for IR (needs raw with
  `internal_resistance` column; check `_single_test_raw` provides it, else add it).

Existing oracle tests (`test_update_overlap_matches_full_recompute_oracle`,
`test_update_gap_append_matches_full_recompute_oracle`,
`test_update_core_data_refresh_derived`, `tests/test_e2e.py`) guard the non-empty path.

## Open questions

- Scope of step 2 (idempotency hardening of both summarizers): include it, or ship only
  the early return (step 1)? Recommendation: include — two-line change each, closes the
  same defect in `ir_to_summary`, and the issue lists it as an acceptable fix.
- Version bump at close: `patch` (bug fix, no API change). Cellpy needs a new
  `cellpycore` release to drop its xfail.
