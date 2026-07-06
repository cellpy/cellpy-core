# Thoughts and possible issues

Tracked on GitHub:

| Topic | Issue |
|---|---|
| BDF format / scripts folder | [#100](https://github.com/cellpy/cellpy-core/issues/100) |
| Ordered headers | [#96](https://github.com/cellpy/cellpy-core/issues/96) |
| RawCols dtype map | [#97](https://github.com/cellpy/cellpy-core/issues/97) |
| Syntax warning (`mock_core.py`) | [#95](https://github.com/cellpy/cellpy-core/issues/95) |
| Split step C-rate from `make_step_table` | [#98](https://github.com/cellpy/cellpy-core/issues/98) |
| Unclear standalone-use docs | [#99](https://github.com/cellpy/cellpy-core/issues/99) |

## Thoughts and ideas

### BDF format — [#100](https://github.com/cellpy/cellpy-core/issues/100)

Resolved by issue #100: interim prototype lives under `scripts/bdf/`; decision and
revisit criteria recorded in `.issueflows/04-designs-and-guides/bdf-io-placement.md`.


### Ordered headers — [#96](https://github.com/cellpy/cellpy-core/issues/96)

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

### Create a dtype map — [#97](https://github.com/cellpy/cellpy-core/issues/97)

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

### Syntax warning — [#95](https://github.com/cellpy/cellpy-core/issues/95)

When importing `cellpycore` using jupyterlab with python 3.14 we got this message:

```
C:\scripting\cellpy-core\src\cellpycore\legacy\mock_core.py:66: SyntaxWarning: 'return' in a 'finally' block
  return df

```

### Add scaled step summary columns as separate step — [#98](https://github.com/cellpy/cellpy-core/issues/98)

Resolved by issue #98: `make_step_table` builds the base table only; the per-step
C-rate is appended by the separate opt-in `summarizers.add_step_c_rate` (the
`add_c_rate` flag survives only on the `OldCellpyCellCore` bridge). See
`.issueflows/04-designs-and-guides/step-c-rate-split.md`.

### Unclear example — [#99](https://github.com/cellpy/cellpy-core/issues/99)

The example in the docs is a bit unclear.

`nom_cap` vs `nom_cap_abs`

`current_conversion_factor` vs `specific_converters`

It might be because we have not been consistent in naming of parameters / arguments. 

```python

# Example in docs:

from cellpycore.cell_core import CellpyCellCore, Data

core = CellpyCellCore()
core.data = Data.from_raw_frame(my_polars_frame)  # validates against config.RawCols
core.cycle_mode = "anode"                          # half-cells only; unset = normal

data = core.make_core_step_table(
    core.data,
    nom_cap=my_nom_cap_abs,              # absolute (e.g. Ah), for the per-step C-rate
    raw_limits=my_instrument_limits,     # optional; DEFAULT_RAW_LIMITS otherwise
)
data = core.make_core_summary(
    data,
    current_conversion_factor=1.0,       # raw-current -> output-current, by value
)
# optional: specific / normalized columns
data = core.add_scaled_summary_columns(
    data,
    nom_cap_abs=my_nom_cap_abs,
    normalization_cycles=None,
    specific_converters={"gravimetric": f_g, "areal": f_a, "absolute": f_abs},
)

steps, summary = data.steps, data.summary  # polars frames (StepCols / CycleCols)
```
