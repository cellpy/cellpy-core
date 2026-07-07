# Issue #112 — plan: make unit conversion helpers more user-friendly

## Goal

Make the optional `cellpycore.units` standalone helpers self-explanatory at the
call site: document implicit default units, and let callers override them
(without breaking existing float-only usage from #110).

## Constraints

- **Back-compat:** existing calls like
  `calculate_nom_cap_abs_from_specific(3000.0, 2.0)` must keep the same result
  (defaults = `CellpyUnits()`).
- **Pint stays optional** (`units` extra); no new runtime deps; engine hot path
  unchanged.
- **KISS:** one small shared coercion helper; extend signatures additively only.
- **Scope:** all `cellpycore.units` conversion helpers (standalone + data-object /
  `CellMeta` paths) + docs/tests in cellpy-core. Do not refactor cellpy's
  `CellpyCell` reader or the legacy bridge in this issue.

### Prior art

- [`CellpyUnits`](src/cellpycore/units/spec.py) — canonical default unit strings
  (`nominal_capacity="mAh/g"`, `mass="mg"`, `charge="mAh"`, …). All bare-float
  helpers today assume these when building pint quantities.
- [`calculate_nom_cap_abs_from_specific`](src/cellpycore/units/converters.py) —
  gravimetric path delegates to `nominal_capacity_as_absolute`; areal/absolute
  paths use `get_cellpy_units()` internally. **No per-value unit override**
  except `raw_units` for charge conversion.
- [`calculate_specific_conversion_factors`](src/cellpycore/units/converters.py) —
  accepts `from_units` / `to_units` for charge, but `mass` / `area` floats still
  assume cellpy mass/area units (docstring says so; easy to miss).
- [`calculate_current_conversion_factor`](src/cellpycore/units/converters.py) —
  already explicit (`raw_current_unit` required). No change needed beyond docs
  cross-link.
- [`MockCore._check_value_unit`](src/cellpycore/legacy/mock_core.py) — parses
  `"3.579 mAh/g"`-style strings via `Q(value)`; candidate to lift (without the
  mock's side-effect of mutating `cellpy_units`).
- [`docs/user-guide/standalone-use.md`](docs/user-guide/standalone-use.md) —
  shows helper usage (#110) but does **not** list default input units; glossary
  covers engine knobs (`nom_cap_abs`, factors) not helper inputs.
- [`tests/test_units_converters.py`](tests/test_units_converters.py) — golden
  parity tests; all use default `CellpyUnits()`.
- Toolbox: none (`.issueflows/00-tools/` empty). Graph community 35 = units
  module.

## Approach

### 1. Answer the issue directly (defaults today)

Document that bare floats mean **cellpy_units** from [`CellpyUnits()`](src/cellpycore/units/spec.py):

| Helper | Param | Default unit | Output |
| --- | --- | --- | --- |
| `calculate_nom_cap_abs_from_specific` | `nom_cap` (gravimetric) | `mAh/g` | `Ah` |
| | `specific` (gravimetric) | `mg` | |
| | `nom_cap` (areal) | `mAh/cm**2` | `Ah` |
| | `specific` (areal) | `cm**2` | |
| `calculate_specific_conversion_factors` | `mass` | `mg` | dimensionless factor |
| | `area` | `cm**2` | |
| `calculate_current_conversion_factor` | `raw_current_unit` | *(caller must pass)* | dimensionless |

Note for docs: a cellpy session's metadata is **intended** to be in cellpy_units
(`mAh/g`, not `Ah/g`) per `CellpyUnits.nominal_capacity`; if the user's `3.579`
is actually `Ah/g`, they must say so explicitly after this fix.

### 2. Shared coercion helper (internal)

Add `_as_quantity(value, default_unit: str)` in `converters.py`:

- `int` / `float` → `Q(value, default_unit)`
- `str` → `Q(value)` (pint parses `"3.579 mAh/g"`, `"1.334 mg"`, …)
- reject ambiguous / unitless strings with a clear `ValueError`

No public export unless we find a second consumer outside converters.

### 3. Extend standalone helper signatures (additive)

**`calculate_nom_cap_abs_from_specific`**

```python
def calculate_nom_cap_abs_from_specific(
    nom_cap: float | str,
    specific: float | str,
    *,
    specific_type: str = "gravimetric",
    nom_cap_unit: str | None = None,      # default from CellpyUnits
    specific_unit: str | None = None,     # mass or area unit by type
    cellpy_units: CellpyUnits | None = None,  # bulk override for defaults
    ...
) -> float:
```

- Resolve default unit strings from `cellpy_units or CellpyUnits()`.
- Coerce `nom_cap` / `specific` through `_as_quantity`.
- Refactor gravimetric branch to pass coerced quantities into
  `nominal_capacity_as_absolute` (add optional `nom_cap_unit` / `specific_unit`
  there too, or an internal `_nominal_capacity_from_quantities` to avoid
  duplicating pint math).

**`calculate_specific_conversion_factors`**

- Accept `mass: float | str | None`, `area: float | str | None`.
- Add optional `mass_unit`, `area_unit` (default from `cellpy_units`).
- Coerce before calling `get_converter_to_specific`.

**`get_converter_to_specific`** (data-object path — confirmed in scope)

- Accept `value`, `mass`, `active_electrode_area`, `volume` as `float | str`.
- Add optional `mass_unit`, `area_unit`, `volume_unit` plus bulk
  `cellpy_units: CellpyUnits | None = None` (defaults from resolved spec).
- Coerce scale inputs through `_as_quantity` before building pint quantities.
- Resolution order unchanged: explicit kwarg → `cell_meta` → duck-typed `data`
  attr; coercion applies after resolution.

**`nominal_capacity_as_absolute`** (data-object path — confirmed in scope)

- Accept `value` and `specific` as `float | str`.
- Add optional `nom_cap_unit`, `specific_unit`, `cellpy_units`.
- When resolving from `cell_meta` / `data`, attrs remain plain floats in
  cellpy_units (existing behaviour); coercion + unit kwargs apply when caller
  passes `value` / `specific` explicitly (standalone or data-object).

### 4. Documentation

- Expand [standalone-use.md](docs/user-guide/standalone-use.md) **Unit conversion**
  section: defaults table, three usage patterns (defaults, explicit unit kwargs,
  quantity strings). Include the issue's example both ways:

  ```python
  # implicit cellpy defaults (mAh/g, mg)
  units.calculate_nom_cap_abs_from_specific(3.579, 1.334)

  # explicit units
  units.calculate_nom_cap_abs_from_specific(
      3.579, 1.334, nom_cap_unit="Ah/g", specific_unit="mg"
  )

  # quantity strings
  units.calculate_nom_cap_abs_from_specific("3.579 Ah/g", "1.334 mg")
  ```

- Update Google docstrings on touched public functions (Args must state default
  units when param is a bare float).

### 5. Ordering

1. `_as_quantity` + `_default_unit(cellpy_units, key)` helper
2. `nominal_capacity_as_absolute` + `get_converter_to_specific` (shared coercion)
3. `calculate_nom_cap_abs_from_specific` + `calculate_specific_conversion_factors`
4. Docs
5. Tests (standalone + data-object / `CellMeta` paths)

## Files to touch

| File | Change |
| --- | --- |
| [`src/cellpycore/units/converters.py`](src/cellpycore/units/converters.py) | `_as_quantity`; coercion in all conversion helpers |
| [`tests/test_units_converters.py`](tests/test_units_converters.py) | Defaults unchanged; quantity strings, unit kwargs, `cellpy_units`; data-object / `CellMeta` cases |
| [`docs/user-guide/standalone-use.md`](docs/user-guide/standalone-use.md) | Defaults table + examples |
| [`HISTORY.md`](HISTORY.md) | Unreleased bullet (user-facing API clarity) |

## Test strategy

```bash
uv run pytest tests/test_units_converters.py tests/test_units_optional.py -q
uv run ruff check && uv run ruff format --check
```

New tests (pint required, same as existing file):

- `calculate_nom_cap_abs_from_specific("3.579 Ah/g", "1.334 mg")` matches
  explicit-unit / converted golden.
- `nom_cap_unit="Ah/g"` with float `3.579` matches above.
- `calculate_specific_conversion_factors(mass="2 mg", …)` still returns existing
  golden dict.
- `get_converter_to_specific(..., mass="2 mg")` and via `CellMeta` unchanged
  golden; `mass="2 g"` + `cellpy_units` override returns adjusted factor.
- `nominal_capacity_as_absolute(value="1000 mAh/g", specific="0.5 mg", …)` matches
  float golden.
- `_as_quantity("not a quantity")` raises `ValueError`.

## Decisions (confirmed)

1. **Both** quantity strings **and** per-param unit kwargs (`nom_cap_unit`, etc.).
2. **Include** bulk `cellpy_units=` override on all touched helpers.
3. **Widen** `get_converter_to_specific` and `nominal_capacity_as_absolute`
   (data-object + `CellMeta` paths), not standalone-only.

**Status:** Accepted — ready for `/iflow-start`.
