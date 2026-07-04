# Issue #84 plan — add auto precommit

## Goal

Configure in-repo [pre-commit](https://pre-commit.com/) so commits auto-run
`ruff check --fix` and `ruff format`, matching local dev guidance and CI lint
steps in [`.github/workflows/simpletest.yml`](../../.github/workflows/simpletest.yml).

## Constraints

- No CI/workflow changes — pre-commit is a **local** guard only.
- Keep scope minimal: config + dev dep + doc updates; no new test modules.
- Use project's existing ruff config in [`pyproject.toml`](../../pyproject.toml)
  (`[tool.ruff]`, dev dep `ruff>=0.11.8`).
- Run/install via `uv` per
  [this-project.md](../04-designs-and-guides/this-project.md).

### Prior art

- **CI lint commands** — [`.github/workflows/simpletest.yml`](../../.github/workflows/simpletest.yml)
  lines 31–34: `uv run ruff check` + `uv run ruff format --check` (no `--fix` in CI).
- **Local lint guidance** — [this-project.md](../04-designs-and-guides/this-project.md):
  autofix with `uv run ruff check --fix && uv run ruff format`; notes pre-commit
  "not configured in-repo yet".
- **Issue #66** — added ruff to CI and `[tool.ruff]` config; this issue completes
  the local hook story.
- **Toolbox** — [`.issueflows/00-tools/`](../00-tools/) empty (no helpers).
- **Sibling repos** — no `.pre-commit-config.yaml` in cellpy or batbase.
- **Graph** — no relevant hits in `GRAPH_REPORT.md`.

## Approach

Use **local pre-commit hooks** (`language: system`) that invoke `uv run ruff …`
so hook runs use the same ruff version as [`uv.lock`](../../uv.lock), not a
separate pin in `ruff-pre-commit`.

1. Add `pre-commit` to `[dependency-groups] dev` via `uv add --group dev pre-commit`.
2. Add [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) at repo root.
3. Update docs (see Files to touch).
4. Verify: `uv run pre-commit run --all-files`; then
   `uv run ruff check && uv run ruff format --check` and `uv run pytest`.

**Confirmed scope:** both `ruff check --fix` and `ruff format` hooks.

## Files to touch

| File | Change |
|------|--------|
| [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) | **New** — local hooks |
| [`pyproject.toml`](../../pyproject.toml) + [`uv.lock`](../../uv.lock) | Add `pre-commit` dev dep |
| [`docs/development.md`](../../docs/development.md) | Replace step 3 placeholder with install command |
| [`.issueflows/04-designs-and-guides/this-project.md`](../04-designs-and-guides/this-project.md) | Point at in-repo config + install command |

**Not touched:** CI workflows, source code, tests.

## Test strategy

No new pytest modules — config-only change.

Verification commands:

```bash
uv sync --group dev
uv run pre-commit run --all-files
uv run ruff check && uv run ruff format --check
uv run pytest
```

## Open questions

None — format hook scope confirmed (both hooks).
