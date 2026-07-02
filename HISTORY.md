# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Add `summarizers.normalize_capacity_granularity` + `config.ResetGranularity`
  (`CYCLE`/`STEP`/`TEST`) to normalize step-cumulative or test-cumulative raw capacity /
  energy columns to the mandated cycle-cumulative convention before aggregation; a
  cycle-cumulative input is an exact no-op so the exercised path stays byte-stable (#42).
- Add `test_id` to `StepCols`/`CycleCols` and key all per-step/per-cycle aggregation,
  cumulation, and joins on the composite `(test_id, cycle_num, step_num, …)` so a
  merged `Data` holding many tests never mixes cycles across tests (default `test_id=0`
  for a single unmerged test; single-test goldens stay byte-identical) (#41).
- Promote `CellpyUnits` into `cellpycore.units` (first-class unit-spec module) with a
  `legacy.py` re-export, plus converter-parity and pint-optional guard tests (STEP-12, #40).
- Add native `ref_potential` (reference-electrode potential) to `RawCols` with the full
  `StepCols` aggregate set, wired through the polars step engine (aggregated when
  present, skipped when absent); legacy `reference_voltage` stays unbridged to preserve
  the legacy step-frame parity (#43).
