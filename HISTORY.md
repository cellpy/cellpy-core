# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Add `test_id` to `StepCols`/`CycleCols` and key all per-step/per-cycle aggregation,
  cumulation, and joins on the composite `(test_id, cycle_num, step_num, …)` so a
  merged `Data` holding many tests never mixes cycles across tests (default `test_id=0`
  for a single unmerged test; single-test goldens stay byte-identical) (#41).
- Promote `CellpyUnits` into `cellpycore.units` (first-class unit-spec module) with a
  `legacy.py` re-export, plus converter-parity and pint-optional guard tests (STEP-12, #40).
