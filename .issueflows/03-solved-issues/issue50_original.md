# Issue 50 — Code review report: weaknesses, improvements, plan forward

> Local-only issue captured via cloud agent (`gh` is read-only in this
> environment, so no GitHub issue was created). Number 50 chosen as the next
> free number after GitHub issue/PR #49.

## Task (as requested by the user)

Go through the code base and find possible weaknesses and suggestions for
improvements and suggestions for a plan forward. Write the findings up as a
code report markdown file and put it in `.issueflows/04-designs-and-guides/`
(the project's durable memory). Docs-only: no production code is touched.

## Scope

- Full review of `src/cellpycore/` (engine, config/schema, legacy bridge,
  header mapping, units, selectors, timestamps, metadata scaffolding).
- Packaging (`pyproject.toml`), CI (`.github/workflows/simpletest.yml`),
  repo hygiene, and test coverage.
- Deliverable: `.issueflows/04-designs-and-guides/code-review-2026-07.md`.
