# Issue #148 — status

- [ ] Done

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
- `HISTORY.md` `[Unreleased]` bullet.

## Remaining work

- `uv run pytest` + ruff.

