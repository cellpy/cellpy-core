# Step/summary engine: polars-native migration (deferred)

Durable record of why the cellpy-core compute engine is still pandas, what blocks the
polars rewrite, and the design decisions to honour when it is done. Spun out of issue #12;
tracked in **issue #13**.

## Context

- `make_step_table` was ported to core in PR #9 and is driven by `cellpy` across the seam
  (`cellreader.py::make_step_table` → `OldCellpyCellCore.make_core_step_table` →
  `summarizers.make_step_table`). It works and is tested (`tests/test_schema.py`).
- Issue #12 also asked to "bring `CellpyLimits`" and (per a later comment) to move the
  engine to **polars**. Phase 1 of #12 brought `CellpyLimits` (in `legacy.py`) and derived
  `DEFAULT_RAW_LIMITS` from it. The polars rewrite was **descoped** to this follow-up.

## Why the polars rewrite is non-trivial (blockers)

1. **The whole engine is pandas + legacy-schema only.** Both `summarizers.py` and
   `selectors.py` use `pandas.groupby` and read legacy `*_txt` names
   (`charge_capacity_txt`, `cycle_index_txt`, …) that exist only on `HeadersNormal`. They
   operate on pandas `data.raw` / `data.summary`. There is no working native polars path
   today to "make consistent" — it must be written from scratch while keeping the legacy
   seam byte-stable for cellpy.
2. **Native `RawCols` lacks columns the step engine needs:** no `step_time`,
   `internal_resistance`, `ref_voltage`; capacity is only `step_cumulative_charge_capacity`
   / `step_cumulative_discharge_capacity` (no plain `charge_capacity`); no energy/power.
3. **Native `StepCols` ≠ legacy `HeadersStepTable`:** native uses `_mean`/`potential`/
   `charge_capacity`; legacy uses `_avr`/`voltage`/`charge` and additionally has
   `rate_avr`, `ir`, `ir_pct_change`, `type`, `info`, `ustep` (produced by the engine and
   consumed by cellpy). Native `StepCols` also lists `power_capacity_*` / `*_energy_*` that
   the native raw cannot supply.

## Decisions to honour in the follow-up

- **Engine consistency:** migrate step *and* summary paths together (avoid a split engine).
- **Column policy:** the native step table should always emit the full `StepCols` set,
  filling null/NaN where the source signal is absent from `data.raw`.
- **Keep the cellpy seam working:** either a pandas↔polars + legacy↔native bridge in
  `OldCellpyCellCore`, or extend the native schema first (preferred — resolves the gaps in
  blockers 2 & 3) and then rewrite.
- **Limits:** step-detection thresholds come from `CellpyLimits` (already in `legacy.py`);
  cellpy passes its own `raw_limits` by value.

## Prep done (de-risks this rewrite)

- **Real-data regression oracle in place** (`tests/test_golden.py`): the engine is
  pinned against cellpy's published goldens (103 steps / 18 cycles / cycle-1
  `data_point` 1457) on a real Arbin frame, plus a frozen step-table snapshot. The
  polars rewrite must keep these green. Fixtures + regen script + best-practice are
  described in `test-data-and-fixtures.md`.
- **Edge case to fix during the rewrite:** on the tiny 47-row fixture the engine
  leaves one step's `type` blank (`''`) — revisit step-type classification.

## Related

- Issue #12 (this work's origin): `.issueflows/03-solved-issues/issue12_*` once closed.
- Test-data strategy & oracle: `test-data-and-fixtures.md`.
- Integration design: `cellpy-core-integration-into-cellpy.md`.
- Header harmonization: `column-headers-review.md`, cellpy/cellpy-core#4 (SPEED-30).
- Contract tests for the legacy mirrors: jepegit/cellpy#378.
