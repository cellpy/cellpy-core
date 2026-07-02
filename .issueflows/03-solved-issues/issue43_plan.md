# Issue #43 plan: native schema `ref_potential` support

**Confirmed 2026-07-02** (user accepted with the recommended answers: native name
`ref_potential`; skip-when-absent; proceed before release #44).

## Goal

Add a reference-electrode potential column to the native schema (`RawCols`) and wire it
through the polars step engine so 3-electrode data gets per-step aggregates, exercised by a
fixture/test.

## Constraints

- **Naming convention:** the harmonized spec mandates `potential` (not `voltage`) for the
  cell-voltage column → the native name should be **`ref_potential`** for consistency.
- **Legacy bridge untouched.** Legacy `HeadersStepTable` has *no* reference-voltage base, so
  the legacy 64-column step frame must not grow new columns. Legacy raw `reference_voltage`
  stays in `LEGACY_ONLY_RAW` (unbridged); the new native columns go into the
  `NATIVE_ONLY_*` exception sets. Golden/parity tests (`tests/test_golden.py`) stay
  untouched and must stay green (golden Arbin data has no ref column anyway).
- **Spec docs are authoritative:** `docs/data_format_specifications/harmonized_raw.md` and
  `step_table.md` must be updated in the same PR; `tests/test_config_columns.py` enforces
  code↔spec agreement (`RAW_EXPECTED` / `STEP_EXPECTED`).
- **Engine stat-column contract (code review B1):** per-step stat columns are hardcoded
  `f"{base}_{stat}"`; `ref_potential` follows that existing contract (base name =
  `ref_potential`). No schema-derived stat-name refactor in this issue.
- **No CycleCols / summary change.** Issue scopes StepCols only "if a consumer needs";
  no consumer today.
- Migration guide honoured: no cellpy-side change needed (native-only addition).

### Prior art

- `internal_resistance` (issue #13 Phase 1) is the exact template: optional raw signal,
  added to `RawCols` + `StepCols` aggregate set + `_SIGNAL_BASES`, skipped when absent —
  mirror it 1:1.
- `_helpers.create_raw_data` + `mock_data_with_raw` fixture (conftest) is the existing
  synthetic-data path for exercising optional columns.
- `.issueflows/00-tools/` — nothing relevant (README index only).

## Approach

1. **`config.RawCols`**: add `ref_potential: str = "ref_potential"` (place after
   `internal_resistance`, before the `aux_*` block; optional value).
2. **`config.StepCols`**: add the 7-stat aggregate set `ref_potential_mean/std/min/max/
   first/last/delta` (after the `internal_resistance_*` block, before `c_rate`).
3. **`summarizers.py`**: add `("ref_potential", "ref_potential")` to `_SIGNAL_BASES` and
   `raw_for_base` in `make_step_table`. Present → aggregated like the other signals;
   absent → skipped entirely (same as `internal_resistance` today; see open question 2).
   Classifier unaffected (its `required` set unchanged).
4. **`header_mapping.py`**: add `"ref_potential"` to `NATIVE_ONLY_RAW` and to
   `NATIVE_ONLY_STEP` (base-signal granularity). `reference_voltage` stays in
   `LEGACY_ONLY_RAW`. Totality tests then pass by construction.
5. **Fixture**: extend `_helpers.create_raw_data` with a synthetic `ref_potential` column
   (e.g. `potential` minus a small offset) so `mock_data_with_raw` carries it. No real
   3-electrode parquet exists anywhere yet — vendoring one stays a follow-up when such
   data appears (noted in status file).
6. **Docs**: add the `ref_potential` row to `harmonized_raw.md` (float, Volt, optional) and
   the aggregate rows to `step_table.md`; drop a one-line "gap closed (#43)" note in
   `step-table-polars-migration.md` Phase 1.

## Files to touch

| File | Change |
| --- | --- |
| `src/cellpycore/config.py` | `RawCols.ref_potential`; `StepCols.ref_potential_*` (7 fields) |
| `src/cellpycore/summarizers.py` | `_SIGNAL_BASES` + `raw_for_base` entry |
| `src/cellpycore/header_mapping.py` | `NATIVE_ONLY_RAW` + `NATIVE_ONLY_STEP` additions |
| `src/cellpycore/_helpers.py` | synthetic `ref_potential` in mock raw |
| `docs/data_format_specifications/harmonized_raw.md` | spec row |
| `docs/data_format_specifications/step_table.md` | aggregate spec rows |
| `tests/test_config_columns.py` | extend `RAW_EXPECTED` / `STEP_EXPECTED` |
| `tests/test_schema.py` | new tests (see below) |
| `.issueflows/04-designs-and-guides/step-table-polars-migration.md` | gap-closed note |
| `.issueflows/01-current-issues/issue43_status.md` | status |

## Test strategy

Run with `uv run pytest` (project default; suite currently green, ~88 tests).

New tests:

- `make_step_table` on mock raw **with** `ref_potential` → all 7 `ref_potential_*` columns
  present, values sane (e.g. `mean` between `min`/`max`, `first`/`last` match raw).
- `make_step_table` on raw **without** `ref_potential` (drop the column) → no
  `ref_potential_*` columns, engine unaffected (covers the "absent" path).
- Existing guards that must stay green: `test_config_columns.py` (code↔spec),
  `test_header_mapping.py` (totality/round-trip), `test_golden.py` (legacy parity).

## Open questions

1. **Native name — `ref_potential` (recommended) or `ref_voltage`?** The issue title
   offers both; spec convention (`potential`, not `voltage`) points to `ref_potential`.
   A third option is the aux scheme (`aux_potential_ref`), but the engine does not
   aggregate `aux_*` columns, and the issue explicitly asks for a first-class
   `RawCols` entry.
2. **Absent-column behaviour — skip (recommended) or emit nulls?** The issue text says
   "null where absent", and the old migration-doc decision said "always emit the full
   StepCols set with nulls" — but the shipped Phase-2 engine *skips* absent signals
   (`internal_resistance` behaves this way today). Recommend skip-when-absent for engine
   consistency; switching the whole engine to emit-null-columns is a separate issue if
   wanted.
3. **Sequencing vs release #44.** The 2026-07 code review sequences #43 *after* tagging
   `v0.1.0` (#44). Additive and low-risk, so doing it now is safe — but confirm you want
   #43 before the release.
