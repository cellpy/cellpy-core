# Issue #117 — Stage 1.16: metadata — legacy⇄core field-mapping module (meta_mapping)

GitHub: https://github.com/cellpy/cellpy-core/issues/117
Labels: cellpy2-stage1, yolo

## Goal

`cellpycore/legacy/meta_mapping.py` declaring the legacy `CellpyMetaCommon` /
`CellpyMetaIndividualTest` ⇄ core `CellMeta` / `TestMeta` translation once:
`COMMON_TO_CELL_PAIRS`, `COMMON_TO_TEST_PAIRS` (the re-homed `cell_name`,
`start_datetime`, `time_zone`, `tester_ID→tester_id`), `INDIVIDUAL_TO_TEST_PAIRS`
(incl. `test_ID→test_id` int coercion), `LEGACY_ONLY` (each with documented
destination), `CORE_ONLY` (migration fills from context) — with the same
bijectivity/round-trip/totality tests as the header mapping. Resolve in the same PR:
the G9 decision (tester software/calibration fields → recommendation: into `TestMeta`)
and `CellMeta.volume` (needed by volumetric units mode).

## Acceptance

- Totality tests in place; G9 + volume decisions recorded in the metadata plan doc
  (dated note) and implemented.
