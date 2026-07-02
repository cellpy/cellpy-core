# Issue #64 status: small update in readme

- [x] Done

## What was done

- Rewrote the "Development Workflow" part of `README.md` Developing section:
  replaced `uv venv` + activate + `uv pip install -e ".[dev]"` with a single
  `uv sync` step; kept `uv add` / `uv add --dev`; tests now via `uv run pytest`.
- Updated "Common Commands" to project-manager equivalents (`uv sync`,
  `uv remove`, `uv sync --upgrade`, `uv tree`), dropping the `uv pip ...`
  commands.
- Added a `HISTORY.md` bullet under `[Unreleased]`.

## Remaining work

None. Docs-only change; test suite green (107 passed).
