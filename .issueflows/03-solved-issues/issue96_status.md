# Issue #96 — Status

- [x] Done

## What's done

- Added `Cols.ordered_names()` on `Cols` base (`config.py`) with Google docstring
- Migrated `dev/make_harmonized_raw.py` off `vars(RawCols)`
- Updated `tests/test_config_columns.py` — uses `ordered_names()`, added `_` prefix test
- Updated `tests/test_harmonized_fixture.py` — ordered column list assertion
- All 152 tests pass; ruff clean

## Remaining work

- None
