# Definition of Cellpy Core Functionality

## Cellpy Core Functionality
- Receive data object (Cellpy Core Input)
    - Harmonized_Raw (see below)
- Augment data object with *Cellpy Core Output*:
  - StepTable
    - See separate definition
  - CycleTable
    - See separate definition
- Update Harmonized_Raw
  - If necessary: update Harmonized_Raw with calculated steps (from StepTable) 



### Metadata
Metadata will be kept out of the core. Important to keep metadata in mind when setting up Cellpy Core, so that metadata can easily follow and be aligned with the data.

- Only keep metadata that is strictly necessary for use within core (to be defined as part of Harmonized_Raw)
    - cell-specifics
    - test information
      - tester, channel etc
    - raw data
      - where does the file come from?
      - when loaded, when changed etc.
      - Units, resolution


## Cellpy Core Input (Harmonized_Raw)
Summarized in [harmonized_raw_definition.md](./harmonized_raw_definition.md)

## Cellpy Core Output
*To be summarized in a separate file*

**SPEED-17:** "Define the object that comes out of cellpy core"

### Updated Harmonized_Raw

Additional calculations when necessary:
- Calculate step type and step mode (for steptable and then update)
- Decide on how to handle cycler-specific measurement points that don't follow the time series (e.g. internal resistances at start/end of a cycle)
  - option 1: forward fill values (ethical concerns!!!)
    - could add prefix to indicate what was done in the processing


### StepTable
- Use unique step numbers
- one row for each individual sequential step
- do things to speed up calculations (e.g. for pulsing)

#### Headers
- Min, Max, delta, time-average, capacity-average, arithmetic-mean, stdv, medians, first, last
- First, last, delta
  - Cycle number
  - Step number, substep number and type and mode
  - Original datapoint number and index
- Mask (Boolean)



### Core CycleTable

#### Headers
- Min, Max, delta, time-average, capacity-average, arithmetic-mean
  - for every raw value
  - also for auxillaries
- capacity, energy and time per mode
- charge and discharge difference
- Coulombic/Energy/Power efficiency
- Voltage efficiency: energy efficiency/CE
- Cumulated values
- Splits per mode:
  - CV share: amount of capacity in CV/full capacity in cycle etc
- Internal resistance estimations based on potential drops
  - resistances at different time scales
- Mask (Boolean)



## Other questions
- Header structure & versioning on headers and filestructure (separate Task: **SPEED-30**)

- Units and unit conversion
  - locking units might limit resolution
  
- How to deal with different types of experiments
  - pulsing protocols, such as GITT, ICI
  - EIS
  - 3-electrode data


## Add on's

### Pre-processing Modules
- Convert time series data from any tester to common cellpy-core-input format


### Post-processing/Analysis Modules


### Meta-data Module(s)



## Current code structure:
  - cell_core: the cellpy core class
  - selectors: module containing functions;
    - input: data object;
    - not allowed to modify the data object
  - summarizers: (should also not modify the data object)
  - units (optional)