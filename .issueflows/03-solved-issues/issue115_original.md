# Issue #115 — Stage 1.13: units — convert_value, calculate_scaler, validate_units

GitHub: https://github.com/cellpy/cellpy-core/issues/115
Labels: cellpy2-stage1, yolo

## Goal

Three additive helpers in `cellpycore.units` (behind the existing `units` extra):

- `convert_value(value, physical_property, from_units=None, to_units=None) -> float` —
  port of cellpy's `to_cellpy_unit` generalized (accepts number / pint-quantity string /
  `(value, unit)` tuple; defaults from raw→cellpy units).
- `calculate_scaler(from_unit, to_unit) -> float` — port of `unit_scaler_from_raw`
  (`Q(1, a).to(b).m`).
- `validate_units(units) -> CellpyUnits` — every label pint-parsable, warn on unknown
  keys; the loader-boundary validator (note the `"C"` Celsius-vs-Coulomb pitfall —
  decide `degC` handling here).

## Why

cellpy Stage 1.6 (jepegit/cellpy#451) deletes its duplicated converter bodies and needs
these to wrap; the loader port later calls `validate_units` on every configuration.
Additions cross the repos core-first (release + re-pin) per the merge-order rule.

## Acceptance

- Unit tests incl. quantity-string and tuple inputs, bad-label failures, temperature
  handling documented; pint-optional guard still green (helpers raise only when called).
- Tagged release cut so cellpy can re-pin (release-procedure.md).
