# Status — issue #29: create a test harmonized raw file

- [x] Done

## What landed

- **`dev/make_harmonized_raw.py`** — pure-polars helper that renames the committed
  legacy `tests/data/arbin_cc_raw.parquet` into the harmonized schema. Output
  header names are read from `cellpycore.config.RawCols` at runtime via the
  `LEGACY_TO_RAWCOLS` map, so re-running after any `RawCols` change regenerates an
  up-to-date fixture with no edits to the script (the issue's core requirement).
  Never imports `cellpy`/loaders (loader-free core).
- **`tests/data/arbin_cc_harmonized_raw.parquet`** — generated fixture: 10 261 rows,
  28 cols (full `RawCols` schema, spec order, 18 cycles).
- **`tests/test_harmonized_fixture.py`** — regression guard: columns match
  `RawCols`, row count + `mask`/`source_type`/`epoch_time_utc` sanity.
- Docs: `tests/data/README.md` (new fixture row + regeneration command),
  `docs/data_format_specifications/harmonized_raw.md` (note that `epoch_time_utc`
  is derived by treating a naive tester datetime as UTC — the one non-obvious
  mapping), and `.issueflows/04-designs-and-guides/test-data-and-fixtures.md`
  (follow-up bullet marked partly-done).

## Mapping decisions

- `voltage→potential`, `charge_capacity→cumulative_charge_capacity` (+ energy):
  legacy Arbin capacity is already cumulative-per-cycle-per-direction (issue #13),
  so straight renames, no recomputation.
- `data_point→datapoint_num` + `source_datapoint_num`; `step_index→step_num` +
  `source_step_num`; `date_time→epoch_time_utc` (datetime→float epoch s).
- Generated: `mask`=True, `source_type`="arbin". Unmapped harmonized columns
  (step_type, step_mode, cycle_type, source_uuid, powers, aux_*) emitted as null.
- Dropped legacy-only / EIS columns: `is_fc_data`, `dv_dt`, `ac_impedance`,
  `aci_phase_angle`.

## Open-question resolutions (from the plan, implemented defaults)

1. Standalone script (not a stage in `regenerate_test_data.py`).
2. Full `RawCols` schema emitted (null-filling unmapped columns).
3. Added the small columns/shape regression test.
4. `epoch_time_utc` from naive `date_time` treated as UTC; documented in the spec.

## Verification

- `uv run python dev/make_harmonized_raw.py` → 10 261 rows, 28 cols.
- `uv run pytest` → **38 passed**. No lint errors.

## Remaining / follow-ups

- None required for this issue. Future (tracked in the design guide): native
  expected `StepCols`/cycle output fixtures; non-Arbin harmonized fixture.
