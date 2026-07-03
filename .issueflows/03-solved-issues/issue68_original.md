# Issue #68: Units fallback: replace crashing data.<attr> fallback with explicit values or CellMeta

Source: https://github.com/cellpy/cellpy-core/issues/68

## Original issue text

Deferred from #66 (code review 2026-07, item D4/A2).

`units.get_converter_to_specific` reads `data.raw_units`, `data.mass`, `data.active_electrode_area`, `data.volume`; `nominal_capacity_as_absolute` reads `data.nom_cap_specifics`, `data.nom_cap`. The core `Data` class has none of these attributes, so the fallback path (taken whenever a caller omits `specific_converters` in `add_scaled_summary_columns`) raises `AttributeError` for standalone cellpy-core users.

Make these functions take explicit values or a `metadata.CellMeta` (which already has `mass`, `active_electrode_area`, `nom_cap`, `nom_cap_specifics`) — a natural fit with the metadata-boundary decision. Also remove the pointless `try/except Exception: raise` block in `nominal_capacity_as_absolute`.

See `.issueflows/04-designs-and-guides/code-review-2026-07.md` (A2, D4).
