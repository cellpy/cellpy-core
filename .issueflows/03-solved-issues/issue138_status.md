# Issue #138 — Status

- [x] Done

## 2026-07-18

- Implemented `throughput_to_raw` and `efc_to_summary` in `src/cellpycore/summarizers.py`.
- Registered `test_cumulated_capacity_throughput` and `equivalent_full_cycles` on `CycleCols` (`config.py`), in `docs/specifications/cycle-table.md`, in `tests/test_config_columns.py`, and as `NATIVE_ONLY_CYCLE` in `legacy/mapping.py`.
- Added `tests/test_efc.py` (4 tests). Full suite: 265 passed.
- End-to-end sanity run on mock data with A·s→mAh factor verified by hand (≈194 mAh throughput → EFC ≈ 0.324 at nom_cap 300 mAh).

## 2026-07-23 (revision after review)

- **Integration fixed**: right-Riemann `|I_i|·dt` → trapezoidal `mean(|I|)·dt` in `throughput_to_raw`. The old rule charged a whole preceding rest to the first sample of a pulse — wrong for the irregularly sampled field/BMS data this targets.
- **Silent failures now logged**: missing current values and negative time deltas are counted and emitted as `logger.warning` instead of passing as zero.
- **Legacy names **: `equivalent_full_cycles` and `cumulated_capacity_throughput` added to legacy `HeadersSummary` + `CYCLE_PAIRS` + `LEGACY_ATTR_TO_SCHEMA`; removed from `NATIVE_ONLY_CYCLE`. EFC now reaches default-schema cellpy users, not only `native_schema=True`.
- **Wired into `add_scaled_summary_columns`** (native + legacy bridge), unconditionally — no `add_efc` flag (`nom_cap_abs` is already resolved there, next to `equivalent_cycles_to_summary`).
- **Units helper**: `calculate_throughput_conversion_factor(current_unit, time_unit)` in `units/converters.py` so cellpy computes the A·s→charge factor the pint way (mirrors `calculate_current_conversion_factor`), instead of hand-derived `1000/3600` at call sites.
- **Docs**: raw derived-columns table in `harmonized-raw.md`; `cycle-table.md` notes `EFC = normalized_cycle_index·(1+CE)/2`.
- **Tests**: analytic case (1 A × 3600 s → EFC 0.5), trapezoidal-vs-right-Riemann, bad-input warnings, native + legacy-bridge wiring, units factor. The old `_expected_raw_throughput` helper mirrored the implementation and could not fail; kept but now backed by the analytic + bridge cases. Full suite: **271 passed**.

## Remaining

- **Blocking cellpy PR**: bump `cellpycore==0.2.4` pin in cellpy `pyproject.toml`, add `helpers.add_efc` wrapper (mirrors `add_normalized_cycle_index`) for the `cell.calculate_efc(...)` API from the issue. Plot label (`plotutils.py:823`) stays as-is, `equivalent_full_cycles` gets no axis-label entry (falls back to column name).
- Version bump to **0.3.0** on close (new spec columns = schema change).
- Deferred (per approved plan): energy throughput, SoC-based EFC.
