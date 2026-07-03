# Issue #66 status: code cleaning and test completion

- [ ] Done

Plan: [issue66_plan.md](issue66_plan.md) (confirmed 2026-07-03, deferred items filed as #67–#70)

## What's done

- Plan confirmed after grilling; deferred issues #67 (selectors), #68 (units
  fallback), #69 (coverage), #70 (B1/B2) filed on GitHub.

## Remaining work

- Phase 1 — hygiene: deps/pyproject, junk files, module loggers, A3 fix +
  regression test, A5 fresh raw_limits, A6 dead fields, ruff in CI.
- Phase 2 — API truthing: `__init__.py` exports + `__version__`, A4 dead
  params, `py.typed`, README + this-project.md.
- Phase 3 — engine guards: `NoDataFound` / missing-column `ValueError`.
- Phase 4 — tests: native e2e via public API, pytest-benchmark (opt-in).
- Full suite green; update this file.
