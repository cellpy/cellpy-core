# Per-step C-rate split (`add_step_c_rate`)

Issue: [#98](https://github.com/cellpy/cellpy-core/issues/98)

## Context

The per-step C-rate (`c_rate`, legacy `rate_avr`) used to be computed inside
`summarizers.make_step_table` behind an `add_c_rate=True` flag. Per-cycle
scaled/derived columns were already appended in separate steps
(`c_rates_to_summary`, `add_scaled_summary_columns`), so the step table was the
odd one out.

## Decision

- `summarizers.make_step_table` builds the **base step table only** (no
  `add_c_rate` / `nom_cap` parameters).
- `summarizers.add_step_c_rate(data, schema=None, nom_cap=1.0)` is the separate
  opt-in step that appends `c_rate = abs(round(current_mean / nom_cap,
  DIGITS_C_RATE))`. The shared expression lives in `_step_c_rate_expr` (also
  used on bare step frames by `merge.update_data` and the bridge).
- Layered defaults:
  - Native `CellpyCellCore.make_core_step_table` keeps `nom_cap` and **always**
    chains both (its `make_core_summary` calls `c_rates_to_summary`, which
    needs the column).
  - Legacy bridge `OldCellpyCellCore.make_core_step_table` keeps the
    `add_c_rate` / `nom_cap` kwargs (old cellpy calls it across the seam) and
    applies the C-rate before the legacy rename/reorder — byte parity with the
    golden fixtures is unchanged.
  - `merge.update_data` appends `c_rate` to the rebuilt step rows only when the
    kept steps carry it, so vertical concat schemas always match.

## Alternatives considered

- Deprecated flag with warning on `make_step_table`: rejected — pre-1.0 core,
  cellpy pins exact versions, KISS.
- Keeping `c_rate` in its old column position (before `step_type`): rejected —
  nothing asserts the native frame order; the bridge reorders explicitly.
