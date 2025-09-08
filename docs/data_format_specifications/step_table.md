# Cellpy Core StepTable (DRAFT)

Date: 2025-09-08

## Purpose


## Column Headers

| Column name | Data type | Unit | Sample data |
| --- | --- | --- | --- |
| cycle_num | int | - | 12 | Cycle number 
| step_num | int | - | 123 | Step number 
| sub_step_num | int | - | 123 | Sub-step number 
| step_type | str(10) | - | "charge", "discharge", "rest", etc. 
| sub_step_type | str(10) | - | TBD | 
| datapoint_num_first | int | - | 123 | 
| datapoint_num_last | int | - | 123 | 
| test_time_first | float | second (s) | 14.1231 | 
| test_time_last | float | second (s) | 15.1231 | 
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
| power_capacity_mean | float | Watt (W) | 15.1231 | 
| power_capacity_std | float | Watt (W) | 15.1231 | 
| power_capacity_min | float | Watt (W) | 15.1231 | 
| power_capacity_max | float | Watt (W) | 15.1231 | 
| power_capacity_first | float | Watt (W) | 15.1231 | 
| power_capacity_last | float | Watt (W) | 15.1231 | 
| power_capacity_delta | float | % | 15.1231 |
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