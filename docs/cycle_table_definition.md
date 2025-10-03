# Cellpy Core CycleTable

Updated definition  
**Date:** 2025-10-03  
**SPEED-17:** "Define the object that comes out of cellpy core"

## Column Headers

| Column name | Data type | Unit | Sample data | Description |
| --- | --- | --- | --- | --- |
| cycle_num | int | - | 12 | Cycle number |
| datapoint_num_first | int | - | 123 | First datapoint number in cycle |
| datapoint_num_last | int | - | 123 | Last datapoint number in cycle | 
| first_epoch_time_utc | float | Seconds (s) | UNIX timestamp for first datapoint in cycle (in UTC) |
| last_epoch_time_utc | float | Seconds (s) | UNIX timestamp for last datapoint in cycle (in UTC) |
| first_test_time | float | Seconds (s) | Seconds since start of test at the beginning of cycle |
| last_test_time | float | Seconds (s) | Seconds since start of test at the end of cycle |
| cycle_duration | float | Seconds (s) | Duration of cycle (last_epoch_time_utc - first_epoch_time_utc) |
| charge_duration | float | Seconds (s) | Duration of charge steps. |
| discharge_duration | float | Seconds (s) | Duration of discharge steps. |
| rest_duration | float | Seconds (s) | Duration of rest steps. |
| charge_capacity | float | Ampere-hour (Ah) | 34.1234 | Total charge capacity in current cycle. |
| discharge_capacity | float | Ampere-hour (Ah) | 34.1234 | Total discharge capacity in current cycle. |
| charge_capacity_loss | float | Ampere-hour (Ah) | 34.1234 | Charge capacity loss (charge capacity_n-1 - charge capacity_n) |
| discharge_capacity_loss | float | Ampere-hour (Ah) | 34.1234 | Discharge capacity loss (discharge capacity_n-1 - discharge capacity_n) |
| coulombic_difference | float | Amphere-hour (Ah) | 34.1234 | Coulombic difference (charge capacity - discharge capacity) |
| coulombic_efficiency | float | Percentage (%) | 99.95 | Coulombic efficiency (discharge capacity/charge capacity * 100%) |
| test_cumulated_charge_capacity | float | Ampere-hour (Ah) | 34.1234 | Cumulated charge capacity throughout test. |
| test_cumulated_discharge_capacity | float | Ampere-hour (Ah) | 34.1234 | Cumulated discharge capacity throughout test. |
| test_cumulated_coulombic_difference | float | Ampere-hour (Ah) | 34.1234 | Cumulated Coulombic difference throughout test. | 
| test_cumulated_charge_capacity_loss | float | Ampere-hour (Ah) | 34.1234 | Cumulated charge capacity loss throughout test. |
| test_cumulated_discharge_capacity_loss | float | Ampere-hour (Ah) | 34.1234 | Cumulated discharge capacity loss throughout test. |
| test_net_capacity | float | Ampere-hour (Ah) | 34.1234 | Net total capacity throughout test. |
| charge_energy | float | Watt-hour (Wh) | 34.1234 | Total charge energy in current cycle.  |
| discharge_energy | float | Watt-hour (Wh) | 34.1234 | Total discharge energy in current cycle. |
| cycle_net_energy | float | Watt-hour (Wh) | 34.1234 | (charge energy - discharge energy) |
| energy_efficiency | float | Percentage (%) | 99.95 | Energy efficiency (discharge energy/charge energy * 100%) |
| test_cumulated_charge_energy | float | Watt-hour (Ah) | 34.1234 | Cumulated charge energy throughout test. |
| test_cumulated_discharge_energy | float | Watt-hour (Ah) | 34.1234 | Cumulated discharge energy throughout test. |
| test_net_energy | float | float | Watt-hour (Wh) | 34.1234 | Net total energy throughout test. | 
| current_charge_mean | float | Ampere (A) | 3.1234 | Arithmetic mean of current during charge step. |
| current_charge_mean_tw | float | Ampere (A) | 3.1234 | Time-weighted mean of current during charge step. |
| current_charge_mean_cw | float | Ampere (A) | 3.1234 | Capacity-weighted mean of current during charge step. |
| current_charge_max | float | Ampere (A) | 3.1234 | Maximum current value during charge step. |
| current_charge_min | float | Ampere (A) | 3.1234 | Minimum current value during charge step. |
| current_discharge_mean | float | Ampere (A) | 3.1234 | Arithmetic mean of current during discharge step. |
| current_discharge_mean_tw | float | Ampere (A) | 3.1234 | Time-weighted mean of current during discharge step. |
| current_discharge_mean_cw | float | Ampere (A) | 3.1234 | Capacity-weighted mean of current during discharge step. |
| current_discharge_max | float | Ampere (A) | 3.1234 | Maximum current value during discharge step. |
| current_discharge_min | float | Ampere (A) | 3.1234 | Minimum current value during discharge step. |
| potential_charge_mean | float | Volt (V) | 3.1234 | Arithmetic mean of potential during charge step. |
| potential_charge_mean_tw | float | Volt (V) | 3.1234 | Time-weighted mean of potential during charge step. |
| potential_charge_mean_cw | float | Volt (V) | 3.1234 | Capacity-weighted mean of potential during charge step. |
| potential_charge_max | float | Volt (V) | 3.1234 | Maximum potential value during charge step. |
| potential_charge_min | float | Volt (V) | 3.1234 | Minimum potential value during charge step. |
| potential_discharge_mean | float | Volt (V) | 3.1234 | Arithmetic mean of potential during discharge step. |
| potential_discharge_mean_tw | float | Volt (V) | 3.1234 | Time-weighted mean of potential during discharge step. |
| potential_discharge_mean_cw | float | Volt (V) | 3.1234 | Capacity-weighted mean of potential during discharge step. |
| potential_discharge_max | float | Volt (V) | 3.1234 | Maximum potential value during discharge step. |
| potential_discharge_min | float | Volt (V) | 3.1234 | Minimum potential value during discharge step. |
| potential_start_charge | float | Volt (V) | 4.7 | First value of the potential in the charge step. |
| potential_end_charge | float | Volt (V) | 4.7 | Last value of the potential in the charge step. |
| potential_start_discharge | float | Volt (V) | 4.7 | First value of the potential in the discharge step. |
| potential_end_discharge | float | Volt (V) | 4.7 | Last value of the potential in the discharge step. |
| voltage_efficiency | float | Percentage (%) | 99.00 | Energy efficiency divided by Coulombic efficiency |
| power_charge_mean | float | Watt (W) | 3.1234 | Arithmetic mean of power during charge step. |
| power_charge_mean_tw | float | Watt (W) | 3.1234 | Time-weighted mean of power during charge step. |
| power_charge_mean_cw | float | Watt (W) | 3.1234 | Capacity-weighted mean of power during charge step. |
| power_charge_max | float | Watt (W) | 3.1234 | Maximum power value during charge step. |
| power_charge_min | float | Watt (W) | 3.1234 | Minimum power value during charge step. |
| power_discharge_mean | float | Watt (W) | 3.1234 | Arithmetic mean of power during discharge step. |
| power_discharge_mean_tw | float | Watt (W) | 3.1234 | Time-weighted mean of power during discharge step. |
| power_discharge_mean_cw | float | Watt (W) | 3.1234 | Capacity-weighted mean of power during discharge step. |
| power_discharge_max | float | Watt (W) | 3.1234 | Maximum power value during discharge step. |
| power_discharge_min | float | Watt (W) | 3.1234 | Minimum power value during discharge step. |
| ir_start_charge | float | Ohm (Ω) | 0.1234 | Estimated internal resistance at start of charge |
| ir_end_charge | float | Ohm (Ω) | 0.1234 | Estimated internal resistance at end of charge |
| ir_start_discharge | float | Ohm (Ω) | 0.1234 | Estimated internal resistance at start of discharge |
| ir_end_discharge | float | Ohm (Ω) | 0.1234 | Estimated internal resistance at end of discharge |
| relaxation_potential_charge | float | Volt(V) | 4.1234 | Potential straight after end of charge step |
| relaxation_potential_discharge | float | Volt (V) | 4.1234  | Potential straight after end of discharge step |
| open_circuit_potential_charge | float | Volt (V) | 4.1234 | Potential at the end of a rest step following end of charge step |
| open_circuit_potential_discharge | float | Volt (V) | 4.1234 | Potential at the end of a rest step following end of discharge step | 
| cv_share | float | Percentage (%) | 3.412 | Share of total charge capacity from cycling in CV-mode |
| cv_charge_capacity | float | Ampere-hour (Ah) | 3.1234 | Total cycle charge capacity from cycling in CV-mode |
| cv_charge_energy | float | Watt-hour (Wh) | 3.1234 | Total cycle charge energy from cycling in CV-mode |
| cv_charge_time | float | Seconds (s) | 3.1234 | Total cycle charge time cycling in CV-mode |
| cc_charge_capacity | float | Ampere-hour (Ah) | 3.1234 | Total cycle charge capacity from cycling in CC-mode |
| cc_charge_energy | float | Watt-hour (Wh) | 3.1234 | Total cycle charge energy from cycling in CC-mode |
| cc_charge_time | float | Seconds (s) | 3.1234 | Total cycle charge time cycling in CC-mode |
| aux_temperature_cell_mean | float | degrees celcius | 25.3 | Arithmetic mean of temperature during cycle |
| aux_temperature_cell_mean_tw | float | degrees celcius | 25.3 | Time-weighted mean of temperature during cycle |
| aux_temperature_cell_max | float | degrees celcius | 25.3 | Maximum temperature value during cycle |
| aux_temperature_cell_min | float | degrees celcius | 25.3 | Minimum temperature value during cycle |


### Auxillaries
For each auxillary column in harmonized_raw, the following columns will be added (datatype and unit will be carried over from harmonized raw):


| Column name | Data type | Unit | Sample data | Description |
| --- | --- | --- | --- | --- |
| aux_[xx]_[xx]_mean | float | unit | 25.3 | Arithmetic mean of xxx during cycle |
| aux_[xx]_[xx]_mean_tw | float | unit | 25.3 | Time-weighted mean of xxx during cycle |
| aux_[xx]_[xx]_max | float | unit | 25.3 | Maximum xxx value during cycle |
| aux_[xx]_[xx]_min | float | unit | 25.3 | Minimum xxx value during cycle |


## Open questions & Follow-ups
- need very good documentation how each of those columns is actually calculated
- If a cycle has multiple charge and discharge steps:
  - document which value is taken for
    - ir_start_charge, ir_start_discharge etc.
    - relaxation_potential_charge, relaxation_potential_discharge
    - open_circuit_potential_charge, open_circuit_potential_discharge	
- How to deal with dedicated resistance steps (e.g. as included in Arbins)?
- Resistances at different time scales?
- We have cc and cv shares - what about cp?
  - What additional columns would make sense with respect to CP?
- Should we also have cv_discharge_capacity etc.? (even though CCCV is more common for charge)
- Should we split auxillaries into charge and discharge as well?
- Check summary tables for PEC data from Preben
- Mask (Boolean) - how should this be included?
- Any other cumulated values to be added?


Doublecheck if we have
- charge and discharge difference
- Coulombic/Energy/Power efficiency