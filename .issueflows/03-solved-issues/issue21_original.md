# Issue #21: Complete the native polars summary path (port remaining helpers + anode mode + native add_scaled)

Source: https://github.com/cellpy/cellpy-core/issues/21

## Original issue text

Follow-up to #13. The step engine and the **core** per-cycle summary subset (`summarizers.make_summary`) are polars-native, but several summary helpers are still pandas and are only reachable through the `OldCellpyCellCore` legacy bridge. To finish the migration the native path needs to stand on its own.

### Port to polars-native (native schema)
These are tagged with `TODO(#13)` in `src/cellpycore/summarizers.py`:
- [ ] `c_rates_to_summary` (still used by the legacy summary bridge)
- [ ] `ir_to_summary` (see separate correctness bug issue — keep behaviour oracle-locked while porting)
- [ ] `equivalent_cycles_to_summary` (used by `add_scaled_summary_columns`)
- [ ] `generate_specific_summary_columns` (used by `add_scaled_summary_columns`)
- [ ] `_calculate_nominal_capacity_from_cycles` (helper for the two above)

### Native-path gaps discovered during #13
- [ ] **Anode (discharge-first) cycle mode.** `make_summary` currently assumes full-/cathode convention (charge = first). Add discharge-first handling (legacy `cycle_mode == ANODE`).
- [ ] **Native `add_scaled_summary_columns`.** Only the legacy bridge path works today; the native `CellpyCellCore` path needs `normalized_cycle_index` + specific (gravimetric/areal/absolute) columns on the native `CycleCols`.

### Acceptance
- The native `CellpyCellCore` summary path runs end-to-end without the legacy bridge.
- `tests/test_golden.py` summary oracle stays byte-green through the bridge.
- New native-schema tests mirroring `test_make_summary_native_schema`.
