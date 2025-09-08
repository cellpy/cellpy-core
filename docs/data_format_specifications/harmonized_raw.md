# Cellpy Core Harmonized Raw (DRAFT)

Date: 2025-09-08

## Purpose

Original cyclers files are converted to this format, in order to unify the format so only one importer have to be used wherever it will be imported.

## Column Headers

| Column name | Data type | Unit | Sample data |
| --- | --- | --- | --- |
| source_type | str(10) | - | "Neware" |
| source_uuid | str(36) | - | "e15b46ca-e584-467f-a176-8bf98b8090e5" |
| source_datapoint_num | int | - | 1234 |
| datapoint_num | int | - | 1234 |
| step_num | int | - | 123 |
| cycle_num | int | - | 12 |
| epoch_time_utc | float | second | 1715609528.578140 |
| test_time | float | second | 12.43212 |
| mode | str(10) | - | "CCCV", "CC", "CP", etc. |
| channel_status | str(10) | -  | "active", "inactive" |
| step_type | str(10) | - | "charge", "discharge", "rest", etc. |
| step_type_detail | str(10) | - | (to be used to give additional info about steps, for example when a test is interrupted) |
| potential | float | Volt | 3.6500 |
| current | float | Ampere | 96.4413 |
| temperature_cell | float | degrees celcius | 25.3 |
| temperature_chamber | float | degrees celcius | 25.0 |
| pressure | float | mbar | 123.4 |
| step_cumulative_charge_capacity | float | Ah | 34.5678 |
| step_cumulative_discharge_capacity | float | Ah | 34.5678 |
