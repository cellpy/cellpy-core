# Status — issue #117 (Stage 1.16)

- [x] Done

## 2026-07-15

- `cellpycore/legacy/meta_mapping.py` landed with pair tables, exception sets,
  pinned legacy inventories, `coerce_test_id`, `legacy_meta_to_core`.
- G9 decision implemented (tester triplet onto `TestMeta`); `CellMeta.volume`
  added and wired into the volumetric converter path. Dated decision notes
  written into `architecture-plan/cellpy2-metadata-handling-plan.md`.
- Quirk documented: legacy `schedule_file_name` is an un-annotated class
  attribute (not a dataclass field) — cellpy's contract test must include it
  explicitly.
- Full suite: 224 passed.
