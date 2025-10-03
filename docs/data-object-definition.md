# Data Object Definiton

The Data Object that goes into Cellpy Core must at least contain:

- test_time with unit of millisecond
- voltage with unit of volt
- current with unit of ampere

The Data Object that comes out of Cellpy Core should ahere to the best practices set by the Battery Data Alliance: https://github.com/battery-data-alliance

The Data Object must contain:
- test_time with unit of millisecond
- voltage with unit of volt
- current with unit of ampere
- cycle number with unit of dimensionless

Unless the measured quantity can be represented as an integer, float64 should be used in order to ensure sufficient resolution.

The Data Object could contain:
- unix_time with unit of millisecond, which for example supports sorting of testdata coming from different files
- what type of experiment it is, e.g. Life-time, rate test, GITT, EIS, etc.



## Interface