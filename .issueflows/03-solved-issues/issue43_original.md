# Issue #43: Native schema: add ref_potential/ref_voltage support

Source: https://github.com/cellpy/cellpy-core/issues/43

## Original issue text

Tracked gap from `.issueflows/04-designs-and-guides/step-table-polars-migration.md` (Phase 1: "`ref_potential` deferred — not present in the golden Arbin data, so not needed for parity yet").

## Scope

- Add `ref_potential` / `ref_voltage` to native `config.RawCols` (and the corresponding `StepCols` aggregate set if a consumer needs per-step reference voltage).
- Wire it through the polars step engine (aggregate like the other native raw signals; null where absent).
- Add a fixture that actually carries reference-electrode data so the column is exercised.

Lower priority / on-demand: deferred until a consumer or fixture with reference-electrode data needs it.
