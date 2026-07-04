# Issue #86 status

- [x] Done

## What's done

### Phase A
- `merge_data` in `src/cellpycore/merge.py`
- `CellpyCellCore.merge_core_data` wrapper
- Exported `merge_data` from `cellpycore`
- 11 merge tests

### Phase B
- `update_data` — partition trim, incremental steps (`from_data_point`), full summary rebuild
- `CellpyCellCore.update_core_data(refresh_derived=True)` — IR + C-rates
- Exported `update_data`
- 6 update tests (overlap, gap, full-replace error, immutability, validation, refresh_derived)
- Full suite green (148 passed)

## Remaining work

- None
