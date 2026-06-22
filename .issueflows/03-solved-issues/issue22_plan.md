# Plan for issue #22: Remove superseded pandas summary/selector functions

## Goal

Resolve the dead-code cleanup from #22 by confirming what is already gone, deleting
anything still dead, and explicitly **not** removing functions that the external
`cellpy` repo still imports. End state: cellpy-core has no superseded summary/selector
dead code, `uv run pytest` is green, and cellpy keeps importing what it needs.

## Constraints

- KISS: this is a deletion / verification task, not a refactor. No new abstractions.
- Back-compat with the external `cellpy` repo: cellpy is pinned to
  `cellpycore @ git+...@main`, so anything still imported there **must not** be hard-removed
  (the issue's own "Before deleting" guard: coordinate a deprecation, not a hard removal).
- Google-style docstrings; project loggers; tests stay green.
- Scope: only the four named candidates. No drive-by edits to `get_step_numbers` /
  `get_cycle_numbers` / `get_rates`.

### Prior art

- `summarizers.generate_absolute_summary_columns` / `summarizers.end_voltage_to_summary`
  — **already removed in issue #24** (see `.issueflows/03-solved-issues/issue24_status.md`,
  "Dead-code cleanup"). Grep confirms neither name exists in `src/cellpycore/` today.
  New work: nothing to delete; optionally add a regression guard so they stay gone.
- `selectors.create_selector` (`src/cellpycore/selectors.py:18`) — convention: `(data, schema,
  selector_type, exclude_types, exclude_steps, final_data_points)`, returns a `functools.partial`
  over `summary_selector_exluder`. **Still imported externally** by cellpy
  (`cellpy/readers/cellreader.py:5798`, `tests/test_slim.py:91`). New work: **keep / coexist**;
  removal deferred to a coordinated cellpy-side migration.
- `selectors.summary_selector_exluder` (`src/cellpycore/selectors.py:63`) — the pandas engine
  `create_selector` wraps (`selectors.py:52`). Not imported directly by cellpy but reachable
  through `create_selector`. New work: **keep** while `create_selector` lives.
- `tests/test_schema.py::test_no_module_header_globals` (`tests/test_schema.py:68`) — existing
  pattern using `assert not hasattr(module, name)` to lock in removed module-level globals.
  New work: mirror this pattern if we add a guard for the removed summarizer functions.

## Approach

The two summarizer functions named in the issue are already gone (#24); the two selector
functions are **not dead** (cellpy actively calls `create_selector`). Per the resolved decisions
below, #22 is closed as **documentation-only**: no code or test changes, selector removal deferred.

Concrete steps:

1. **Verify (read-only).** Re-confirm with grep that `generate_absolute_summary_columns` and
   `end_voltage_to_summary` are absent from `src/cellpycore/`, and that `create_selector` /
   `summary_selector_exluder` are present and still imported by cellpy
   (`cellreader.py`, `test_slim.py`). (Already done during planning — findings above.)
2. **Record the deferral decision.** Add a short note under `.issueflows/04-designs-and-guides/`
   capturing: `create_selector` / `summary_selector_exluder` are kept because the external cellpy
   consumer still imports `core_selectors.create_selector`; remove only after cellpy migrates off it.
3. **Close out #22** via `issue22_status.md`: the two summarizer functions were removed in #24;
   the two selector functions are intentionally retained (deferred follow-up, blocked on cellpy).

## Files to touch

- `.issueflows/04-designs-and-guides/selector-dead-code-deferral.md` (new, short) — record the
  "keep `create_selector` until cellpy migrates" decision and link back to #22 / #24 / #13.
- `.issueflows/01-current-issues/issue22_status.md` — created at `/issue-start`/`/issue-close`
  time with the explicit `- [x] Done` checkbox and the per-candidate outcome.

No changes to `src/cellpycore/summarizers.py`, `src/cellpycore/selectors.py`, or
`tests/test_schema.py` (decision 2: close as documentation, no guard test).

## Test strategy

- `uv run pytest` — full suite should stay green; since no source/test changes are made, this is a
  sanity check that the tree is still green (currently ~30 tests; #24 left it green).
- No cellpy-side run needed: we are explicitly *not* removing anything cellpy imports.

## Open questions — RESOLVED

1. **Selector removal:** **Defer** (option a). Keep both functions, document the dependency, close
   #22 noting selector removal is blocked on a future cellpy migration off
   `core_selectors.create_selector`.
2. **Guard test:** **Close as documentation** — no `tests/test_schema.py` change.
