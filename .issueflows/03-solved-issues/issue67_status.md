# Issue #67 status: selectors → bridge-only `legacy_selectors`

- [x] Done

Plan: [issue67_plan.md](issue67_plan.md) (confirmed 2026-07-03, grill-me)

## What's done

- Added `config.legacy_schema()` (lazy import of legacy header classes).
- Moved three functions to `src/cellpycore/legacy_selectors.py`; deleted `selectors.py`.
- `tests/test_legacy_selectors.py` — unit tests (always run) + golden smoke (`skipif`).
- `tests/test_golden.py` — uses shared `legacy_schema()`; dropped private `_legacy_schema()`.
- `tests/test_schema.py` — removed `selectors` import and selector asserts.
- Docs: `this-project.md`, `code-review-2026-07.md` A1 resolution note.
- Suite green: 123 passed (+ 3 deselected benchmarks).

## Remaining work

None.
