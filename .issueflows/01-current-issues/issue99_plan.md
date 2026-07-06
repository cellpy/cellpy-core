# Issue #99 — plan: align `nom_cap` -> `nom_cap_abs` naming (with deprecation path)

## Goal

Make the absolute-nominal-capacity parameter name consistent across the native
step and summary entry points: canonical name **`nom_cap_abs`** everywhere,
with a deprecation path for the old `nom_cap` keyword. Clarify
`current_conversion_factor` vs `specific_converters` in the docs (no rename —
they are different things).

## Constraints

- Issue selects **option 2 (API alignment, breaking)** with an explicit
  "deprecation path + tests updated" note — so unlike #98 (which dropped
  params outright), the renamed functions keep a deprecated `nom_cap`
  keyword alias that warns (`DeprecationWarning`) and forwards.
- Issue comment (@jepegit): after the #98 split, the `nom_cap` parameter
  belongs to the `add_step_c_rate` seam — the rename targets that function
  plus the summary helpers, not the base `make_step_table` (which no longer
  has the param).
- **Legacy bridge untouched.** `OldCellpyCellCore.make_core_step_table`
  mirrors legacy cellpy's signature across the seam (`add_c_rate` /
  `nom_cap`); golden byte parity must stay green (`tests/test_golden.py`,
  `tests/test_legacy_selectors.py` drive the bridge and keep `nom_cap=`).
- `CellMeta.nom_cap` / `nom_cap_specifics` (metadata) stay as-is: there
  `nom_cap` is qualified by `nom_cap_specifics` and mirrors cellpy metadata;
  same for `units.converters` (`value` + `nom_cap_specifics` API).
- `current_conversion_factor` (current-unit factor for C-rate columns) and
  `specific_converters` (mode -> specific-capacity factor mapping) have
  different semantics; docs-only clarification, no rename.
- KISS: one tiny shared deprecation helper, no general kwargs machinery.

### Prior art

- #98 (`step-c-rate-split.md`, `issue98_plan.md`): established the
  `add_step_c_rate` seam this rename lands on; #98 rejected deprecation shims,
  but #99 explicitly requests them — follow the issue.
- `add_scaled_summary_columns(nom_cap_abs=...)` (`cell_core.py`): already uses
  the target name — the anchor of the rename.
- Toolbox `.issueflows/00-tools/`: nothing relevant. Graph report skimmed.

## Approach

Canonical name `nom_cap_abs` (self-documenting: absolute capacity, e.g. Ah;
matches the existing `add_scaled_summary_columns` param). Renames, each with
`nom_cap_abs: float = <old default>` plus keyword-only deprecated
`nom_cap: Optional[float] = None`:

1. `summarizers.add_step_c_rate` (`nom_cap=1.0` -> `nom_cap_abs=1.0`).
2. `summarizers.equivalent_cycles_to_summary` (same).
3. `summarizers.c_rates_to_summary` (same).
4. `merge.update_data` (keyword-only `nom_cap=1.0` -> `nom_cap_abs=1.0`).
5. `CellpyCellCore.make_core_step_table` (`nom_cap: Optional[float] = None`
   -> `nom_cap_abs`).
6. `CellpyCellCore.update_core_data` (`nom_cap=1.0` -> `nom_cap_abs=1.0`).
7. Private `_step_c_rate_expr(shdr, nom_cap)` param renamed for consistency
   (no deprecation, private).

Deprecation helper in `summarizers.py`:

```python
def _resolve_nom_cap_abs(nom_cap_abs, nom_cap):
    if nom_cap is not None:
        warnings.warn(
            "`nom_cap` is deprecated; use `nom_cap_abs`",
            DeprecationWarning, stacklevel=3,
        )
        return nom_cap
    return nom_cap_abs
```

reused by `merge.py` and `cell_core.py`. Positional callers are unaffected
(the parameter keeps its position); `nom_cap=` keyword callers get the warning
and correct behavior.

Docs:

- Update all native examples `nom_cap=` -> `nom_cap_abs=`: `docs/index.md`,
  `docs/getting-started.md`, `docs/user-guide/standalone-use.md`,
  `docs/examples/quickstart.md` + `.ipynb`,
  `docs/examples/real_data_walkthrough.md` + `.ipynb`,
  `docs/specifications/step-table.md`, `cell_core.py` class docstring example.
- `standalone-use.md`: extend the "Units by value" contract bullet into a
  short glossary: `nom_cap_abs` = absolute nominal capacity (same unit as the
  raw capacity columns, e.g. Ah) used by both the per-step C-rate and the
  summary normalization; `current_conversion_factor` converts raw current
  units for the per-cycle C-rate columns; `specific_converters` maps
  `mode -> factor` for the specific (gravimetric/areal/absolute) capacity
  columns.
- `SCRATCHPAD.md`: mark the #99 "Unclear example" entry resolved.
- Design note: short entry in `.issueflows/04-designs-and-guides/`
  (nom-cap-naming) recording canonical name + deprecation decision.
- `HISTORY.md`: bullet under `[Unreleased]` (breaking-ish rename with
  deprecation path).

## Files to touch

- `src/cellpycore/summarizers.py` — renames 1-3 + helper + `_step_c_rate_expr`.
- `src/cellpycore/merge.py` — `update_data` rename + forwarding.
- `src/cellpycore/cell_core.py` — native `make_core_step_table`,
  `update_core_data`, class-docstring example; bridge untouched.
- `tests/test_schema.py`, `tests/test_merge.py`, `tests/test_e2e.py`,
  `tests/test_units_optional.py` — native call sites -> `nom_cap_abs=`; new
  test: deprecated `nom_cap=` warns `DeprecationWarning` and still scales
  (cover `add_step_c_rate` + `make_core_step_table`).
- `tests/test_golden.py`, `tests/test_legacy_selectors.py` — unchanged
  (bridge seam keeps `nom_cap`).
- Docs listed above; `SCRATCHPAD.md`; `HISTORY.md`; new design note.

## Test strategy

- `uv run pytest` (golden parity + e2e must stay green).
- `uv run ruff check` + `uv run ruff format --check`.
- New deprecation-warning tests as above.
- Sanity pipeline run on the vendored fixture with the new kwarg names.

## Open questions

- None blocking. Direction chosen: `nom_cap_abs` (not collapsing to
  `nom_cap`) because the metadata field `CellMeta.nom_cap` is
  specifics-qualified and the explicit `_abs` suffix is the whole point of
  the issue.
