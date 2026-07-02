# Issue 50 — Plan

Run in `/iflow-yolo` mode (small, low-risk, docs-only; single consolidated
confirmation given by the user up front: "no actual code is touched", "feel
free to merge the PR you create yourself").

## Approach

1. Review the code base (done in the analysis session preceding this issue):
   read every module in `src/cellpycore/`, the tests, packaging, and CI;
   verify each suspected defect by executing code (e.g. confirm the native
   schema lacks the legacy attributes `selectors.py` dereferences); run the
   full test suite (88 passed).
2. Write the findings up as
   `.issueflows/04-designs-and-guides/code-review-2026-07.md`, structured as:
   overall verdict → verified bugs → design gaps → packaging/hygiene →
   sequenced plan forward → test gaps.
3. No production code changes. No `graphify update` needed (markdown only).
4. Close: status file with `- [x] Done`, move the issue group to
   `03-solved-issues`, commit, push, PR, merge (explicitly authorized).

## Non-goals

- Fixing any of the reported defects (each gets its own follow-up issue; see
  the "Plan forward" section of the report).
