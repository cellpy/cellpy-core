# Issue #68 status: units fallback → explicit values / `CellMeta`

- [x] Done

Plan: [issue68_plan.md](issue68_plan.md) (confirmed 2026-07-03)

## What's done

- `units.py`: `_resolve_optional_attr`, `_require_attr`, `_resolve_raw_units`; both public helpers accept explicit kwargs + `CellMeta`; pointless try/except removed
- `cell_core.py`: optional `cell_meta` on `add_scaled_summary_columns` (native + legacy bridge) and `_resolve_specific_converter`
- Tests: `CellMeta` + `ValueError` cases in `test_units_converters.py`; `test_native_add_scaled_summary_columns_with_cell_meta` in `test_schema.py`
- Suite green: 127 passed (+ 3 deselected benchmarks)

## Remaining work

None.
