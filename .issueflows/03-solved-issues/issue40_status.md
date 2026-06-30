# Issue #40 status: Finalize STEP-12 (core) — promote `CellpyUnits` + tests

- [x] Done

## What was done (2026-06-30)

- **Broke the import cycle** by adding `src/cellpycore/settings_base.py` holding the
  generic dict-like settings base (`DictLikeClass`, `BaseSettings`), moved verbatim from
  `legacy.py`. Neutral, dependency-free → import-order safe.
- **Promoted `CellpyUnits`** into `src/cellpycore/units.py` (the issue's first-choice
  target). Added `from __future__ import annotations` and a `TYPE_CHECKING`-only `Data`
  import so `units` has no runtime import of `cell_core`/`legacy` and pint stays lazy.
- **`legacy.py`** now re-imports + re-exports `DictLikeClass`, `BaseSettings` (from
  `settings_base`) and `CellpyUnits` (from `units`); its other classes (`CellpyLimits`,
  `BaseHeaders`, `Headers*`) subclass the re-imported `BaseSettings`. Resulting DAG:
  `settings_base ← units ← legacy ← cell_core` (verified import works legacy-first and
  units-first; `legacy.CellpyUnits is units.CellpyUnits`).
- **Converter-parity test** `tests/test_units_converters.py`: golden floats for
  `get_converter_to_specific` (gravimetric=500.0, areal=0.5, volumetric=0.5, absolute=1.0,
  unknown-mode=1.0, charge-unit-mismatch=500000.0) and `nominal_capacity_as_absolute`
  (gravimetric=0.006, explicit value/specific=0.0005, convert_charge_units=6e-6). Skips
  without pint; no cellpy import (goldens hand-derived from the documented unit math).
- **Optional-extra guard test** `tests/test_units_optional.py`: a `meta_path` finder blocks
  `import pint`; asserts (1) `cellpycore` + `cellpycore.units` import fine, (2) the step +
  summary engine runs end-to-end on the arbin golden fixture, (3) `units.Q` /
  `get_converter_to_specific` raise `ModuleNotFoundError` matching "units".

## Tests

- `python -m pytest -q` (cellpy-core, `.venv`): **85 passed** — incl. 12 new, goldens
  (`test_golden.py`) unchanged.
- Cross-repo contract (cellpy `.venv`, editable cellpy-core):
  `tests/test_core_settings_parity.py` **5 passed** — `CellpyUnits` field parity intact.

## Remaining work

None for #40 (cellpy-core side). The upstream opt-in — cellpy delegating its duplicate
`get_converter_to_specific` / `nominal_capacity_as_absolute` to `cellpycore.units` — stays
tracked on jepegit/cellpy and is out of scope here.

## Notes

- Branch `40-...` is up to date with its own remote (`origin/40-...`); it sits behind
  `origin/main` but no rebase was needed (`git pull --rebase` = "Already up to date" on its
  upstream).
- `nominal_capacity_as_absolute` "areal"/"absolute" modes raise `DimensionalityError` with
  the default `nominal_capacity="mAh/g"` unit (pre-existing behavior, identical to cellpy);
  only the dimensionally-valid combinations are pinned as goldens.
