# Plan — issue #117 (Stage 1.16)

1. **Model changes (the two decisions, implemented):**
   - G9: `tester_server_software_version`, `tester_client_software_version`,
     `tester_calibration_date` become `TestMeta` fields (test-dependent
     provenance; no `extra` dict).
   - `CellMeta.volume: Optional[float]` (cellpy units convention, `cm**3`),
     wired into `get_converter_to_specific(mode="volumetric", cell_meta=…)`.
   - Both recorded as dated notes in the metadata plan
     (architecture-plan repo, Step 1 section).
2. **`cellpycore/legacy/meta_mapping.py`** — pair tables
   (`COMMON_TO_CELL_PAIRS` 19, `COMMON_TO_TEST_PAIRS` 7 incl. the G9 triplet,
   `INDIVIDUAL_TO_TEST_PAIRS` 8), `LEGACY_ONLY` with documented destinations
   (`file_errors` dropped, `raw_id` → `TestMeta.uuid`, `cellpy_file_version` →
   file-format layer), `CORE_ONLY_CELL` / `CORE_ONLY_TEST`, pinned legacy field
   inventories (core cannot import cellpy; cellpy contract tests guard the pins).
3. **Helpers:** `coerce_test_id` (int coercion; legacy list → first entry,
   logged; bool/garbage → ValueError) and `legacy_meta_to_core(common,
   individual)` (pure translation, provenance untouched, accepts mappings or
   attribute-style objects).
4. **Quirk found and documented:** legacy `schedule_file_name` is an
   un-annotated class attribute, not a dataclass field.
5. **Tests:** `tests/test_meta_mapping.py` — totality on all four sides,
   bijectivity, no target collisions, documented destinations, `coerce_test_id`
   matrix, end-to-end translation incl. re-homing and legacy-only skips;
   volumetric-via-CellMeta test added to the units suite.
