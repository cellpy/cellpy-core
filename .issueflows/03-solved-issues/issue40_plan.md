# Issue #40 plan: Finalize STEP-12 (core) — promote `CellpyUnits` + converter/optional-extra tests

## Goal

Promote `CellpyUnits` out of `legacy.py` into a first-class core unit-spec module while
keeping `cellpycore.legacy.CellpyUnits` working (re-export) so the STEP-05 parity contract
holds. Add a converter-parity test (gravimetric/areal/absolute) and a pint-optional guard
test. Goldens unchanged.

## Constraints

- **Back-compat / contract:** `cellpycore.legacy.CellpyUnits` must stay importable with
  identical fields/defaults — `cellpy/tests/test_core_settings_parity.py` reads it from
  `cellpycore.legacy` and field-compares against `cellpy.parameters.internal_settings`.
- **No new runtime deps; pint stays optional.** The step/summary engine must import and run
  with `pint` absent; pint stays lazy (`units` extra), off the hot path.
- **No cellpy import in cellpy-core tests.** The converter-parity test asserts against
  hand-computed golden floats (cellpy-core can't depend on cellpy), reproducing cellpy's
  converter math.
- **Goldens unchanged** (`tests/test_golden.py` must still pass untouched).
- KISS: minimal, mechanical move; keep re-exports so nothing else needs editing.

### Prior art

- `src/cellpycore/units.py` — already the home of the pint tooling
  (`get_converter_to_specific`, `nominal_capacity_as_absolute`, `Q`, `get_cellpy_units`,
  `get_default_output_units`); lazy pint via `_get_unit_registry` (lru_cached). Currently
  does `from cellpycore.legacy import CellpyUnits`.
- `src/cellpycore/legacy.py` — defines `DictLikeClass`, `BaseSettings`, `CellpyUnits`,
  plus `CellpyLimits` / `BaseHeaders` / `Headers*` (all subclass `BaseSettings`).
- `cellpy/cellpy/readers/cellreader.py` (`get_converter_to_specific` @5165,
  `nominal_capacity_as_absolute` @4970) — the upstream duplicates; cellpy-core's `units.py`
  is already a verbatim port, so "parity" = pin stable golden outputs so the dup can retire
  without drift.
- `tests/conftest.py` — `Data()` fixtures; `Data` has **no** `mass`/`raw_units`/etc., so the
  converter test will use a small attribute stub.
- Toolbox (`.issueflows/00-tools/`): only `README.md`, nothing relevant. Graph: not consulted
  (mechanical move).

## Approach

**1. Break the import cycle, then move `CellpyUnits`.**
`CellpyUnits(BaseSettings)` and `units.py` would otherwise form a cycle
(`legacy` re-exports from `units` → `units` needs `BaseSettings` from `legacy`). Fix by
moving the generic dict-like base out of `legacy.py`:

- New module `src/cellpycore/settings_base.py`: move `DictLikeClass` + `BaseSettings`
  verbatim (no internal imports → neutral, import-order safe).
- `units.py`: add `from __future__ import annotations`; import `BaseSettings` from
  `settings_base`; **define `CellpyUnits` here** (moved verbatim, same fields/defaults/
  `update`); drop `from cellpycore.legacy import CellpyUnits`. Guard the `Data` type-hint
  import under `TYPE_CHECKING` so `units` has **no runtime import of `cell_core`/`legacy`**
  (prevents the cycle and keeps pint lazy).
- `legacy.py`: import `DictLikeClass`, `BaseSettings` from `settings_base` and
  `CellpyUnits` from `units`, and **re-export all three** (so `cellpycore.legacy.CellpyUnits`
  / `BaseSettings` still resolve). Remaining classes (`CellpyLimits`, `BaseHeaders`,
  `Headers*`) now subclass the re-imported `BaseSettings`.

Resulting import DAG (no cycle): `settings_base` ← `units` ← `legacy` ← `cell_core`.

**2. Converter-parity test** (`tests/test_units_converters.py`, requires pint):
`pytest.importorskip("pint")`. Build a minimal stub (e.g. `SimpleNamespace`) carrying the
attributes the converters read (`raw_units=CellpyUnits()`, `mass`, `active_electrode_area`,
`volume`, `nom_cap`, `nom_cap_specifics`). Assert `get_converter_to_specific` for
`gravimetric` / `areal` / `absolute` and `nominal_capacity_as_absolute` for
`gravimetric` / `areal` / `absolute` return the expected golden floats (computed from the
documented unit math, `pytest.approx`). This pins the contract so cellpy's duplicates can be
retired without drift.

**3. Optional-extra guard test** (`tests/test_units_optional.py`):
- Engine-without-pint: with `pint` import blocked (a `sys.meta_path` finder raising
  `ModuleNotFoundError` for `pint` + `pint` evicted from `sys.modules` +
  `units._get_unit_registry.cache_clear()`), assert importing `cellpycore` and running the
  step + summary engine on a fixture (reuse `test_golden` parquet, or the small fixture)
  succeeds — proving the hot path never touches pint.
- Clear error when called: under the same block, assert `units.Q(...)` /
  `get_converter_to_specific(...)` raise `ModuleNotFoundError` whose message names the
  `units` extra. Restore `sys.meta_path`/`sys.modules` and `cache_clear()` in teardown.

## Files to touch

- **new** `src/cellpycore/settings_base.py` — `DictLikeClass`, `BaseSettings` (moved from `legacy.py`).
- `src/cellpycore/units.py` — `from __future__ import annotations`; `TYPE_CHECKING` `Data`; define `CellpyUnits`; import `BaseSettings` from `settings_base`.
- `src/cellpycore/legacy.py` — remove `DictLikeClass`/`BaseSettings`/`CellpyUnits` bodies; re-import + re-export them (`settings_base` + `units`); keep all other classes.
- **new** `tests/test_units_converters.py` — converter-parity goldens (skip if no pint).
- **new** `tests/test_units_optional.py` — pint-absent engine + clear-error guard.

## Test strategy

- Project runner: `uv run pytest` (or activate `.venv`). Run full suite — must stay green,
  including `tests/test_golden.py` (unchanged) and `tests/test_import.py`.
- New: `uv run pytest tests/test_units_converters.py tests/test_units_optional.py`.
- Cross-repo contract: cellpy's `tests/test_core_settings_parity.py` must still pass against
  the editable cellpy-core (legacy re-export keeps `CellpyUnits` field parity). Verify in the
  cellpy env if convenient; at minimum confirm `cellpycore.legacy.CellpyUnits` fields/defaults
  are byte-identical to before.

## Open questions

1. **Target module for `CellpyUnits`** — plan promotes it into the existing
   `cellpycore.units` (the issue's first suggestion) rather than a brand-new
   `unit_spec.py`. OK, or prefer a dedicated module name?
2. **Moving `DictLikeClass`/`BaseSettings` to `settings_base.py`** — needed to break the
   import cycle cleanly (vs. fragile import-ordering). Acceptable scope creep, or keep base
   in `legacy` and instead define `CellpyUnits` in a module that imports base lazily? (Plan
   recommends the new base module.)
3. **Converter goldens source** — hand-computed/pint-derived constants embedded in the test
   (no cellpy dependency). OK, or should goldens be generated once from cellpy and vendored?

Branch note: `40-...` is currently 1 commit behind `origin/main` (clean tree). Suggest a
`git pull --rebase` before `/iflow-start`; not done here (planning is read-only).
