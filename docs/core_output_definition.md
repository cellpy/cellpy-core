# Cellpy Core Output (DRAFT)

Updated definition  
**Date:** 2025-10-03  
**SPEED-17:** "Define the object that comes out of cellpy core"

## Purpose
- Augment data object with *Cellpy Core Output*:
  - StepTable
    - Defined in [step_table_definition.md](./step_table_definition.md)
  - CycleTable
    - Defined in [cycle_table_definition.md](./cycle_table_definition.md)
- Update Harmonized_Raw
  - If necessary: update Harmonized_Raw with calculated steps (from StepTable)


## Updated Harmonized_Raw

Additional calculations when necessary:
- Calculate step type and step mode (for steptable and then update)
- Decide on how to handle cycler-specific measurement points that don't follow the time series (e.g. internal resistances at start/end of a cycle)
  - option 1: forward fill values (ethical concerns!!!)
    - could add prefix to indicate what was done in the processing


## StepTable
- Use unique step numbers
- one row for each individual sequential step
- do things to speed up calculations (e.g. for pulsing)

### Headers
- Min, Max, delta, time-average, capacity-average, arithmetic-mean, stdv, medians, first, last
- First, last, delta
  - Cycle number
  - Step number, substep number and type and mode
  - Original datapoint number and index
- Mask (Boolean)

