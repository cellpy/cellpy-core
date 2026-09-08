# Issue #148 — plan

Source: https://github.com/cellpy/cellpy-core/issues/148

## Goal

`merge.update_data` gap-append (`new_raw` starts strictly after existing
`datapoint_num` / `source_datapoint_num` max) must not split a tester step that
continues across the cut. Resulting steps + summary match a full
`make_step_table` / `make_summary` on the concatenated raw (same contract as
the overlap path).

## Constraints

- Polars-native; do not mutate the input `Data` (`_copy_data` / new frames).
- Overlap path (`r2_start <= r1_max`) stays unchanged — already trims via
  `_trim_steps_for_overlap` and the existing oracle stays green.
- Gap-append that starts on a **new** (cycle, step) stays as today: keep every
  existing step row, rebuild from the first new `datapoint_num`.
- Single-`test_id` only (`update_data` v1). Match `(cycle_num, step_num)` as
  the issue states; do not invent `sub_step_num` matching (engine still
  hardcodes sub-step `1`).
- Google-style docstrings; `ruff check` + `ruff format --check` clean.
- Downstream: cellpy `tests/test_incremental_update.py::test_gap_append_mid_step_equals_full_load`
  is `xfail(strict=True)` against this issue. Dropping that marker is a cellpy
  follow-up after the next `cellpycore` pin bump — note in PR body, out of
  scope here.

### Prior art

- `merge.update_data` (`src/cellpycore/merge.py`): `gap_append = r2_start > r1_max`
  keeps **all** `steps_pl` and sets `from_data_point` to `min(new datapoint_num)`.
  That is the bug. Overlap branch already calls `_trim_steps_for_overlap`.
- `_trim_steps_for_overlap` (`merge.py`): finds the step whose
  `[datapoint_num_first, datapoint_num_last]` contains the first overlapping
  datapoint, drops that step and later ones, returns `from_data_point` = that
  step's first. On a **gap**, the first new datapoint is *after* every existing
  `datapoint_num_last`, so this helper currently keeps all steps — it cannot
  detect continuation by range alone.
- `summarizers.make_step_table(..., from_data_point=)` (`summarizers.py`):
  filters `datapoint_num >= from_data_point` then `group_by(test_id, cycle_num,
  step_num, sub)`. Rebuilding from the spanning step's first datapoint
  concatenates the kept partial raw + new rows into one step group. That is
  why overlap works and why gap-append must use the same `from_data_point`.
- Issue #86 original algorithm: *"If r2(0) >= r1(last): find what step r2(0)
  is in. That step and all the ones after will then belong to R2."* Gap-append
  skipped that "find the step" part; this issue completes it.
- `tests/test_merge.py::test_update_gap_append_matches_full_recompute_oracle`:
  cut is at `source_datapoint_num == 20` (`_single_test_raw` n_cycles=3) —
  **step boundary** (start of cycle 3 step 1), so it does not catch this bug.
  New tests go beside it; reuse `_single_test_raw`, `_process_raw`,
  `_steps_oracle_equal`, `_summary_oracle_equal`.
- `step-c-rate-split.md`: `update_data` still appends `c_rate` to rebuilt rows
  when kept steps carry it — keep that. Split steps are why downstream
  `discharge_c_rate` drifts.
- Toolbox (`.issueflows/00-tools/`) empty. Graphify community 76 is the
  `merge.py` helper cluster (`_trim_steps_for_overlap`, `update_data`); no
  extra helper to reuse.

## Approach

Implement the issue's primary expected behaviour (trim), not the
"document that callers must re-read" alternative.

1. **Continuation trim on gap-append.** After detecting `gap_append`, still
   keep **all** existing raw (`kept_raw = raw_pl` — new rows do not repeat the
   partial step). Trim steps: if the first new row's `(cycle_num, step_num)`
   equals the **last** existing step's `(cycle_num, step_num)`, drop that last
   step and set `from_data_point` to its `datapoint_num_first`. Else keep all
   steps and `from_data_point = min(new datapoint_num)` (current behaviour).

   Implement as a **continuation fallback inside** `_trim_steps_for_overlap`
   (when `overlap_idx is None`), then call that helper from the gap-append
   branch with `new_pl` as the "incoming" frame. One trim function, two
   callers. Do not add a second helper unless the fallback makes the overlap
   docstring dishonest — if so, a tiny `_trim_steps_for_gap_append` next to it
   is the fallback (same predicate).

   Predicate (last step vs first incoming row, after sort by
   `datapoint_num` / `datapoint_num_first`):

   ```text
   last[shdr.cycle_num] == first_new[nhdr.cycle_num]
   and last[shdr.step_num] == first_new[nhdr.step_num]
   ```

2. **Do not trim `kept_raw` on gap.** Overlap drops existing rows with
   `partition >= r2_start` because `new_raw` re-sends them. Gap does not.
   `make_step_table(from_data_point=spanning_first)` then sees kept partial
   points **plus** new points and rebuilds one step row.

3. **Docs.** One sentence on `update_data` and on `_trim_steps_for_overlap`:
   gap-append that continues the trailing `(cycle, step)` rebuilds that step
   from `datapoint_num_first`, same as overlap.

Order: helper + `update_data` call site → tests → ruff → `HISTORY.md` at
close.

## Files to touch

- `src/cellpycore/merge.py` — continuation fallback in
  `_trim_steps_for_overlap` (or sibling helper); gap-append branch calls it
  instead of keeping all steps; docstring.
- `tests/test_merge.py` — new oracle test(s) (see below).
- `HISTORY.md` — `[Unreleased]` fix bullet at close.

No `cell_core.py` change unless a docstring cross-ref is useful;
`update_core_data` already forwards to `update_data`.

## Test strategy

Run: `uv run pytest` then `uv run ruff check && uv run ruff format --check`.

New tests in `tests/test_merge.py`, same helpers as the existing update
oracles:

- `test_update_gap_append_mid_step_matches_full_recompute_oracle` — the
  issue. `_single_test_raw(..., n_cycles=2)`: cycle 2 step 1 is datapoints
  10–14. `base_raw` = `source_datapoint_num <= 12`, `extension` =
  `source_datapoint_num >= 13` (`r2_start > r1_max` → gap). Assert
  `_steps_oracle_equal` + `_summary_oracle_equal` vs `_process_raw(full_raw)`.
  Also `updated.steps.height == oracle.steps.height` (no extra split row).
- `test_update_core_data_gap_append_mid_step_c_rate_matches_full` — same cut
  through `CellpyCellCore.update_core_data` (default `refresh_derived=True`);
  `discharge_c_rate` / `charge_c_rate` match a fully processed oracle
  (`pytest.approx`). Guards the cellpy L6 symptom.

Existing `test_update_gap_append_matches_full_recompute_oracle` (step-boundary
gap) and `test_update_overlap_matches_full_recompute_oracle` stay green.
Optional e2e mid-step cut on the Arbin fixture is **out of scope** (unit
oracle is enough; fixture may be absent).

## Open questions

- Trim vs document-only (issue lists both)? **Recommend trim** — overlap
  already does this; #86's update algorithm already said "find what step
  r2(0) is in". Document-only would leave core wrong and keep the cellpy
  xfail forever.
- Extend `_trim_steps_for_overlap` vs a new `_trim_steps_for_gap_append`?
  **Recommend extend** (continuation fallback when the first incoming
  datapoint is past every `datapoint_num_last`). New helper if that muddies
  the overlap-only name.
- Version bump at close: **patch** (behaviour bug, no API change). Cellpy
  needs a new `cellpycore` release to drop its xfail.
