# Cellpy Core Harmonized_Raw (DRAFT)

Updated definition  
**Date:** 2025-09-17  
**SPEED-16:** "Define the object that goes into cellpy core"

## Purpose

Original cycler files are converted to this format, in order to unify the format so that only one importer has to be used wherever it will be imported.

## Column Headers

Set up a flexible structure that allows for more columns.

| Column name | Data type | Unit | Sample data |  Comment |
| --- | --- | --- | --- | --- |
| datapoint_num | int | - | 1234 | index, corrected sequential datapoints |
| source_datapoint_num | int | - | 1234 | original data point number from data collection |
| mask | boolean | - | True | default: True (meaning: this value is selected and used) |
| epoch_time_utc | float | second | 1715609528.578140 | - |
| test_time | float | second | 12.43212 | - |
| source_type | str(10) | - | "Neware" | - |
| source_uuid | str(36) | - | "e15b46ca-e584-467f-a176-8bf98b8090e5" | will not be used, only kept for info and tracability |
| step_num | int | - | 123 | updated unique and sequential step number |
| source_step_num | int | - | 123 | original step number |
| step_type | str(10) | - | "charge", "discharge", "rest", etc. | optional value |
| step_type_detail | str(10) | - | - | optional value; (to be used to give additional info about steps, for example when a test is interrupted) |
| step_mode | str(10) | - | "CV", "CC", "CP", "None" | optional value |
| cycle_num | int | - | 12 | - |
| cycle_type | str(36) | - | "Standard", "GITT", "ICI", "Characterization" | categorial column; in first version: pre-defined input |
| potential | float | Volt | 3.6500 | - |
| current | float | Ampere | 96.4413 | - |
| step_cumulative_charge_capacity | float | Ah | 34.5678 | - |
| step_cumulative_discharge_capacity | float | Ah | 34.5678 | - |
| step_cumulative_charge_energy | float | Wh | 34.5678 | ** |
| step_cumulative_discharge_energy | float | Wh | 34.5678 | ** |
| step_charge_power | float | W | 34.5678 | ** |
| step_discharge_power | float | W | 34.5678 | ** |
| aux_temperature_cell | float | degrees celcius | 25.3 | - |
| aux_temperature_chamber | float | degrees celcius | 25.0 | - |
| aux_pressure_cell | float | mbar | 123.4 | - |


** calculate if empty; keep if filled (can be overridden by argument)

### Auxillary columns  
Option for more auxillary columns; naming scheme:
- aux_temperature_[arbitrary name]
- aux_potential_[]
- aux_pressure_[]
- aux_resistance_[]

## Follow-ups
- **step_types**
  - 'charge', 'discharge', 'rest'
  - limit to those or allow for others?
  - how to deal with 'IR' steps in Arbin or other cycler specific step-types?
- **step_type_detail**
  - how is this is intended to be used
- **step_mode**
  - "CV", "CC", "CP", "None"
  - similar to step_type: limit to those, or allow for more?
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
- **channel_status**
  - | channel_status | str(10) | -  | "active", "inactive" | --- |
  - part of Rasmus' suggestion - what is it used for?
  - suggest removing?
- **source_uuid**
  - does this contain info about the channel?
  - if not, should we add a channel number/identifyer? (string)




### Other discussion points
- **Units**
  - Units (based on Rasmus' suggestion) are included in the header table above
- EIS, cyclic voltametry, 3-electrode setup
- **Data resolution** (for definition of step types)

