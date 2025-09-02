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



## Cellpy Core Input

- Time series data (format to be decided)
  - **Datetime/timestamp** (in *high enough* resolution)
    - resolution might vary throughout a measurement
    - different cyclers use different time formats - pre-processing?
  - **Data point number**
    - important for sorting and debugging
      - handling of daylight saving time
      - sort out mismatch between datapoint vs timestamp vs order in the file
  - Voltage (V)
  - Current (A)

    
- needed:
  - data resolution (for definition of step types)
  - units (if we chose units)



## Cellpy Core Output

https://cellpy.readthedocs.io/en/latest/fundamentals/data_structure.html

### Raw data

Define headers

### Core Summary

Define headers


### Steptable

Define headers


## Other questions
- Units and unit conversion
  - locking units might limit resolution
  
- How to deal with different types of experiments
  - pulsing protocols, such as GITT, ICI
  - EIS?


## Add on's

### Pre-processing Modules
Convert time series data from any tester to common cellpy-core-input format


### Post-processing/Analysis modules

