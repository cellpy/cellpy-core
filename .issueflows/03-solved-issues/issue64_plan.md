# Issue #64 plan: small update in readme

## Goal

The Developing section in `README.md` tells developers to run `uv venv` +
`uv pip install -e ".[dev]"`. Switch to uv's built-in project workflow:
`uv sync` after cloning, `uv add` for new dependencies.

## Approach

Rewrite the "Development Workflow" and "Common Commands" parts of the
Developing section:

- Drop `uv venv` + activate + `uv pip install -e ".[dev]"`; replace with a
  single `uv sync` step (creates `.venv` and installs all locked deps).
- Keep `uv add` / `uv add --dev` for adding dependencies.
- Run tests via `uv run pytest`.
- Update "Common Commands" to project-manager equivalents (`uv remove`,
  `uv sync --upgrade`, `uv tree`).

## Files to touch

- `README.md` (only)

## Test strategy

Docs-only change; run `uv run pytest` before commit to confirm the suite is
still green (yolo chain requirement).
