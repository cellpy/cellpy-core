# Issue #22 status: Remove superseded pandas summary/selector functions

- [x] Done

## Summary

Resolved as **documentation-only**. The practically removable dead code named in #22 was
already deleted in #24; the two remaining functions are not dead (the external cellpy repo
still imports them), so they are intentionally retained and the removal is deferred.

## Per-candidate outcome

| Candidate | Outcome |
|---|---|
| `summarizers.generate_absolute_summary_columns` | **Removed in #24.** Absent from `src/cellpycore/`. |
| `summarizers.end_voltage_to_summary` | **Removed in #24.** Absent from `src/cellpycore/`. |
| `selectors.create_selector` | **Kept (deferred).** Still imported by cellpy (`cellreader.py`, `tests/test_slim.py`); hard removal would break cellpy's pinned `@main` dependency. |
| `selectors.summary_selector_exluder` | **Kept (deferred).** Pandas engine wrapped by `create_selector`; lives as long as `create_selector`. |

## What was done

- Verified (grep) that the two summarizer functions no longer exist in `src/cellpycore/` and
  that `create_selector` / `summary_selector_exluder` are present and still imported by cellpy.
- Recorded the deferral decision and removal trigger in
  `.issueflows/04-designs-and-guides/selector-dead-code-deferral.md`.
- Per agreed decisions: no source edits and no regression guard test (closed as documentation).

## Verification

- `uv run pytest` → see run output (green-tree sanity check; no source/test changes made).

## Remaining / deferred (tracked, not part of this issue)

- Remove `create_selector` + `summary_selector_exluder` once cellpy stops importing
  `core_selectors.create_selector` (migrates onto the native `make_summary` path or its own
  helper). See the deferral note above.
