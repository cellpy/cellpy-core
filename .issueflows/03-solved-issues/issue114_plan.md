# Issue #114 — plan

## Goal

Sync stale statuses in `.issueflows/04-designs-and-guides/` so planners do not re-derive facts already true in code.

## Approach

1. **STEP-12 / #40** — `CellpyUnits` schema lives in `cellpycore.units.spec` (#40, #112 done on core); remaining scope is cellpy-side converter delegation only.
2. **#54** — `exclude_step_types` implemented in `summarizers.py`; mark done in STEP-13+ table.
3. **`column-headers-review.md`** — fix module path to `src/cellpycore/legacy/mapping.py`.
4. **`cellpy-core-integration-into-cellpy.md`** — retire stale "make_step_table NOT ported" finding; align seam/follow-up bullets with STEP-08 ✅.
5. **Grep sweep** — fix other `header_mapping.py` path refs in the same folder; leave intentional 🟡 (STEP-06 ongoing, STEP-12 partly) as-is.

## Files to touch

- `.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md`
- `.issueflows/04-designs-and-guides/column-headers-review.md`
- `.issueflows/04-designs-and-guides/cellpy-core-integration-into-cellpy.md`
- `.issueflows/04-designs-and-guides/code-review-2026-07.md` (path ref only, if present)

## Test strategy

Docs-only — re-run `uv run pytest` as sanity check; no new tests.
