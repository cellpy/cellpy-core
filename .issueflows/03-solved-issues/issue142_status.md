# Issue #142 — status

- [x] Done

## What's done

- Plan confirmed (`issue142_plan.md`).
- Added `_unwrap_meta_scalar` / `_as_cycle_mode_scalar` in `cell_core.py`.
- Hardened `CellpyCellCore.cycle_mode` getter/setter to store/return scalar
  (or `None`); nested lists no longer persist as lowered lists.
- `_cycle_mode_to_test_mode` unwraps list/tuple before `.strip()`.
- Tests in `tests/test_schema.py` (issue #142 block): translator shapes,
  setter scalar store, getter unwrap, `OldCellpyCellCore.make_core_summary`
  smoke with `[['anode']]` meta.
- Full suite: 281 passed; ruff green.
- `HISTORY.md` Unreleased bullet added.

## Remaining work

- None (close / PR).
