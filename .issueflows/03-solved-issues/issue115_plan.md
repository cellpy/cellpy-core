# Plan — issue #115 (Stage 1.13)

All three helpers live in `src/cellpycore/units/converters.py` (behind the lazy
pint import; nothing touches the compute hot path) and are exported from
`cellpycore.units`.

1. **Label-alias decision (the `"C"` pitfall).** pint parses bare `"C"` as
   *coulomb* and rejects the spec's lowercase `"hz"` outright (verified against
   the installed pint). Decision: a small per-property alias table
   `_PINT_LABEL_ALIASES` maps `temperature: "C" → "degC"` and
   `frequency: "hz" → "Hz"` for parsing/validation only — the spec keeps its
   legacy labels, so nothing user-visible changes.
2. **`convert_value`** — port of legacy `CellpyCell.to_cellpy_unit`,
   generalized: number → `Q(v, from_units[prop])`; quantity string → parsed by
   pint (unitless strings rejected, same rule as `_as_quantity`); `(value,
   unit)` tuple → `Q(*value)`; unknown property → `KeyError`. Defaults:
   `CellpyUnits()` on both sides (raw → cellpy direction).
3. **`calculate_scaler(from_unit, to_unit)`** — `Q(1, a).to(b).m`; offset units
   (degC) raise by pint design, documented (use `convert_value` for
   temperatures). cellpy's `unit_scaler_from_raw(unit, prop)` becomes
   `calculate_scaler(raw_units[prop], unit)`.
4. **`validate_units(units, strict=True)`** — accepts `CellpyUnits` or plain
   mapping; every label must be a string (floats → `TypeError` naming the v7
   artifact) and pint-parsable through the alias table (else `ValueError`, or
   warning when `strict=False` — the `local_instrument` escape hatch); unknown
   keys are warned about, label-checked, and left out of the returned spec;
   validated labels are layered over `CellpyUnits()` defaults.
5. **Tests** — appended to `tests/test_units_converters.py` (17 new cases) and
   the pint-optional guard extended so all three helpers raise the clear
   `ModuleNotFoundError` naming the `units` extra.
