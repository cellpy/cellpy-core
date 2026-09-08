# Issue #147: update_core_data: empty new_raw with refresh_derived duplicates c-rate columns

Source: https://github.com/cellpy/cellpy-core/issues/147

## Original issue text

Found by the cellpy L6 golden-equality oracle (jepegit/cellpy#778).

`CellpyCellCore.update_core_data(data, new_raw=<empty frame>)` short-circuits inside `merge.update_data` (returns `_copy_data(data)`), but `refresh_derived=True` (default) then runs `summarizers.c_rates_to_summary` on a summary that already carries `charge_c_rate` / `discharge_c_rate`. The join adds `charge_c_rate_right` / `discharge_c_rate_right`.

Expected: an empty `new_raw` is a no-op (frames identical to the input).

Repro (cellpy 2.1.4 / cellpycore 0.2.5): `tests/test_incremental_update.py::test_empty_tail_is_noop` in jepegit/cellpy (strict xfail until fixed).

Suggested fix: skip the `refresh_derived` block when `new_raw` is empty, or make `c_rates_to_summary` drop existing c-rate columns before joining (idempotent).
