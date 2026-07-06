# Issue #98: Split per-step C-rate (add_c_rate) into separate post-step function

Source: https://github.com/cellpy/cellpy-core/issues/98

## Original issue text

## Context

Per-step C-rate (`rate_avr` / `shdr.c_rate`) is currently computed inside `make_step_table` when `add_c_rate=True`. For cycle summary, scaled/specific columns are already appended in a separate step (`add_scaled_summary_columns`).

Source: `SCRATCHPAD.md` (Add scaled step summary columns as separate step).

## Proposal

Move C-rate computation out of the core step engine into a separate optional function (mirroring the summary pattern):

```python
# Currently inside make_step_table when add_c_rate=True:
steps = steps.with_columns(
    (pl.col("current_mean") / _nom_cap)
    .round(DIGITS_C_RATE)
    .abs()
    .alias(shdr.c_rate)
)
```

- `make_step_table` / `make_core_step_table` should produce the base step table only.
- New helper (e.g. `add_step_c_rate` or similar) appends `c_rate` when the caller supplies `nom_cap`.
- Legacy bridge (`OldCellpyCellCore`) can call both to preserve byte parity.

## Pre-work

- [ ] Check downstream impact on cycle summary and legacy bridge goldens before removing the inline option.

## Acceptance criteria

- [ ] C-rate is opt-in via a separate function, not a flag on the core step builder
- [ ] Legacy parity tests / golden fixtures still pass
- [ ] Docs updated to show the two-step flow
