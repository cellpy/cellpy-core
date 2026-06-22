# Status — issue #21: Complete the native polars summary path

- [x] Done

## What landed

Single PR (per confirmed plan). Native polars summary path now stands on its own.

### Helpers ported to polars-native (`src/cellpycore/summarizers.py`)
- `generate_specific_summary_columns` — polars `with_columns`; skips columns absent from the summary.
- `_calculate_nominal_capacity_from_cycles` — polars `filter`/`mean` on `schema.cycle.cycle_num`.
- `equivalent_cycles_to_summary` — `normalized_cycle_index = test_cumulated_charge_capacity / nom_cap`.
- `c_rates_to_summary` — per-cycle first charge/discharge `c_rate` joined onto the summary.
- `ir_to_summary` — self-contained (no `selectors.get_step_numbers`), **behaviour-preserving** (legacy off-by-one IR quirk kept oracle-locked).
- All accept a pandas frame for convenience (convert to polars), matching `make_summary`.

### Anode mode
- `make_summary` gained `test_mode: TestMode` (`NORMAL`/`INVERTED`); `INVERTED` flips `coulombic_efficiency` and `coulombic_difference` only.
- `CellpyCellCore.make_core_summary` derives the mode from `cycle_mode == "anode"` and now also adds native C-rate / IR columns.

### Schema (Option A — revises Phase 3b; recorded in `04-designs-and-guides/step-table-polars-migration.md`)
- `config.CycleCols`: added `normalized_cycle_index`, `charge_c_rate`, `discharge_c_rate`, `ir_charge`, `ir_discharge`, and a `specific_columns` accessor.
- Synced `docs/data_format_specifications/cycle_table.md` and `tests/test_config_columns.py::CYCLE_EXPECTED`.

### Bridge (`src/cellpycore/cell_core.py`)
- `OldCellpyCellCore.make_core_summary` runs the native polars C-rate/IR helpers before the native→legacy rename; legacy-only cruft (`cumulated_coulombic_efficiency`, `shifted_*`, `cumulated_ric*`) stays pandas in `_add_legacy_summary_cruft`.
- `OldCellpyCellCore.add_scaled_summary_columns` overridden to bridge pandas↔polars + legacy↔native (maps `{col}_{mode}` specific columns back to legacy names) — keeps cellpy's legacy call working.

### Tests (`tests/test_schema.py`)
- Updated `test_generate_specific_columns_takes_factor_by_value` to polars.
- Added: anode CE/coulombic-difference flip, native `c_rates_to_summary`, native `ir_to_summary`, native `add_scaled_summary_columns` end-to-end.

## Verification
- `uv run pytest` — **34 passed**. Golden summary oracle (`test_golden.py`) stays byte-green through the bridge.

## Acceptance check
- [x] Native `CellpyCellCore` summary path runs end-to-end without the legacy bridge.
- [x] `tests/test_golden.py` summary oracle byte-green through the bridge.
- [x] New native-schema tests mirroring `test_make_summary_native_schema`.

## Remaining / follow-ups (out of scope)
- `ir_to_summary` correctness bug (writes IR for cycle n on n+1) — preserved here, fix in its own issue.
- Cross-repo (cellpy) byte-parity for the bridge `add_scaled` path — covered when cellpy bumps its pinned core (cellpy#377/#378).
