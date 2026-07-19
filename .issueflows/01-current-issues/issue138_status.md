# Issue #138 — Status

- [x] Done

## 2026-07-18

- Implemented `throughput_to_raw` and `efc_to_summary` in `src/cellpycore/summarizers.py`.
- Registered `test_cumulated_capacity_throughput` and `equivalent_full_cycles` on `CycleCols` (`config.py`), in `docs/specifications/cycle-table.md`, in `tests/test_config_columns.py`, and as `NATIVE_ONLY_CYCLE` in `legacy/mapping.py`.
- Added `tests/test_efc.py` (4 tests). Full suite: 265 passed.
- End-to-end sanity run on mock data with A·s→mAh factor verified by hand (≈194 mAh throughput → EFC ≈ 0.324 at nom_cap 300 mAh).

## Remaining

- Nothing for this issue. Deferred (per approved plan): energy throughput, SoC-based EFC, default wiring into `make_core_summary`.
