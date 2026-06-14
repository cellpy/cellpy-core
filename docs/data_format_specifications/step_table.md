# Cellpy Core StepTable (DRAFT)

Date: 2025-09-08 (reviewed in issue #10)

## Purpose

One row per individual sequential step. Holds per-step aggregates (min, max, mean,
std, first, last, delta) of the raw signals, used to speed up downstream cycle
calculations and to classify steps.

> **Note (issue #10):** the `power_*` aggregate columns below are currently named
> `power_capacity_*` in `src/cellpycore/config.py`. "Power" is not a capacity; the
> intended name is `power_*`. Renaming `config.py` is deferred to a follow-up issue
> (see `.issueflows/04-designs-and-guides/column-headers-review.md`).

## Column Headers

| Column name | Data type | Unit | Sample data | Description |
| --- | --- | --- | --- | --- |
| cycle_num | int | - | 12 | Cycle number |
| step_num | int | - | 123 | Step number |
| sub_step_num | int | - | 123 | Sub-step number |
| step_type | str(10) | - | "charge", "discharge", "rest", etc. | Step type |
| sub_step_type | str(10) | - | TBD | Sub-step type (semantics TBD) |
| mask | boolean | - | True | Selection flag; default True (row is selected / used) |
| datapoint_num_first | int | - | 123 | First datapoint number in step |
| datapoint_num_last | int | - | 123 | Last datapoint number in step |
| test_time_first | float | second (s) | 14.1231 | Test time at start of step |
| test_time_last | float | second (s) | 15.1231 | Test time at end of step |
| current_mean | float | Ampere (A) | 15.1231 | 
| current_std | float | Ampere (A) | 15.1231 | 
| current_min | float | Ampere (A) | 15.1231 | 
| current_max | float | Ampere (A) | 15.1231 | 
| current_first | float | Ampere (A) | 15.1231 | 
| current_last | float | Ampere (A) | 15.1231 | 
| current_delta | float | % | 15.1231 | 
| potential_mean | float | Volt (V) | 15.1231 | 
| potential_std | float | Volt (V) | 15.1231 | 
| potential_min | float | Volt (V) | 15.1231 | 
| potential_max | float | Volt (V) | 15.1231 | 
| potential_first | float | Volt (V) | 15.1231 | 
| potential_last | float | Volt (V) | 15.1231 | 
| potential_delta | float | % | 15.1231 |
| charge_capacity_mean | float | Ampere-hour (Ah) | 15.1231 | 
| charge_capacity_std | float | Ampere-hour (Ah) | 15.1231 | 
| charge_capacity_min | float | Ampere-hour (Ah) | 15.1231 | 
| charge_capacity_max | float | Ampere-hour (Ah) | 15.1231 | 
| charge_capacity_first | float | Ampere-hour (Ah) | 15.1231 | 
| charge_capacity_last | float | Ampere-hour (Ah) | 15.1231 | 
| charge_capacity_delta | float | % | 15.1231 |
| discharge_capacity_mean | float | Ampere-hour (Ah) | 15.1231 | 
| discharge_capacity_std | float | Ampere-hour (Ah) | 15.1231 | 
| discharge_capacity_min | float | Ampere-hour (Ah) | 15.1231 | 
| discharge_capacity_max | float | Ampere-hour (Ah) | 15.1231 | 
| discharge_capacity_first | float | Ampere-hour (Ah) | 15.1231 | 
| discharge_capacity_last | float | Ampere-hour (Ah) | 15.1231 | 
| discharge_capacity_delta | float | % | 15.1231 |
| power_mean | float | Watt (W) | 15.1231 | 
| power_std | float | Watt (W) | 15.1231 | 
| power_min | float | Watt (W) | 15.1231 | 
| power_max | float | Watt (W) | 15.1231 | 
| power_first | float | Watt (W) | 15.1231 | 
| power_last | float | Watt (W) | 15.1231 | 
| power_delta | float | % | 15.1231 |
| charge_energy_mean | float | Watt-hour (Wh) | 15.1231 | 
| charge_energy_std | float | Watt-hour (Wh) | 15.1231 | 
| charge_energy_min | float | Watt-hour (Wh) | 15.1231 | 
| charge_energy_max | float | Watt-hour (Wh) | 15.1231 | 
| charge_energy_first | float | Watt-hour (Wh) | 15.1231 | 
| charge_energy_last | float | Watt-hour (Wh) | 15.1231 | 
| charge_energy_delta | float | % | 15.1231 |      
| discharge_energy_mean | float | Watt-hour (Wh) | 15.1231 | 
| discharge_energy_std | float | Watt-hour (Wh) | 15.1231 | 
| discharge_energy_min | float | Watt-hour (Wh) | 15.1231 | 
| discharge_energy_max | float | Watt-hour (Wh) | 15.1231 | 
| discharge_energy_first | float | Watt-hour (Wh) | 15.1231 | 
| discharge_energy_last | float | Watt-hour (Wh) | 15.1231 | 
| discharge_energy_delta | float | % | 15.1231 |      