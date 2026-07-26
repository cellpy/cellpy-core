# Issue #138: Add a built-in utility for calculating Equivalent Full Cycles (EFC) from time-series data.

Author: jepegit
URL: https://github.com/cellpy/cellpy-core/issues/138

Cellpy currently provides cycle-based summaries and performance metrics for cycling experiments. However, many battery datasets particularly operational, field, and BMS datasets do not contain well-defined charge/discharge cycles. Instead, they consist of continuous time-series measurements of voltage, current, temperature, and time.

For these datasets, researchers and engineers often use Equivalent Full Cycles (EFC) as a throughput-based ageing metric. Currently, users must calculate EFC outside of cellpy and maintain custom implementations, leading to duplicated effort and inconsistent definitions across projects.

As battery research increasingly incorporates operational and real-world datasets, the lack of a built-in EFC calculation makes it more difficult to compare ageing across datasets and integrate operational data into existing cellpy workflows.

## Proposed Solution

Add a built-in utility for calculating **Equivalent Full Cycles (EFC)** from time-series data.

Example usage:

```python
cell.calculate_efc(nominal_capacity=300.0)
````

or

```python
cell.make_summary(add_efc=True)
```

The implementation could:

* Calculate cumulative charge throughput from current and time:

  $$
  Q_{throughput} = \sum |I| \Delta t
  $$

* Compute EFC as:

  $$
  EFC = \frac{Q_{throughput}}{2Q_{nom}}
  $$

  where $$Q_{nom}$$ is the nominal capacity.

* Optionally add:
  * Instantaneous cumulative EFC to the raw dataframe.
  * EFC columns to the summary dataframe.
  * Energy-throughput-based equivalents (optional future extension).
  * Support for SoC-based EFC calculations when SoC data is available.

Suggested outputs:

* `cumulative_ah_throughput`
* `cumulative_energy_throughput`
* `equivalent_full_cycles`

This would provide a standardized and reproducible EFC implementation directly within the cellpy ecosystem.

***

**Describe alternatives you've considered**

Current alternatives include:

* Implementing custom EFC calculations in downstream analysis scripts.
* Adding project-specific preprocessing steps prior to importing data into cellpy.

While these approaches work, they lead to code duplication and make it harder to compare results across projects and users. A native cellpy implementation would provide a common reference method and improve reproducibility.

***

**Additional context**

This feature would be particularly useful for:

* Operational battery datasets.
* BMS and field-monitoring data.
* Fleet and stationary storage applications.
* Machine learning pipelines where degradation progress is tracked using throughput-based metrics.
* Continuous time-series datasets that do not contain explicit cycle boundaries.

As cellpy expands beyond traditional cycling experiments and is increasingly used for large-scale battery data analysis, a standardized EFC utility would help bridge the gap between laboratory cycling data and real-world operational datasets.

```
```

