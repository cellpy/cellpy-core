# Issue #84 status

## Done

- [x] Done

## Summary

Added `.pre-commit-config.yaml` with local `uv run ruff` hooks (`check --fix`,
`format`); `pre-commit` dev dependency; updated `docs/development.md` and
`this-project.md` with install instructions.

## Verification

- `uv run pre-commit run --all-files` — passed
- `uv run ruff check && uv run ruff format --check` — passed
- `uv run pytest` — 131 passed
