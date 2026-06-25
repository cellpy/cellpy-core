# Cellpy Core Harmonized_Raw

**Authoritative definition** — this is the single source of truth for the harmonized raw
format. (Moved here from `docs/harmonized_raw_definition.md`; it supersedes the older
2025-09-08 draft that was removed in issue #10.)

**Date:** 2025-09-17 (reviewed in issue #10)  
**SPEED-16:** "Define the object that goes into cellpy core"

## Purpose

Original cycler files are converted to this format, in order to unify the format so that only one importer has to be used wherever it will be imported.

## Conventions

- The cell voltage column is named **`potential`** (not `voltage`).
- Time columns (`test_time`, etc.) are in **seconds**.
- The cycler step mode column is **`step_mode`**. There is no `channel_status` column
  (it was dropped in issue #10).
- **`epoch_time_utc`** is float **seconds since the Unix epoch, UTC**. When an importer
  only has the cycler's wall-clock timestamp (often a *naive*, timezone-less datetime,
  e.g. legacy Arbin `date_time`), it is converted to epoch seconds by treating the naive
  timestamp as UTC. (Example: `dev/make_harmonized_raw.py` does this when building the
  `arbin_cc_harmonized_raw.parquet` test fixture.)
- Capacity / energy columns are **cumulative per cycle, per direction** — see *Capacity
  convention* below. (Renamed from `step_cumulative_*` in issue #13; the old name was
  misleading.)

## Column Headers

Set up a flexible structure that allows for more columns.

| Column name | Data type | Unit | Sample data |  Comment |
| --- | --- | --- | --- | --- |
| datapoint_num | int | - | 1234 | index, corrected sequential datapoints |
| source_datapoint_num | int | - | 1234 | original data point number from data collection |
| mask | boolean | - | True | default: True (meaning: this value is selected and used) |
| epoch_time_utc | float | second | 1715609528.578140 | - |
| test_time | float | second | 12.43212 | - |
| step_time | float | second | 12.43212 | optional value; time elapsed since the start of the current step |
| source_type | str(10) | - | "Neware" | - |
| source_uuid | str(36) | - | "e15b46ca-e584-467f-a176-8bf98b8090e5" | will not be used, only kept for info and tracability |
| test_id | int | - | 0 | compact per-test key within a (possibly merged) object; 0 for a single test. Group keys are (test_id, cycle_num, step_num, ...). Global identity: source_uuid |
| step_num | int | - | 123 | updated unique and sequential step number |
| source_step_num | int | - | 123 | original step number |
| step_type | str(10) | - | "charge", "discharge", "rest", etc. | optional value |
| step_type_detail | str(10) | - | - | optional value; (to be used to give additional info about steps, for example when a test is interrupted) |
| step_mode | str(10) | - | "CV", "CC", "CP", "None" | optional value |
| cycle_num | int | - | 12 | - |
| cycle_type | str(36) | - | "Standard", "GITT", "ICI", "Characterization" | categorial column; in first version: pre-defined input |
| potential | float | Volt | 3.6500 | - |
| current | float | Ampere | 96.4413 | - |
| cumulative_charge_capacity | float | Ah | 34.5678 | cumulative per cycle, per direction (resets at each cycle boundary); per-step / per-cycle values are derived downstream — see *Capacity convention* below |
| cumulative_discharge_capacity | float | Ah | 34.5678 | cumulative per cycle, per direction (see *Capacity convention*) |
| cumulative_charge_energy | float | Wh | 34.5678 | ** ; cumulative per cycle, per direction (see *Capacity convention*) |
| cumulative_discharge_energy | float | Wh | 34.5678 | ** ; cumulative per cycle, per direction (see *Capacity convention*) |
| step_charge_power | float | W | 34.5678 | ** |
| step_discharge_power | float | W | 34.5678 | ** |
| internal_resistance | float | ohm | 56.4866 | optional value; instrument-reported internal resistance |
| aux_temperature_cell | float | degrees celcius | 25.3 | - |
| aux_temperature_chamber | float | degrees celcius | 25.0 | - |
| aux_pressure_cell | float | mbar | 123.4 | - |


** calculate if empty; keep if filled (can be overridden by argument)

### Capacity convention

`cumulative_charge_capacity` / `cumulative_discharge_capacity` (and the matching energy
columns) are **cumulative per cycle, per direction**: within a cycle they accumulate across
that cycle's steps for their direction, and reset to `0` at each cycle boundary. This matches
how legacy cellpy raw data is supplied (verified on real Arbin data in issue #13) and is what
the summary path relies on (the per-cycle capacity is read from the cycle's last datapoint).

Downstream values are **derived**, not stored in raw:
- **per-step** capacity = the in-step delta (last − first within a step group), produced in
  the step table;
- **per-cycle** capacity = the cycle-end cumulative value, produced in the cycle/summary
  table.

Importers must deliver cycle-cumulative capacity. (Accepting step-/test-cumulative raw and
normalizing the reset granularity inside the engine is a possible future extension.)

### Auxillary columns  
Option for more auxillary columns; naming scheme:
- aux_temperature_[arbitrary name]
- aux_potential_[]
- aux_pressure_[]
- aux_resistance_[]

## Test metadata (TestMeta)

Per-test metadata, **one record per test**, keyed by `test_id` (the same `test_id` carried
on every raw row). This is where test-level descriptors live so they are **not** repeated on
every raw row; it is what lets a single object hold many merged test files efficiently (see
`.issueflows/04-designs-and-guides/test-metadata-and-merging.md`). When several tests are
merged, `TestMeta` holds one row per `test_id`.

Test-level descriptors that are constant within a test (e.g. `test_family`, `test_type`,
`cycle_mode`) belong here, **not** in the raw columns.

This spec remains authoritative for the field set. The fields below now also have a code home
as the `TestMeta` / `CellMeta` dataclasses in `cellpycore.metadata` (scaffolding; see
`.issueflows/04-designs-and-guides/metadata-scaffolding.md`, issue #30).

| Field | Data type | Unit | Sample data | Comment |
| --- | --- | --- | --- | --- |
| test_id | int | - | 0 | key; matches `raw.test_id` (the per-test grouping key) |
| uuid | str(36) | - | "e15b46ca-e584-467f-a176-8bf98b8090e5" | stable, globally-unique id for this test run |
| cell_name | str | - | "cell_001" | human-readable cell / test name |
| test_family | str(36) | - | "rate test" | broad classification of the overall test |
| test_type | str(36) | - | "GITT" | detailed classification within a family |
| cycle_mode | str(10) | - | "anode" | "anode" / "cathode" / "full" |
| source_kind | str(10) | - | "file" | where the data came from: "file", "db", "api", ... |
| source_type | str(20) | - | "Neware" | cycler / instrument type |
| source_uri | str | - | "/data/run1.ndax" or "db://cellpydb/tests/123" | file path or DB/API locator for the source |
| source_uuid | str(36) | - | "..." | original identifier from the source (matches `raw.source_uuid`) |
| raw_file_names | list[str] | - | ["run1.ndax"] | original raw file(s) backing this test |
| schedule_file_name | str | - | "rate_test.sdu" | cycler schedule / protocol file |
| creator | str | - | "jdoe" | who produced / imported the test |
| channel | str | - | "12" | tester channel id |
| tester_id | str | - | "neware-01" | tester / server identity |
| start_datetime | datetime (ISO 8601) | - | "2026-06-14T10:00:00+02:00" | test start time (from the cycler) |
| time_zone | str | - | "Europe/Oslo" | time zone for naive timestamps |
| loaded_datetime | datetime (ISO 8601) | - | "2026-06-14T12:30:00Z" | when the data was obtained / imported into cellpy |
| comment | str | - | "" | free text |

**Cell / material metadata (optional).** Physical cell properties (mass, total mass,
nominal capacity + specifics, active-electrode area / loading / thickness, electrode and
electrolyte types, experiment type, ...) are also per-test/per-cell. Legacy cellpy already
defines these in `cellpy.parameters.internal_settings.CellpyMetaCommon` (cell/material/
geometry) and `CellpyMetaIndividualTest` (test-dependent: `channel_index`, `creator`,
`schedule_file_name`, `voltage_lim_low/high`, `cycle_mode`, `test_ID`). Mine those for the
full field set; they can sit in `TestMeta` or a sibling `CellMeta` record (decision
deferred — see the design note).

## Follow-ups
- **step_types**
  - 'charge', 'discharge', 'rest'
  - limit to those or allow for others?
  - how to deal with 'IR' steps in Arbin or other cycler specific step-types?
  - *Reference vocabulary now defined as `cellpycore.config.StepType` (issue #24); it is a non-validating reference set, so other values are still allowed.*
- **step_type_detail**
  - how is this is intended to be used
- **step_mode**
  - "CV", "CC", "CP", "None"
  - similar to step_type: limit to those, or allow for more?
  - *Reference vocabulary now defined as `cellpycore.config.StepMode` (`CC`/`CV`/`CP`); "None" means a null/missing value, not a stored string (issue #24).*
- **Substep Number**
  - in our previous notes we listed "substep number"
  - do we need this? and if so, what would it be used for?
- **epoch_time_utc**
  - should this be a float or a datetime object?
- **cycle_num**
  - usually provided by the tester
  - enough with keeping it, or do we need an updated cycle number?
- **cycle_type**
  - details to be discussed
  - *Reference vocabulary now defined as `cellpycore.config.CycleType` (`Standard`/`GITT`/`ICI`/`Characterization`); may later migrate to test metadata as `test_type` (issue #24).*
- **test_family / test_type** (now in **TestMeta**, not raw columns)
  - `test_family` is the broad classification (e.g. "reference capacity test", "rate test");
    `test_type` is the detailed one within a family (e.g. "GITT", "current interrupt").
  - limit to a controlled vocabulary, or allow free text? (same open question as `cycle_type` / `step_mode`)
- **channel_status** — *Resolved (issue #10): removed.* Not part of the harmonized raw format.
- **source_uuid**
  - does this contain info about the channel?
  - if not, should we add a channel number/identifyer? (string)
- **test_id / merging**
  - `test_id` is the compact per-row key that lets a single object hold many merged test
    files; downstream grouping must use composite keys `(test_id, cycle_num, step_num, ...)`
    because `cycle_num`/`step_num` collide across files.
  - test-level descriptors (`test_family`, `test_type`, mass, nominal capacity, cycle_mode,
    ...) should live in a normalized per-test metadata table keyed by `test_id` rather than
    be repeated on every raw row. See
    `.issueflows/04-designs-and-guides/test-metadata-and-merging.md`.




### Other discussion points
- **Units**
  - Units (based on Rasmus' suggestion) are included in the header table above
- EIS, cyclic voltametry, 3-electrode setup
- **Data resolution** (for definition of step types)

