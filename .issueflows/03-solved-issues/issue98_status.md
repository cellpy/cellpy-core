# Issue #98 — status

- [x] Done

## What's done

- `summarizers.make_step_table` builds the base step table only (`add_c_rate` /
  `nom_cap` parameters removed); docstring points to the new two-step flow.
- New `summarizers.add_step_c_rate(data, schema=None, nom_cap=1.0)` (exported
  from `cellpycore`) appends `c_rate`; shared `_step_c_rate_expr` used on bare
  frames by `merge.update_data` and the legacy bridge.
- Native `CellpyCellCore.make_core_step_table` keeps `nom_cap`, drops the flag,
  and always chains base builder + `add_step_c_rate` (downstream
  `c_rates_to_summary` needs the column).
- Legacy bridge `OldCellpyCellCore.make_core_step_table` keeps `add_c_rate` /
  `nom_cap` kwargs (old-cellpy seam) and applies the C-rate before the legacy
  rename/reorder — golden byte parity preserved.
- `merge.update_data` appends `c_rate` to rebuilt step rows when the kept steps
  carry it (vertical concat schema match).
- Tests updated to the two-step flow; new tests: base builder emits no
  `c_rate`, `add_step_c_rate` schema rename + missing-steps error.
- Docs updated (`index`, `getting-started`, `standalone-use`, quickstart md +
  ipynb, step-table spec); design note
  `.issueflows/04-designs-and-guides/step-c-rate-split.md`; SCRATCHPAD entry
  marked resolved.
- Verified: `uv run pytest` (155 passed), `uv run pytest -m benchmark`
  (3 passed), `uv run ruff check` + `uv run ruff format --check` green;
  native pipeline sanity run on the vendored fixture. Graph rebuilt
  (`graphify update .`).

## Remaining work

- None. Closed via `/iflow-close`: `HISTORY.md` bullet added under
  `[Unreleased]` (no version bump requested), PR
  [#105](https://github.com/cellpy/cellpy-core/pull/105) open against `main`.
  Post-merge: run `/iflow-cleanup`.
