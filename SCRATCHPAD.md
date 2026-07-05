# Thoughts and possible issues

## Thoughts and ideas

### BDF format

Read and export in BDF format; should it be a part of cellpy-core, or should it be a part of another repo (cellpy-io)?

Idea: create a folder called scripts in cellpy-core repo and put it there for now. Then we can decide later where to finally put it.


### Ordered headers

Consider adding explicit ordering to the headers, e.g.

```python

class RawCols(Cols):
    __column_order__ = (
        "datapoint_num", "source_datapoint_num", "mask", ...
    )

    @classmethod
    def ordered_names(cls) -> list[str]:
        cols = cls()
        return [getattr(cols, name) for name in cls.__column_order__]

```

### Create a dtype map

Currently we have to map the dtypes "by hand", e.g. by creating a function like this:

```python


def rawcols_dtype_map() -> dict[str, pl.DataType]:
    c = RawCols()
    return {
        c.datapoint_num: pl.Int64,
        c.source_datapoint_num: pl.Int64,
        c.mask: pl.Boolean,
        c.epoch_time_utc: pl.Int64,
        c.test_time: pl.Float64,
        c.step_time: pl.Float64,
        c.source_type: pl.Utf8,
        c.source_uuid: pl.Utf8,
        c.test_id: pl.Int64,
        c.step_num: pl.Int64,
        c.source_step_num: pl.Int64,
        c.step_type: pl.Utf8,
        c.step_type_detail: pl.Utf8,
        c.step_mode: pl.Utf8,
        c.cycle_num: pl.Int64,
        c.cycle_type: pl.Utf8,
        c.potential: pl.Float64,
        c.current: pl.Float64,
        c.cumulative_charge_capacity: pl.Float64,
        c.cumulative_discharge_capacity: pl.Float64,
        c.cumulative_charge_energy: pl.Float64,
        c.cumulative_discharge_energy: pl.Float64,
        c.step_charge_power: pl.Float64,
        c.step_discharge_power: pl.Float64,
        c.internal_resistance: pl.Float64,
        c.ref_potential: pl.Float64,
        c.aux_temperature_cell: pl.Float64,
        c.aux_temperature_chamber: pl.Float64,
        c.aux_pressure_cell: pl.Float64,
    }

```

Important to have a single point of truth. Consider adding to config.py. And also add helper functions (ala the validate_raw_frame function). Not sure how to structure it so that it will be easy maintainable. Hmmm....

## Do we have an Issue?

### Syntax warning

When importing `cellpycore` using jupyterlab with python 3.14 we got this message:

```
C:\scripting\cellpy-core\src\cellpycore\legacy\mock_core.py:66: SyntaxWarning: 'return' in a 'finally' block
  return df

```

### Add scaled step summary columns as separate step

Should use the same pattern as we do for cycle summary. It should not be an option within the  core make step table, but appended afterwards if user wants to

Check first what implications it has on downstream functions (like making the cycle summary). If not too high-cost - split the make_step_table into two functions, i.e. 
move this out to separate function:

```python
    # Per-step C-rate (legacy ``rate_avr`` = abs(current_avr / nom_cap)); the
    # nominal capacity is supplied by the caller (by value).
    if add_c_rate:
        _nom_cap = nom_cap if nom_cap is not None else 1.0
        steps = steps.with_columns(
            (pl.col("current_mean") / _nom_cap)
            .round(DIGITS_C_RATE)
            .abs()
            .alias(shdr.c_rate)
        )
```

