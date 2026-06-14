# Status — issue #13: Migrate the step/summary compute engine to polars (native schema)

- [ ] Done

Phased migration (see `issue13_plan.md`). **Phase 1 complete; Phases 2–4 remain.**

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

## Remaining

- **Phase 2:** polars-native `make_step_table` + legacy↔native / pandas↔polars bridge in
  `OldCellpyCellCore`; keep `tests/test_golden.py` green; fix tiny-fixture blank-`type` edge
  case.
- **Phase 3:** polars-native summary path (`summarizers` summary fns + all of `selectors.py`)
  + bridge `make_core_summary` / `add_scaled_summary_columns`.
- **Phase 4:** cross-repo parity tests vs cellpy's `make_step_table` / `make_summary`.
