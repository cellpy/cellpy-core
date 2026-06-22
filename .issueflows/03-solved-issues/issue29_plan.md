# Plan for issue #29: create a test harmonized raw file

## Goal

Add a `dev/` helper script that converts the existing legacy-named
`tests/data/arbin_cc_raw.parquet` into a **harmonized raw** parquet whose headers
come straight from `cellpycore.config.RawCols`, so we have a real-data fixture in
the native (harmonized) schema. Re-running the script after any `RawCols` change
must regenerate an up-to-date file with no further edits.

## Constraints

- KISS: one new `dev/` script + one generated parquet + doc touch-ups. No new
  runtime dependency (pure `polars`, already used).
- Loader-free core principle (see `test-data-and-fixtures.md`): the script reads
  the committed legacy parquet, never imports `cellpy` or any instrument loader.
- Headers must be **derived from `RawCols`**, not hard-coded, so the file tracks
  future schema renames automatically (the issue's core requirement).
- Capacity convention (see `docs/data_format_specifications/harmonized_raw.md` →
  *Capacity convention*): legacy Arbin `charge_capacity` / `discharge_capacity`
  are already cumulative-per-cycle-per-direction (verified on real Arbin data in
  issue #13), so the mapping is a **straight rename — no recomputation**.

### Prior art

- `create_raw_data` (`cellpycore._helpers`) — convention: builds a polars frame
  keyed by `RawCols()` attributes (`data = {raw_cols.epoch_time_utc: ...}`) so
  header names follow the schema. New work: **mirror** this pattern — build the
  output frame from `RawCols()` attributes via a legacy→attribute map.
- `dev/regenerate_test_data.py` — convention: documented multi-stage test-data
  generator writing into `tests/data/`, with provenance in `tests/data/README.md`.
  New work: **coexist** as a separate, dependency-light script (Stage A/B there
  need `cellpy`/ODBC; this conversion is pure-polars and independent). See open
  question 1.
- `tests/data/README.md` + `.issueflows/04-designs-and-guides/test-data-and-fixtures.md`
  — the latter already lists "add native-schema parquet fixtures (RawCols naming)"
  as an open follow-up; this issue delivers exactly that.

## Approach

1. **Mapping table** (legacy `HeadersNormal` → `RawCols` *attribute name*), the
   single place a maintainer edits if the source columns change:

   | legacy column      | RawCols attr(s)                         | note |
   |--------------------|-----------------------------------------|------|
   | `test_id`          | `test_id`                               | direct |
   | `data_point`       | `datapoint_num`, `source_datapoint_num` | one source fills both |
   | `test_time`        | `test_time`                             | seconds, direct |
   | `step_time`        | `step_time`                             | seconds, direct |
   | `date_time`        | `epoch_time_utc`                        | datetime→float epoch seconds (non-obvious, see below) |
   | `step_index`       | `step_num`, `source_step_num`           | one source fills both |
   | `cycle_index`      | `cycle_num`                             | direct |
   | `current`          | `current`                               | direct |
   | `voltage`          | `potential`                             | rename (spec convention) |
   | `charge_capacity`  | `cumulative_charge_capacity`            | straight rename (cumulative-per-cycle) |
   | `discharge_capacity`| `cumulative_discharge_capacity`        | straight rename |
   | `charge_energy`    | `cumulative_charge_energy`              | straight rename |
   | `discharge_energy` | `cumulative_discharge_energy`           | straight rename |
   | `internal_resistance`| `internal_resistance`                 | direct |

   **Dropped** (no harmonized equivalent; cellpy-internal / EIS): `is_fc_data`,
   `dv_dt`, `ac_impedance`, `aci_phase_angle`. Logged so the drop is explicit.

2. **Generated / constant columns**: `mask` = `True`; `source_type` = `"arbin"`.

3. **Unmapped harmonized columns** emitted as nulls so the fixture is a *complete*
   `RawCols` example: `source_uuid`, `step_type`, `step_type_detail`, `step_mode`,
   `cycle_type`, `step_charge_power`, `step_discharge_power`, `aux_temperature_cell`,
   `aux_temperature_chamber`, `aux_pressure_cell` (see open question 2).

4. **`epoch_time_utc`**: legacy `date_time` is a naive `Datetime`; convert with
   `pl.col("date_time").dt.epoch("ms") / 1000.0` (float seconds), treating the
   naive timestamp as UTC. This is the one non-obvious rename → documented in the
   spec (open question 4).

5. **Output column order** follows the `RawCols` attribute order so the file
   mirrors the spec table; write to `tests/data/arbin_cc_harmonized_raw.parquet`.

6. Build output frame from `RawCols()` attributes (mirrors `create_raw_data`), so
   renaming e.g. `RawCols.potential` and re-running yields the new header with no
   script edit.

## Files to touch

- `dev/make_harmonized_raw.py` — new script (read legacy parquet, apply map, write
  harmonized parquet; small `if __name__ == "__main__"` + a docstring with usage).
- `tests/data/arbin_cc_harmonized_raw.parquet` — generated output (committed).
- `tests/data/README.md` — add the new fixture row + a "Harmonized fixture" note
  and how to regenerate it.
- `docs/data_format_specifications/harmonized_raw.md` — add a short note that
  `epoch_time_utc` is derived from a tester datetime (naive→UTC) — only the one
  non-obvious mapping, per the issue ("if not obvious, amend the documentation").
- `.issueflows/04-designs-and-guides/test-data-and-fixtures.md` — tick off / update
  the "native-schema parquet fixtures" follow-up bullet.
- (optional) `tests/test_harmonized_fixture.py` — see Test strategy / open question 3.

## Test strategy

- Run `uv run python dev/make_harmonized_raw.py` and confirm: 10 261 rows; output
  column set == `set(vars-of RawCols())`; no leftover legacy names; `potential`,
  `cumulative_charge_capacity`, `epoch_time_utc` populated; `mask` all `True`.
- (optional) add `tests/test_harmonized_fixture.py` asserting the fixture's columns
  match `RawCols()` and row count is stable — cheap regression guard.
- `uv run pytest` to confirm nothing else breaks.

## Open questions

1. **Standalone script vs. a stage in `regenerate_test_data.py`?** Recommend
   **standalone** `dev/make_harmonized_raw.py` (issue says "create a helper
   script"; it's pure-polars and independent of the cellpy/ODBC stages). OK to
   instead fold it in as a "Stage C" if you'd rather keep one generator.
2. **Emit the full `RawCols` schema (null-filling unmapped columns) or only the
   mapped subset?** Recommend **full schema** (better as a canonical example /
   future engine fixture). Subset is leaner if you prefer.
3. **Add a regression test for the fixture now**, or leave testing for when the
   native engine path consumes it? Recommend a **tiny columns/shape test**.
4. **`epoch_time_utc` from naive `date_time` as UTC** — acceptable approximation
   for a test fixture, and document it in the spec?
