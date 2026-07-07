# Issue #99 — status

- [x] Done

## What's done

- Canonical parameter name `nom_cap_abs` across native entry points:
  `summarizers.add_step_c_rate`, `equivalent_cycles_to_summary`,
  `c_rates_to_summary`, `merge.update_data`,
  `CellpyCellCore.make_core_step_table`, `update_core_data`. Private
  `_step_c_rate_expr` param renamed too.
- Deprecation path: keyword-only `nom_cap=None` alias on each renamed function
  emits `DeprecationWarning` and forwards (shared
  `summarizers._resolve_nom_cap_abs`); positional callers unaffected.
- Legacy bridge `OldCellpyCellCore.make_core_step_table` untouched (keeps
  `add_c_rate` / `nom_cap`, old-cellpy seam); golden parity green.
- Tests updated to `nom_cap_abs=`; new tests:
  `test_deprecated_nom_cap_kwarg_warns_and_scales`,
  `test_deprecated_nom_cap_kwarg_on_make_core_step_table`.
- Docs: all native examples renamed (`index`, `getting-started`,
  `standalone-use`, quickstart md + ipynb, real-data walkthrough md + ipynb,
  step-table spec, `cell_core.py` class docstring); `standalone-use.md` gains
  a units-by-value glossary (`nom_cap_abs` vs `current_conversion_factor` vs
  `specific_converters`).
- `SCRATCHPAD.md` #99 entry marked resolved; design note
  `.issueflows/04-designs-and-guides/nom-cap-naming.md`; `HISTORY.md` bullet
  under `[Unreleased]`.
- Verified: `uv run pytest` (165 passed), `uv run pytest -m benchmark`
  (3 passed), `uv run ruff check` + `uv run ruff format --check` green;
  sanity pipeline run on the vendored fixture with new kwarg + deprecated
  alias (warns, values identical). graphify CLI not installed in this
  environment, graph not rebuilt.

## Remaining work

- None. PR [#107](https://github.com/cellpy/cellpy-core/pull/107) on branch
  `cursor/99-nom-cap-naming-12dd`. Post-merge: run `/iflow-cleanup`.
