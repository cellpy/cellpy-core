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


## Cellpy Core Input (Harmonized_Raw)
Summarized in [harmonized_raw_definition.md](./harmonized_raw_definition.md)

## Cellpy Core Output
Summarized in [core_output_definition.md](./core_output_definition.md)



## Other questions
- Header structure & versioning on headers and filestructure (separate Task: **SPEED-30**)

- Units and unit conversion
  - locking units might limit resolution
  
- How to deal with different types of experiments
  - pulsing protocols, such as GITT, ICI
  - EIS
  - 3-electrode data

- How do we handle sequential tests?
  - re-proccess everything?
  - smart ways of stitching processed data together?
  - then we might have e.g. a cycle number and a total cycle number
    - decide how to deal with cummulative values

## Add on's

### Pre-processing Modules
- Convert time series data from any tester to common cellpy-core-input format

### Post-processing/Analysis Modules


### Meta-data Module(s)

Metadata will be kept out of the core. Important to keep metadata in mind when setting up Cellpy Core, so that metadata can easily follow and be aligned with the data.

- Only keep metadata that is strictly necessary for use within core (to be defined as part of Harmonized_Raw)
    - cell-specifics
    - test information
      - tester, channel etc
    - raw data
      - where does the file come from?
      - when loaded, when changed etc.
      - Units, resolution

## Current code structure:
  - cell_core: the cellpy core class
  - selectors: module containing functions;
    - input: data object;
    - not allowed to modify the data object
  - summarizers: (should also not modify the data object)
  - units (optional)