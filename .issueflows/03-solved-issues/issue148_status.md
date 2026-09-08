# Issue #148 — status

- [x] Done

## What's done

- Plan accepted (2026-09-08): trim trailing step on gap-append continuation;
  rebuild from that step's `datapoint_num_first`.
- `_trim_steps_for_overlap`: continuation fallback when the first incoming
  datapoint is past every existing step but `(cycle_num, step_num)` matches
  the last kept step.
- `update_data` gap-append branch now calls `_trim_steps_for_overlap` on
  `new_pl`; post-offset `from_data_point` still follows a non-continuation
  gap.
- Tests: `test_update_gap_append_mid_step_matches_full_recompute_oracle`,
  `test_update_core_data_gap_append_mid_step_c_rate_matches_full`.
- `uv run pytest`: 287 passed, 3 deselected. `ruff check` + `ruff format --check`
  clean.
- Version bump `0.2.5` → `0.2.6`. `HISTORY.md` promoted (`#147`/`#148` under
  `[0.2.6]`; `#142` backfilled under `[0.2.5]` to match tag `v0.2.5`).

## Remaining work

- None in this repo.
- Follow-up (cellpy repo, after `cellpycore` pin bump to a release with this
  fix): remove strict `xfail` on
  `tests/test_incremental_update.py::test_gap_append_mid_step_equals_full_load`.
