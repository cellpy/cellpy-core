# Status — issue #13: Migrate the step/summary compute engine to polars (native schema)

- [ ] Done

Phased migration (see `issue13_plan.md`). **Phases 1–3 complete; Phase 4 remains.**

## Confirmed decisions (2026-06-14)

- **Engine vocabulary:** Option A — polars engine targets the **native** schema;
  `OldCellpyCellCore` bridges legacy↔native + pandas↔polars at the seam.
- **Dataframe lib:** pure **polars** in the engine.
- **Sequencing:** separate PR per phase.
- **Capacity:** raw capacity/energy are **cumulative per cycle, per direction** (mandated).
  Renamed `step_cumulative_*` → `cumulative_*`. Per-step (delta) and per-cycle (cycle-end)
  are derived. Verified on the real Arbin fixture. Full rationale in
  `.issueflows/04-designs-and-guides/step-table-polars-migration.md`.

## Phase 1 — extend native schema (DONE)

- `docs/data_format_specifications/harmonized_raw.md`: renamed the 4 `step_cumulative_*`
  capacity/energy columns to `cumulative_*`; added `step_time` and `internal_resistance`;
  added a *Capacity convention* section + Conventions bullet.
- `docs/data_format_specifications/step_table.md`: added `step_time` aggregates,
  `internal_resistance` aggregates, and `c_rate`.
- `src/cellpycore/config.py`: `RawCols` renamed cumulative columns + added `step_time`,
  `internal_resistance`; `StepCols` added `step_time_*`, `internal_resistance_*` aggregates
  and `c_rate`.
- `src/cellpycore/_helpers.py`: mock raw updated for the renamed/new columns.
- `tests/test_config_columns.py`: `RAW_EXPECTED` / `STEP_EXPECTED` updated to the new specs.
- `legacy.py` and the legacy/golden path are **unchanged** (cellpy contract intact).
- **Tests:** `uv run pytest` → 26 passed (golden suite unaffected).

## Deferred / notes

- `ref_potential` not added — **not present** in the golden Arbin data, so not needed for
  parity yet. Add when a consumer needs it.
- Power columns (`step_charge_power` / `step_discharge_power`) left as-is (instantaneous, not
  cumulative); a separate naming cleanup if desired.
- Whether native `test_time` / `datapoint_num` need **full** aggregates (vs first/last) for
  byte-exact legacy parity through the bridge is a **Phase 2** reconciliation decision
  (expand native StepCols vs regenerate the golden snapshot under the native column set).

## Phase 2 — polars step engine + bridge (DONE)

- `src/cellpycore/summarizers.py`: `make_step_table` rewritten **polars-native** on the
  native schema (full per-signal aggregates + `delta`, `c_rate`, step-type classification via
  `_classify_steps`). Removed the pandas `_ustep`/`delta`/groupby path.
- `src/cellpycore/cell_core.py`: `OldCellpyCellCore.make_core_step_table` is the
  **legacy↔native + pandas↔polars bridge**, reproducing the legacy 64-column step frame
  byte-for-byte.
- `tests/test_golden.py`: drives the step table through the bridge; the existing
  cellpy-parity snapshot stays the gate (no regen). `tests/test_schema.py`: step tests moved
  to the native schema.
- Parity choice **Path P** (reproduce legacy frame exactly) over Path N (regen golden); see
  the design note.
- Blank step-type "edge case": resolved as a **degenerate-fixture artifact** (matches legacy
  cellpy); classification left unchanged to preserve parity.
- **Tests:** `uv run pytest` → 26 passed.

## Phase 3a — data-model fix + summary oracle (DONE)

Phase 3 is split: **3a** lands the data-model fix + a summary regression oracle (legacy
pandas summary made to run); **3b** is the polars-native rewrite of `selectors.py` + the
summary functions + bridge.

- **Finding:** the summary path was never runnable — `Data` declared only `raw`/`cycle`/`step`,
  but the engine uses `data.steps`/`data.summary`/`data.has_steps` dynamically; `has_steps`
  was undefined → `AttributeError`. Once fixed, the existing legacy pandas summary runs
  (18 cycles × 27 cols; +scaled = 64) and reproduces the cellpy golden cyc-1 `data_point`
  (1457).
- `src/cellpycore/cell_core.py`: `Data` now declares `steps`/`summary` and exposes
  `has_steps`/`has_summary` properties.
- `dev/regenerate_test_data.py`: stage B fixed (its `make_step_table` call broke after Phase 2)
  to use the bridge, and now also writes `arbin_cc_summary_expected.parquet`.
- `tests/data/arbin_cc_summary_expected.parquet`: new frozen summary oracle (cellpy-core's
  own current output; cellpy byte-parity deferred to Phase 4).
- `tests/test_golden.py`: + `test_arbin_summary_matches_cellpy_goldens` (counts + cyc-1
  datapoint) and `test_arbin_summary_matches_snapshot`.
- **Tests:** `uv run pytest` → 28 passed.

## Phase 3b — polars-native summary engine + bridge (DONE)

Architecture decision **`bridge_extras`** (keep the curated native cycle schema clean):

- `src/cellpycore/summarizers.py`: new **polars-native** `make_summary` (+ `_add_end_potentials`)
  that produces only the **clean native `CycleCols` subset** (per-cycle capacities, CE,
  coulombic difference, capacity losses, `test_cumulated_*`, end-of-charge/discharge potentials).
  It does the cycle-end raw selection inline (no `selectors.create_selector`).
- `src/cellpycore/cell_core.py`:
  - `CellpyCellCore.make_core_summary` now calls the native engine (clean subset).
  - `OldCellpyCellCore.make_core_summary` is the **legacy↔native + pandas↔polars bridge**:
    native engine → rename native→legacy → add the **legacy-only "extras"** the curated native
    design deliberately omits (`cumulated_coulombic_efficiency`, `shifted_*`, `cumulated_ric*`,
    IR via `ir_to_summary`, C-rates via `c_rates_to_summary`) → legacy column order. Reproduces
    the Phase 3a summary oracle **byte-for-byte**.
- **Why bridge_extras (not extend CycleCols):** `cycle_table.md` is a curated forward design;
  the ~11 legacy-only summary columns are exactly the cruft it drops. Keeping them in the bridge
  leaves `CycleCols`/`cycle_table.md`/`CYCLE_EXPECTED` untouched.
- **Parity semantics verified:** polars `cum_sum`/`shift`/÷-by-zero match pandas exactly, so the
  rewrite is byte-faithful.
- `tests/test_schema.py`: + `test_make_summary_native_schema` (asserts the native summary has the
  clean subset and **no** legacy cruft). `tests/test_golden.py` summary oracle unchanged + green.
- **Superseded (transitional, left in place):** `summarizers.generate_absolute_summary_columns`,
  `summarizers.end_voltage_to_summary`, `selectors.create_selector`,
  `selectors.summary_selector_exluder` are no longer used inside cellpy-core but kept (the
  external `cellpy` repo may import them); prune in a later cleanup once usage is confirmed.
- **Tests:** `uv run pytest` → 29 passed.

## Remaining

- **Phase 4:** cross-repo parity tests vs cellpy's `make_step_table` / `make_summary`.
