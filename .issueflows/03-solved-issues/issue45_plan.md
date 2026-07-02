# Issue #45 plan: remove `create_selector` / `summary_selector_exluder` (two-repo cleanup)

## Goal

Migrate cellpy off `core_selectors.create_selector`, then delete both
`create_selector` and `summary_selector_exluder` from cellpy-core
(`src/cellpycore/selectors.py`), plus the dead `selector` parameter on
`make_core_summary`.

## Key finding (unblocks the issue)

Both `make_core_summary` implementations in `src/cellpycore/cell_core.py`
(native, line ~159; legacy bridge, line ~563) accept `selector` but **never use
it** — the polars engine selects cycle-end rows via `final_data_points`
internally. So the selector cellpy builds in `_make_summary`
(`cellpy/readers/cellreader.py:5794-5805`) and passes at line 5917 is already a
no-op, as are cellpy's public `selector` / `selector_type` / `exclude_types` /
`exclude_steps` kwargs on `make_summary`. Migration is therefore a pure
dead-code removal on the cellpy side too — no behavior replacement needed.

## Constraints

- **Merge order:** cellpy pins `cellpycore @ git+…@main`
  (`cellpy/pyproject.toml:61`). The cellpy PR (stop importing) must merge
  **before** the cellpy-core PR (delete functions), or cellpy breaks at its
  next pin resolution.
- **Branch, don't fork** (per `cellpy-core-migration.md`): cellpy work goes on
  a dedicated branch of the existing cellpy repo, e.g.
  `core45-drop-create-selector`. cellpy-core work stays on the existing
  branch `45-cleanup-blocked-remove-create_selectorsummary_selector_exluder-once-cellpy-migrates-off-them`.
- **Local dev wiring:** cellpy already has the editable
  `[tool.uv.sources] cellpycore = { path = "../cellpy-core", editable = true }`
  override, so both branches can be tested together locally.
- **User decisions (2026-07-02):** keep cellpy's `selector*` / `exclude*`
  kwargs but emit `DeprecationWarning` when supplied; also remove the dead
  `selector` parameter from both `make_core_summary` signatures in core.

### Prior art

- `selector-dead-code-deferral.md` (04-designs-and-guides) — the deferral
  decision this issue executes; update it when done.
- `code-review-2026-07.md` — notes #45 covers only these two functions;
  `get_step_numbers` / `get_cycle_numbers` / `get_rates` stay.
- Issue #24 removed the sibling pair `generate_absolute_summary_columns` /
  `end_voltage_to_summary`; `tests/test_schema.py::test_no_module_header_globals`
  shows the "assert name gone" test pattern to mirror.
- Toolbox (`.issueflows/00-tools/`) and graph checked: no relevant helper.

## Approach

### Phase 1 — cellpy (branch `core45-drop-create-selector`)

1. Create the branch from cellpy's default branch.
2. `cellpy/readers/cellreader.py`:
   - Remove `from cellpycore import selectors as core_selectors` (line 73).
   - In `_make_summary`: delete the selector-building block (lines 5794-5805)
     and stop passing `selector=selector` to `self.core.make_core_summary`
     (line 5917).
   - Emit `DeprecationWarning` when `selector`, `selector_type`,
     `exclude_types`, or `exclude_steps` is supplied (non-None) to
     `make_summary` — they have been no-ops since the core seam.
3. `tests/test_slim.py`: drop the `core_selectors` import; update
   `test_direct_core_make_core_summary` to call
   `make_core_summary(data, find_ir=True, find_end_voltage=True)` without a
   selector.
4. Run cellpy tests (conda `cellpy_dev_313`): at least `pytest tests/test_slim.py`
   plus summary-related tests (`-k summary`).

### Phase 2 — cellpy-core (existing branch for #45)

1. `src/cellpycore/selectors.py`: delete `create_selector` and
   `summary_selector_exluder`; remove now-unused imports/constants
   (`functools`, `FIRST`/`LAST`/`DELTA` if unused elsewhere — verify).
2. `src/cellpycore/cell_core.py`: remove the unused `selector` parameter from
   both `make_core_summary` signatures + docstrings.
3. `tests/test_schema.py`: extend the dead-code assertions with
   `create_selector` / `summary_selector_exluder` gone from `selectors`
   (mirror `test_no_module_header_globals`).
4. Docs: update `selector-dead-code-deferral.md` (resolved, date, link #45)
   and flip #45 in `cellpy-core-integration-roadmap.md` from blocked to done.
5. Run `uv run pytest`; rerun cellpy's `test_slim.py` against the edited core
   via the editable path source.

### Merge sequencing

cellpy PR merges first → then cellpy-core PR. Local editable wiring keeps both
testable during development.

## Files to touch

- `cellpy/cellpy/readers/cellreader.py` — remove import + selector block, add
  deprecation warnings.
- `cellpy/tests/test_slim.py` — drop selector usage.
- `cellpy-core/src/cellpycore/selectors.py` — delete the two functions.
- `cellpy-core/src/cellpycore/cell_core.py` — drop dead `selector` param (2 sites).
- `cellpy-core/tests/test_schema.py` — add removed-name assertions.
- `cellpy-core/.issueflows/04-designs-and-guides/selector-dead-code-deferral.md`,
  `cellpy-core-integration-roadmap.md` — status updates.

## Test strategy

- cellpy-core: `uv run pytest` (top dir) — includes `tests/test_golden.py`
  (golden parquet fixtures: 103 steps / 18 cycles / cycle-1 `data_point` 1457),
  which is the core-side parity oracle.
- cellpy: activate conda `cellpy_dev_313`, run `pytest tests/test_slim.py` and
  `pytest -k summary`.

### End-to-end verification (both branches together, before either PR)

With the cellpy branch checked out and the editable
`[tool.uv.sources]` path resolving `cellpycore` to the edited
`../cellpy-core` working copy (branch for #45):

1. Full seam pipeline via `tests/test_slim.py` — covers raw load
   (`arbin_res` `from_raw`) → `make_step_table` → `make_summary` →
   golden value (`summary.loc[1, data_point] == 1457`) → `save(.h5)`
   roundtrip, now without any selector import.
2. Full cellpy test suite: `pytest` (conda `cellpy_dev_313`) — catches any
   other path that indirectly relied on the removed functions or the
   `selector` kwarg plumbing.
3. Deprecation check: call `make_summary(selector_type="non-cv")` (e.g. in a
   test with `pytest.warns(DeprecationWarning)`) to verify the warning fires
   and the summary still builds.
4. Sanity import check against edited core:
   `uv run python -c "import cellpycore.selectors as s; assert not hasattr(s, 'create_selector')"`.

## Open questions

- None — kwargs handling, core-param removal, and cellpy branching resolved by
  user 2026-07-02.
