# Issue #69 — plan

## Goal

Add pytest coverage reporting to CI (deferred from #66 / code-review section C).

## Approach

1. Add `pytest-cov` to the `[dependency-groups] dev` list; sync lockfile.
2. Configure `[tool.coverage.run]` in `pyproject.toml` (`source = ["cellpycore"]`).
3. Extend `.github/workflows/simpletest.yml` test step: `--cov=cellpycore --cov-report=term-missing`.
4. No fail threshold or badge (optional per issue; keep yolo scope minimal).

## Files to touch

- `pyproject.toml`
- `uv.lock`
- `.github/workflows/simpletest.yml`

## Test strategy

- `uv run pytest --cov=cellpycore --cov-report=term-missing` locally before close.
