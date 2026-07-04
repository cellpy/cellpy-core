# Issue #68 plan: units fallback → explicit values / `CellMeta`

## Goal

Stop `get_converter_to_specific` and `nominal_capacity_as_absolute` from crashing on bare `Data` when callers omit `specific_converters`. Accept explicit scalars or `metadata.CellMeta`, keep cellpy duck-typed objects working, and fail with clear errors when required inputs are missing.

## Constraints

- **Metadata boundary** ([cellpy-core-migration.md](../04-designs-and-guides/cellpy-core-migration.md) §4): core must not require populated metadata on `Data`; `CellMeta` is opt-in scaffolding.
- **Units boundary** ([cellpy-core-integration-roadmap.md](../04-designs-and-guides/cellpy-core-integration-roadmap.md) STEP-12): pint stays optional (`units` extra); hot path still passes conversion factors **by value** via `specific_converters`.
- **Back-compat**: cellpy's richer data object (attrs on `.data`) must keep working without changes upstream in this PR.
- **Parity**: existing golden floats in `tests/test_units_converters.py` must stay green.
- **Scope**: `units.py` + thin `cell_core` wiring + tests only — no `CellpyUnits` promotion, no cellpy delegation.

### Prior art

- `cellpycore.units.get_converter_to_specific` / `nominal_capacity_as_absolute` — verbatim cellpy ports; duck-read `data.<attr>` today ([units.py](../../src/cellpycore/units.py)).
- `CellpyCellCore._resolve_specific_converter` — only pint touch on summary path when `specific_converters` omitted ([cell_core.py](../../src/cellpycore/cell_core.py) ~382–399).
- `metadata.CellMeta` — has `mass`, `active_electrode_area`, `nom_cap`, `nom_cap_specifics`; no `volume` / `raw_units` ([models.py](../../src/cellpycore/metadata/models.py)).
- `tests/test_units_converters.py` — `_stub()` `SimpleNamespace` parity goldens (issue #40).
- `tests/test_units_optional.py` — pint-absent guard; `_DummyData` fakes attrs pre-pint.
- `tests/test_schema.py::test_native_add_scaled_summary_columns_end_to_end` — always passes `specific_converters` (bypasses broken fallback).
- Toolbox: none relevant (`00-tools/` empty).

## Approach

### 1. Shared resolution helper(s) in `units.py`

Add small private helpers (one generic `_resolve_attr` or per-field) with precedence:

1. **Explicit kwarg** (e.g. `mass=`, `raw_units=`, `nom_cap=`)
2. **`cell_meta: CellMeta | None`**
3. **Duck-typed `data`** — `getattr(data, name, None)` only when not `None` (cellpy bridge)
4. **`ValueError`** with actionable message (mode + which fields missing)

`raw_units`: explicit `from_units` kwarg → duck `data.raw_units` → default `CellpyUnits()` (documented; matches “assume cellpy default units” when loader units unknown).

`volume` (volumetric): explicit `value` only — `CellMeta` has `electrolyte_volume`, not electrode volume; do not map unless issue expands scope.

### 2. `get_converter_to_specific`

- Add optional kwargs: `cell_meta`, and/or explicit `mass`, `active_electrode_area`, `volume` (mode-dependent).
- Keep `data` parameter (may be `None`) for signature stability and cellpy callers.
- Apply resolution per mode before pint math.
- Unknown mode → still return `1.0` (unchanged).

### 3. `nominal_capacity_as_absolute`

- Add optional `cell_meta: CellMeta | None`.
- Explicit `value`, `specific`, `nom_cap_specifics` already exist — wire resolution: kwarg → `cell_meta` → duck `data`.
- Add optional `raw_units` kwarg (default chain above) instead of only `data.raw_units` for `convert_charge_units=True`.
- **Delete** the `try/except Exception as e: raise e` block; let pint errors propagate naturally.

### 4. `cell_core` fallback path

- Add optional `cell_meta: CellMeta | None = None` to `add_scaled_summary_columns` on `CellpyCellCore` (inherited by `OldCellpyCellCore`).
- Thread `cell_meta` into `_resolve_specific_converter` → `get_converter_to_specific`.
- Docstring: bare `Data` without `specific_converters` **or** `cell_meta` (and required geometry for the mode) raises `ValueError` — not `AttributeError`.

No new attrs on `Data` itself (metadata boundary).

## Files to touch

| File | Change |
|------|--------|
| [`src/cellpycore/units.py`](../../src/cellpycore/units.py) | Resolution helpers; extend both public functions; remove pointless try/except |
| [`src/cellpycore/cell_core.py`](../../src/cellpycore/cell_core.py) | `cell_meta` on `add_scaled_summary_columns` + `_resolve_specific_converter` |
| [`tests/test_units_converters.py`](../../tests/test_units_converters.py) | `CellMeta` path tests; bare-missing-input `ValueError` tests; keep goldens |
| [`tests/test_units_optional.py`](../../tests/test_units_optional.py) | Adjust `_DummyData` / guard test if signature changes |
| [`tests/test_schema.py`](../../tests/test_schema.py) *(optional)* | One test: `add_scaled_summary_columns` without `specific_converters` but with `cell_meta` |

## Test strategy

```bash
uv run pytest tests/test_units_converters.py tests/test_units_optional.py -q
uv run pytest  # full suite before close
```

New cases:

- `get_converter_to_specific(cell_meta=CellMeta(mass=2.0), mode="gravimetric")` → same golden as `_stub()`.
- `nominal_capacity_as_absolute(cell_meta=CellMeta(...))` → gravimetric golden.
- `get_converter_to_specific(data=Data(), mode="gravimetric")` → `ValueError` mentioning `mass`.
- `add_scaled_summary_columns(..., specific_converters=None, cell_meta=...)` end-to-end on native polars summary (if not too heavy).

## Open questions

1. **`data` required vs optional** — plan keeps `data` as first positional arg (can be `None`) to avoid breaking cellpy; OK?
2. **`raw_units` default** — `CellpyUnits()` when nothing supplied (vs hard error). Recommended: default, document in docstring.
3. **Volumetric + `CellMeta`** — defer; volumetric still needs explicit `value` / duck `data.volume`. No `electrolyte_volume` mapping in this PR.
