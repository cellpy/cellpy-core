# Issue #45 status: remove `create_selector` / `summary_selector_exluder`

- [x] Done

## What was done (2026-07-02)

### cellpy (branch `core45-drop-create-selector`, off `master`)

- `cellpy/readers/cellreader.py`:
  - Removed `from cellpycore import selectors as core_selectors`.
  - `make_summary`: kept the `selector` / `selector_type` / `exclude_types` /
    `exclude_steps` kwargs but they now emit a `DeprecationWarning` when
    supplied (they have been no-ops since the core seam); docstring updated.
  - `_make_summary`: dropped the four dead kwargs, the `create_selector`
    block, and the `selector=` forwarding to `make_core_summary`.
- `tests/test_slim.py`: removed `core_selectors` usage in
  `test_direct_core_make_core_summary`; added
  `test_make_summary_selector_kwargs_deprecated` (asserts warning + summary
  still builds).

### cellpy-core (branch `45-cleanup-blocked-...`)

- `src/cellpycore/selectors.py`: deleted `create_selector` and
  `summary_selector_exluder`, plus now-unused imports (`functools`,
  `Callable`, `Iterable`, `List`, `StepCols`, `RawCols`) and the
  `FIRST`/`LAST`/`DELTA` constants.
- `src/cellpycore/cell_core.py`: removed the never-used `selector` parameter
  from both `make_core_summary` signatures (native + legacy bridge).
- `tests/test_schema.py`: added `test_no_legacy_selector_functions`.
- Docs: `selector-dead-code-deferral.md` marked resolved;
  `cellpy-core-integration-roadmap.md` #45 row flipped to done.

## Test results

- cellpy-core: `uv run pytest` — **95 passed** (includes golden fixtures).
- cellpy (conda `cellpy_dev_313`, editable core via `[tool.uv.sources]`):
  - `tests/test_slim.py` — 6 passed (incl. new deprecation test).
  - `pytest -k summary` — 79 passed, 1 skipped, 1 xfailed.
  - Full suite (excluding `test_ica.py`, `test_ocv_relax.py`,
    `test_plotutils_summary_plot.py`) — **428 passed, 17 skipped, 11 xfailed**.

### Pre-existing environment crash (not caused by this change)

`test_ica.py`, `test_ocv_relax.py`, and `test_plotutils_summary_plot.py`
abort the interpreter with `Windows fatal exception: code 0xc06d007f` inside
scipy/numpy LAPACK (`lstsq` / `inv`). A standalone
`python -c "from scipy.signal import savgol_filter; ..."` (no cellpy imports)
crashes the same way in `cellpy_dev_313`, so this is a broken scipy/BLAS DLL
situation in that conda env on this machine, unrelated to the selector
removal. Should be fixed separately (e.g. reinstall scipy/numpy in the env).

## Remaining work

- Commit + push both branches, open PRs.
- **Merge order:** cellpy PR first (cellpy pins `cellpycore @ git+…@main`),
  then the cellpy-core PR.
