# Issue #69 — status

- [x] Done

## What's done

- Added `pytest-cov` (and `coverage`) to the dev dependency group; synced `uv.lock`.
- Configured `[tool.coverage.run]` / `[tool.coverage.report]` in `pyproject.toml`.
- CI test step now runs `pytest --cov=cellpycore --cov-report=term-missing`.
- Local verification: 131 passed, ~83% line coverage.

## Remaining work

- None (threshold/badge left optional per issue scope).
