# Nominal-capacity parameter naming (`nom_cap_abs`)

Issue: [#99](https://github.com/cellpy/cellpy-core/issues/99)

## Context

After the #98 split, the absolute nominal capacity appeared under two names:
`nom_cap` (`add_step_c_rate`, `make_core_step_table`, `c_rates_to_summary`,
`equivalent_cycles_to_summary`, `update_data`) and `nom_cap_abs`
(`add_scaled_summary_columns`), which made the standalone quickstart example
confusing.

## Decision

- Canonical name: **`nom_cap_abs`** on all native entry points. It is always
  the absolute capacity (same unit as the raw capacity columns, e.g. Ah),
  and the `_abs` suffix distinguishes it from the specifics-qualified
  metadata field `CellMeta.nom_cap` (+ `nom_cap_specifics`).
- **Deprecation path** (issue selected option 2 with deprecation): each
  renamed function keeps a keyword-only `nom_cap=None` alias that emits a
  `DeprecationWarning` and forwards (shared helper
  `summarizers._resolve_nom_cap_abs`). Positional callers are unaffected
  (the parameter keeps its position).
- **Legacy bridge untouched:** `OldCellpyCellCore.make_core_step_table`
  keeps `add_c_rate` / `nom_cap` — it mirrors legacy cellpy's signature
  across the seam and must not warn.
- `current_conversion_factor` (current-unit factor for the per-cycle C-rate
  columns) and `specific_conversion_factors` (mode -> factor for specific
  capacity columns; deprecated alias `specific_converters`) are semantically
  different; both use the `_conversion_factor(s)` suffix and the relationship
  is documented in the glossary in `docs/user-guide/standalone-use.md`.

## Alternatives considered

- Collapse to `nom_cap` everywhere: rejected — clashes conceptually with the
  specifics-qualified metadata `nom_cap`, and the explicit `_abs` is the
  clarity the issue asked for.
- Hard rename without deprecation (like #98): rejected — the issue explicitly
  requested a deprecation path.
