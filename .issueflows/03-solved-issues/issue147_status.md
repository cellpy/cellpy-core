# Issue #147 — status

- [x] Done

## What's done

- Plan accepted (2026-09-08): early return in `update_core_data` on empty `new_raw`
  + idempotent `c_rates_to_summary` / `ir_to_summary`.
- `cell_core.update_core_data`: returns the `update_data` copy directly when `new_raw`
  is `None` or empty (skips `refresh_derived`); docstring updated.
- `summarizers.c_rates_to_summary` / `ir_to_summary`: drop pre-existing target columns
  before the join via new `_drop_existing` helper → idempotent; docstrings updated.
- Tests (`tests/test_merge.py`): `test_update_core_data_empty_new_raw_is_noop`,
  `test_update_core_data_empty_pandas_new_raw_is_noop`,
  `test_c_rates_to_summary_idempotent`, `test_ir_to_summary_idempotent`.
  Verified all 4 fail on `main` code, pass with fix.
- Full suite: 285 passed. `ruff check` + `ruff format --check` clean.
- `HISTORY.md` bullet under `[Unreleased]`. No version bump (0.2.5 already pending release).

## Remaining work

- None in this repo.
- Follow-up (cellpy repo, after `cellpycore` pin bump to a release with this fix): remove
  strict `xfail` on `tests/test_incremental_update.py::test_empty_tail_is_noop`.
