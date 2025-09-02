# Definition of what operations Cellpy Core will perform

JP started moving stuff into a readers/slim folder have a look at cell_core.py:

  - cell_core: the cellpy core class
  - selectors: module containing functions;
    - input: data object;
    - not allowed to modify the data object
  - summarizers: (should also not modify the data object)
  - units (optional)



## Cellpy Core Functionality
- receive data object
    - to be defined - separate task?
- augment data object with
  - Unified time series    - 
  - Steptable
    - to be defined - separate task?
    - substeps?
  - Core summary
    - to be defined - separate task?
- Metadata
  - keep metadata out of core, but keep it in mind when setting it up
  - Morrow will not use metadata within cellpy
  - Only keep metadata that is strictly necessary for use within core
    - cell-specific
    - test information
      - tester, channel etc
    - raw data
      - where does the file come from?
      - when loaded, when changed etc.
      - Units, resolution


## Cellpy Core Input (Harmonized_Raw)
flexible structure that allows for more columns

- Time series data (format to be decided)
  - **Datetime object** (in *high enough* resolution)
    - UTC
    - resolution from cycler
  - **Data point number - original**
    - kept from data collection
    - important for sorting and debugging
      - handling of daylight saving time
      - sort out mismatch between datapoint vs timestamp vs order in the file
  - **Data point number - updated**
      - Index (corrected sequential datapoints)
      - Has to be added as separate column

  - Voltage (V)
  - Current (A)
  - Cycle Number
  - Step Number (original)
  - Unique Step Number (sequential)
  - Substep Number
  - Step Type (optional values)
    - ch, dch, rest
  - Step Mode (optional values)
    - CC, CV, CP, None
  - Charge capacity
  - Discharge capacity
  - Source
    - UUID
    - will not be used, only kept for tracability
  - Default: calculate if empty; keep if filled (can be overridden by argument):
    - Charge energy
    - Discharge energy
    - Charge power
    - Discharge power
  - Auxilary
    - e.g. Temperature
      - Cell temperature(s)
      - Chamber temperature
      - (could be more)

Naming scheme:
- aux_temperature_[arbitrary name]
- aux_voltage_[]
- aux_pressure_[]
- aux_resistance_[]


To be discussed
- EIS, cyclic voltametry
- 3-electrode setup

- needed:
  - data resolution (for definition of step types)
  - units (if we chose units)



## Cellpy Core Output

https://cellpy.readthedocs.io/en/latest/fundamentals/data_structure.html

### Raw data: Harmonized_Raw

see above.

### Core Summary

Define headers


### Steptable
- Use unique step numbers
- do things to speed up calculations for pulsing


Define headers


## Other questions
- decide on header structure
- versioning on headers and filestructure

- Units and unit conversion
  - locking units might limit resolution
  
- How to deal with different types of experiments
  - pulsing protocols, such as GITT, ICI
  - EIS?


## Add on's

### Pre-processing Modules
Convert time series data from any tester to common cellpy-core-input format


### Post-processing/Analysis modules

