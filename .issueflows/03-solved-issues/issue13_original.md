# Issue #13: Migrate the step/summary compute engine to polars (native schema)

Source: https://github.com/cellpy/cellpy-core/issues/13

## Original issue text

Follow-up spun out of #12 (which was descoped to bringing `CellpyLimits` + settling the step-type constants).

## Goal

Migrate the cellpy-core compute engine (`make_step_table` **and** the summary path) from pandas to **polars-native**, operating on the native `config` schema, while keeping the `cellpy` integration seam working.

## Why this is non-trivial (blockers found in #12)

1. **The whole engine is pandas + legacy-schema only.** Both `summarizers.py` and `selectors.py` use `pandas.groupby` and read legacy `*_txt` names (`charge_capacity_txt`, `cycle_index_txt`, …) that exist only on `HeadersNormal`; they operate on pandas `data.raw` / `data.summary`. There is no working native polars path today — it must be written from scratch while keeping the legacy seam byte-stable for cellpy.
2. **Native `RawCols` lacks columns the step engine needs:** no `step_time`, `internal_resistance`, `ref_voltage`; capacity is only `step_cumulative_charge_capacity` / `step_cumulative_discharge_capacity` (no plain `charge_capacity`); no energy/power.
3. **Native `StepCols` != legacy `HeadersStepTable`:** native uses `_mean`/`potential`/`charge_capacity`; legacy uses `_avr`/`voltage`/`charge` and additionally has `rate_avr`, `ir`, `ir_pct_change`, `type`, `info`, `ustep` (produced by the engine and consumed by cellpy). Native `StepCols` also lists `power_capacity_*` / `*_energy_*` that the native raw cannot supply.

## Decisions to honour (from #12 planning)

- Migrate step **and** summary paths together (avoid a split engine).
- Native step table always emits the full `StepCols` set, filling null/NaN where the source signal is absent from `data.raw`.
- Keep the cellpy seam working: either a pandas<->polars + legacy<->native bridge in `OldCellpyCellCore`, or **extend the native schema first** (preferred — resolves blockers 2 & 3) then rewrite.
- Step-detection thresholds come from `CellpyLimits` (already in `legacy.py`, landed in #12); cellpy passes its own `raw_limits` by value.

## Tasks

- [ ] Extend native `RawCols`/`StepCols` to represent the step-table output (step_time, internal_resistance, capacity vs cumulative, rate/type/ir columns).
- [ ] Rewrite `make_step_table` to polars-native + full `StepCols` (null/NaN for absent signals).
- [ ] Rewrite the summary path (`summarizers` summary functions + `selectors`) to polars-native.
- [ ] pandas<->polars / legacy<->native bridge in `OldCellpyCellCore` (handle pandas index + duplicate-column tolerance vs polars).
- [ ] Cross-repo parity tests vs cellpy's `make_step_table` / `make_summary`.

## References

- Design note: `.issueflows/04-designs-and-guides/step-table-polars-migration.md`
- Origin issue: #12
- Integration design: `.issueflows/04-designs-and-guides/cellpy-core-integration-into-cellpy.md`
- Consumer-side tracking: jepegit/cellpy#377
