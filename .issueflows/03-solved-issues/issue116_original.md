# Issue #116 — Stage 1.14: legacy mapping extensions — postfix expansion + attribute-level table

GitHub: https://github.com/cellpy/cellpy-core/issues/116
Labels: cellpy2-stage1, yolo

## Goal

Two additive pieces in `cellpycore.legacy.mapping`:

- `expand_specific_columns(rename, modes)` — the `{col}_{gravimetric|areal|absolute}`
  postfix expansion currently inlined in `OldCellpyCellCore.add_scaled_summary_columns`
  (cell_core.py:1086–1092), lifted so the bridge and the future file-importer share it.
- `LEGACY_ATTR_TO_SCHEMA` — attribute-level table (legacy attribute name → native
  schema path, e.g. `voltage_txt → raw.potential`), needed because the value-based
  mapping cannot serve the accessor shim; ~60 attributes cover everything the utils use.
  Handle the duplicate-value pair (`HeadersSummary.discharge_capacity` vs
  `discharge_capacity_raw`) explicitly.

## Acceptance

- Totality + bijectivity tests extended; bridge re-pointed at `expand_specific_columns`
  with byte-identical goldens; release tagged for cellpy re-pin.
