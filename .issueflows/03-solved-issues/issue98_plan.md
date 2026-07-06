# Issue #98 — plan: split per-step C-rate out of `make_step_table`

## Goal

Remove the inline `add_c_rate` flag from the core step builder and provide the
per-step C-rate (`c_rate` / legacy `rate_avr`) via a separate opt-in function
(`summarizers.add_step_c_rate`), mirroring how per-cycle scaled/derived summary
columns are appended after `make_summary`.

## Constraints

- Legacy bridge byte parity must hold: golden fixtures (`tests/test_golden*` /
  `tests/data/`) and the legacy `HeadersStepTable` column order produced by
  `OldCellpyCellCore._legacy_step_column_order` (includes `rate_avr`) must be
  unchanged.
- `OldCellpyCellCore.make_core_step_table` mirrors legacy cellpy's
  `make_step_table` signature (cellpy calls it across the seam, see
  `step-table-polars-migration.md`); its `add_c_rate` / `nom_cap` kwargs must
  stay. Only the native core builder loses the flag.
- Native `CellpyCellCore.make_core_summary` calls `c_rates_to_summary`
  unconditionally, which reads `schema.step.c_rate` from `data.steps` — the
  orchestration layer must keep producing that column by default, otherwise the
  native pipeline breaks.
- `merge.update_data` rebuilds step rows via
  `make_step_table(from_data_point=…)` and vertically concats them with the
  kept steps; new rows must carry `c_rate` too or the concat fails on schema
  mismatch.
- Per-step stat columns stay a fixed engine contract; only `c_rate` honours the
  injected `StepCols` rename (unchanged).
- KISS: one new public function, no back-compat shims on the native API
  (pre-1.0 core; cellpy pins exact versions).

### Prior art

- `c_rates_to_summary`, `ir_to_summary`, `equivalent_cycles_to_summary`
  (`summarizers.py`) — post-summary append helpers taking
  `(data, schema=None, …) -> Data`; `add_step_c_rate` mirrors this shape.
- `CellpyCellCore.add_scaled_summary_columns` (`cell_core.py`) — the
  separate-step pattern named in the issue; coexist, no merge.
- Toolbox (`.issueflows/00-tools/`): empty — nothing to reuse.
- Guides: `step-table-polars-migration.md` (bridge seam + byte parity),
  `summary-extractors.md` checked.

## Approach

1. **`summarizers.py`**
   - Remove `add_c_rate` and `nom_cap` parameters (and the inline `if
     add_c_rate:` block) from `make_step_table`; it emits the base step table
     only. Update docstring.
   - Add module-level private `_step_c_rate_expr(shdr, nom_cap)` returning the
     polars expression `abs(round(current_mean / nom_cap, DIGITS_C_RATE))`
     aliased to `shdr.c_rate`.
   - Add public `add_step_c_rate(data, schema=None, nom_cap=1.0) -> Data`:
     requires `data.steps` (clear error when missing, matching
     `_require_frame`), accepts pandas for convenience, appends `c_rate` using
     the expression, returns `data`. `nom_cap=1.0` keeps the old default.
2. **`__init__.py`** — export `add_step_c_rate` next to `make_step_table`.
3. **`cell_core.py`**
   - Native `CellpyCellCore.make_core_step_table`: drop `add_c_rate`, keep
     `nom_cap: Optional[float] = None`; call the engine, then always append
     `c_rate` via `add_step_c_rate` (needed downstream by
     `make_core_summary`). For the `from_data_point` frame return, apply
     `_step_c_rate_expr` to the frame.
   - Bridge `OldCellpyCellCore.make_core_step_table`: keep `add_c_rate=True` /
     `nom_cap=None` kwargs (legacy API); call base `make_step_table`, then
     conditionally apply the C-rate step before the legacy rename, preserving
     byte parity.
4. **`merge.py` `update_data`** — keep the `nom_cap` param; after building the
   new step rows, apply `_step_c_rate_expr` so the concat schema matches.
   Strip `add_c_rate` from forwarded kwargs docs.
5. **Docs** — show the two-step flow (`make_step_table(data)` then
   `add_step_c_rate(data, nom_cap=…)`): `docs/index.md`,
   `docs/getting-started.md`, `docs/user-guide/standalone-use.md`,
   `docs/examples/quickstart.md` + `quickstart.ipynb`; note in
   `docs/specifications/step-table.md` that `c_rate` comes from
   `add_step_c_rate`.
6. **Design note** — short entry in
   `.issueflows/04-designs-and-guides/` (or extend `summary-extractors.md`)
   recording the split; drop the issue line from `SCRATCHPAD.md` backlog table.

## Files to touch

- `src/cellpycore/summarizers.py` — remove flag/params from `make_step_table`;
  add `_step_c_rate_expr` + `add_step_c_rate`.
- `src/cellpycore/__init__.py` — export `add_step_c_rate`.
- `src/cellpycore/cell_core.py` — native + bridge `make_core_step_table`
  reworked as above.
- `src/cellpycore/merge.py` — `update_data` applies C-rate to rebuilt rows.
- `tests/test_schema.py` — update `make_step_table(..., nom_cap=…)` call sites
  to the two-step flow; `test_nom_cap_scales_c_rate_by_value` now exercises
  `add_step_c_rate`; add tests: base builder emits no `c_rate`;
  `add_step_c_rate` respects injected `StepCols` rename; clear error when
  `data.steps` missing.
- `tests/test_e2e.py`, `tests/test_merge.py`, `tests/test_limits.py`,
  `tests/test_exclude_types.py`, `tests/test_benchmarks.py` — adjust call
  sites (drop `nom_cap=` kwarg / insert `add_step_c_rate` where the pipeline
  needs `c_rate`).
- Docs listed in Approach step 5; `SCRATCHPAD.md` backlog line.

## Test strategy

- `uv run pytest` (golden parquet e2e + legacy parity must stay green).
- `uv run ruff check && uv run ruff format --check`.
- New unit tests as listed under Files to touch.
- Sanity run of the native pipeline (`Data.from_raw_frame` →
  `make_step_table` → `add_step_c_rate` → `make_summary` +
  `c_rates_to_summary`) on the vendored fixture.

## Open questions

- Native step-frame column position of `c_rate` moves from
  "after stats, before `step_type`" to appended last. Nothing asserts the
  native frame order (spec-order tests check the `StepCols` dataclass, and the
  bridge reorders explicitly), so plan accepts the move. Flag if byte-order of
  the *native* frame matters to anyone downstream.
- Bridge keeps `add_c_rate` kwarg for legacy-cellpy compatibility — confirm
  that is the intended reading of "not a flag on the core step builder"
  (the flag survives only on `OldCellpyCellCore`).
