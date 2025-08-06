# Definition of what operations Cellpy Core will perform

JP started moving stuff into a readers/slim folder have a look at cell_core.py

cell_core: the cellpy core class
selectors: module containing functions; input: data object; not allowed to modify the data object
summarizers: (should also not modify the data object)
units (optional)

## Input
to be defined

- time series data (format to be decided)
  - datetime/timestamp (in high enough resolution)
  - data point number (redundant if datetime resolution is good enough?); can be optional and be created if it doesn't exist.
  - voltage
  - current
  - 
- needed:
  - data resolution (for definition of step types)
  - units (if we chose units)

## Cellpycore should
- receive data object
- augment data object with
  - steptable
    - to be defined - separate task?
  - core summary
    - to be defined - separate task?



## Open questions
- units and unit conversion
  - locking units might limit resolution
