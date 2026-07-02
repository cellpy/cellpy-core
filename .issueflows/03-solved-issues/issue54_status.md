# Issue #54 status — Native exclude-types summary support

- [x] Done

## What's done

- 2026-07-02: plan accepted (`issue54_plan.md`); branch `54-exclude-types-summary` created off up-to-date `main`.
- 2026-07-02: implemented per plan:
  - `summarizers.make_summary` gained `exclude_step_types: Optional[Sequence[str]] = None`; new helper `_subtract_excluded_step_deltas` subtracts excluded steps' per-cycle `last - first` capacity deltas (prefix match on `step_type`, `_group_keys`-aware, `fill_null(0.0)`) from the cycle-end capacities **before** CE / loss / cumulated columns are derived.
  - Pass-through kwarg on `CellpyCellCore.make_core_summary` and `OldCellpyCellCore.make_core_summary` (legacy bridge, per accepted open question 1).
  - Capacities-only correction (accepted open question 2); documented in the helper docstring.
  - New `tests/test_exclude_types.py` (7 tests): parity vs inline pandas oracle (resurrected `summary_selector_exluder` math), derived-column correctness, `None`/`[]` guard, unmatched-prefix zero correction, cycle-without-excluded-step, `startswith` ("only-cv") semantics lock, merged two-test isolation.
- Full suite green: 107 passed (golden fixtures untouched → `None` path byte-identical).

## Remaining work

- None in this repo. Cellpy-side follow-up (wire `selector_type` / `exclude_types`
  to the new kwarg instead of the bare `DeprecationWarning`) is a separate issue in
  jepegit/cellpy. `selector-dead-code-deferral.md` note updated at close.
