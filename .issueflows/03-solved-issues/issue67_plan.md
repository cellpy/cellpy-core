# Issue #67 plan: selectors → bridge-only `legacy_selectors`

Confirmed via grill-me (2026-07-03).

## Goal

Relocate the three remaining pandas selector helpers (`get_step_numbers`,
`get_cycle_numbers`, `get_rates`) to a clearly bridge-only module, fix the
`default_schema()` trap by defaulting to `legacy_schema()`, and add unit +
golden tests. No native polars port.

## Grill decisions (locked)

| # | Decision |
|---|----------|
| 1 | **Bridge-only** — not a native polars port |
| 2 | **`legacy_selectors.py`** — delete `selectors.py`; no shim |
| 3 | **`legacy_schema()` default** — new helper in `config.py`, used when `schema is None` |
| 4 | **Tests: unit + golden** — handcrafted legacy frames always run; one golden smoke with parquet `skipif` |
| 5 | **Relocation + schema fix only** — preserve cellpy-parity behavior; do not fix dead code (e.g. unreachable `rate = 0.05` block) |

## Constraints

- Read-only on cellpy repo; no cellpy changes required (cellpy owns its own
  `cellreader.py` copies; #45 removed the last `cellpycore.selectors` import).
- Functions stay **pandas-only** (dict / `pandas.DataFrame` returns unchanged).
- Not part of the public API (`__init__.py` exports unchanged).
- Google-style docstrings on new/changed public helpers.

### Prior art

- `src/cellpycore/selectors.py` — current broken module (legacy attr names +
  `default_schema()`).
- `src/cellpycore/legacy.py` — `HeadersNormal`, `HeadersStepTable`,
  `HeadersSummary` (target neighbourhood).
- `config.default_schema()` — native `RawCols`/`StepCols`/`CycleCols` bundle.
- `tests/test_golden._legacy_schema()` — private duplicate; replace with shared
  `config.legacy_schema()`.
- `tests/test_schema.py` — imports `selectors`, asserts removed #45 functions
  absent; update import path.
- `cellpy/readers/cellreader.py` — verbatim upstream copies of the three
  functions (parity reference, not imported).
- `.issueflows/04-designs-and-guides/this-project.md` — already notes selectors
  as bridge-only/broken; update wording post-fix.
- Graph community (selectors): `get_step_numbers`, `get_cycle_numbers`,
  `get_rates` — isolated, no engine callers.

## Approach

1. **Add `legacy_schema()` to `config.py`**
   - `Schema(raw=HeadersNormal(), cycle=HeadersSummary(), step=HeadersStepTable())`.
   - Docstring: bridge/legacy callers only; engine uses `default_schema()`.
   - Import header classes from `cellpycore.legacy` (lazy or top-level — match
     existing `config.py` style).

2. **Move `selectors.py` → `legacy_selectors.py`**
   - Move the three functions verbatim (only change: `default_schema()` →
     `legacy_schema()` in each `if schema is None` block).
   - Module-level docstring: bridge-only, pandas + legacy column names required,
     not for native `CellpyCellCore` / `default_schema()` consumers.
   - Delete `src/cellpycore/selectors.py`.

3. **Deduplicate test helper**
   - `tests/test_golden.py`: replace `_legacy_schema()` with
     `config.legacy_schema()`.

4. **Update `tests/test_schema.py`**
   - Drop `selectors` import.
   - Move `test_no_legacy_selector_functions` to new test file (or delete if
     module gone — function removal is already covered by #45; optional thin
     assert that `legacy_selectors` has no `create_selector`).

5. **Add `tests/test_legacy_selectors.py`**
   - **Unit (always run):** minimal legacy-named pandas raw + step tables;
     assert `get_step_numbers` dict keys/values, `get_cycle_numbers` without
     rate filter, `get_rates` columns; confirm `schema=None` uses
     `legacy_schema()` (no `AttributeError`).
   - **Golden (skipif parquet missing):** reuse `test_golden._step_table()` +
     `CYCLER_CC_*` constants; call `get_step_numbers("charge")`,
     `get_cycle_numbers()`, `get_rates()` on real legacy-shaped step table;
     assert cycle count matches `CYCLER_CC_N_CYCLES` and charge steps exist
     for cycle 1.

6. **Docs touch-up**
   - `this-project.md`: selectors line → "bridge-only in `legacy_selectors.py`,
     requires `legacy_schema()`".
   - Optional one-liner in `code-review-2026-07.md` A1 noting resolution via #67
     (no rewrite of the report).

## Files to touch

| File | Change |
|------|--------|
| `src/cellpycore/config.py` | Add `legacy_schema()` |
| `src/cellpycore/legacy_selectors.py` | New — moved functions + module docstring |
| `src/cellpycore/selectors.py` | Delete |
| `tests/test_legacy_selectors.py` | New — unit + golden tests |
| `tests/test_golden.py` | Use `legacy_schema()` |
| `tests/test_schema.py` | Remove `selectors` import; adjust/remove selector asserts |
| `.issueflows/04-designs-and-guides/this-project.md` | Update non-goals line |

## Test strategy

```bash
uv run pytest tests/test_legacy_selectors.py -v
uv run pytest   # full suite green
```

Golden test uses same `pytest.mark.skipif` + `CYCLER_CC_RAW` pattern as
`test_golden.py`.

## Open questions

None — all branches resolved in grill-me.
