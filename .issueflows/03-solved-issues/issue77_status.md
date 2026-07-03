# Issue #77 status

- [x] Done

## What's done

- Created `cellpycore/units/`, `cellpycore/legacy/`, `cellpycore/testing/` packages
- Split `units/` into `spec.py` + `converters.py`; `legacy/` into `exceptions`, `limits`, `meta`, `headers`, `mock_core` (+ existing `mapping`, `selectors`)
- Package `__init__.py` files are re-export only
- Updated all importers (no shims); deleted old top-level modules
- Updated `this-project.md`, `config.py` docstrings
- 131 tests pass; ruff clean; graphify rebuilt

## Remaining work

- None
