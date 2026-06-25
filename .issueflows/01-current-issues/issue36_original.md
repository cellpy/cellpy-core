# Issue 36 — Iterative fixes: header-schema-review

Source: https://github.com/cellpy/cellpy-core/issues/36

Interactive `/iflow-fix` session.

After landing the authoritative native<->legacy column mapping in
`src/cellpycore/header_mapping.py`, re-evaluate whether the native header schema
(`config.RawCols` / `StepCols` / `CycleCols`) is optimal, and consider promoting
selected legacy-only columns into the native schema.

Individual fixes are recorded in `issue36_status.md` under an "Iterative fixes
log" and landed together via `/iflow-close`.
