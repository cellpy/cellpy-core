# Issue #114: Stage 0.12: Doc-sync pass over the guiding documents (stale statuses)

Source: https://github.com/cellpy/cellpy-core/issues/114

## Original issue text

> Part of **Stage 0 â€” foundations for cellpy 2** (see the tracking issue). Plan documents live in the shared workspace: `cellpy-workspace/architecture-plan/` (the [architecture-plan repo](https://github.com/cellpy/architecture-plan); formerly `architecture-plan/`) (alongside the `cellpy` and `cellpy-core` repos).

## Goal

A one-hour pass over `.issueflows/04-designs-and-guides/` + the integration roadmap fixing
the stale statements found during the cellpy-2 planning cross-read:

- Integration roadmap STEP-12: says "schema lives in `legacy.py`" â€” `cellpycore/units/spec.py`
  exists (issue #40 executed, plus #112); remaining scope is only the cellpy-side delegation.
- Roadmap STEP-13+ table: #54 (`exclude_step_types`) marked "future" but implemented
  (`summarizers.py:655/715`, threaded through `make_core_summary`).
- `column-headers-review.md` Â§Issue-#34 points at `src/cellpycore/header_mapping.py`;
  the module lives at `src/cellpycore/legacy/mapping.py`.
- `cellpy-core-integration-into-cellpy.md` "Key findings" still says `make_step_table` is
  NOT ported (superseded by STEP-08 âœ… in the same folder).

## Why

Stale "partly done" statuses cost every future planner a code-level re-derivation â€” the
cellpy-2 gap analysis (workspace: `architecture-plan/cellpy2-plans-gap-analysis.md`, item F7)
had to verify each of these against the source. One hour now, saved repeatedly later.

## Acceptance

- The four listed corrections applied; a quick grep for other â¬œ/ðŸŸ¡ statuses done in the
  same sitting and corrected or confirmed.


