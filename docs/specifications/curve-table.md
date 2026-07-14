# Cellpy Core Curve Tables (DRAFT)

Date: 2026-07-15 (issue #118, Stage 1.17; home decided in jepegit/cellpy#438
decision 2)

## Purpose

Spec'd output schemas for the curve-extraction layer (`cellpycore.curves`) —
the port of legacy cellpy's most-used data API (`get_cap` / `get_ccap` /
`get_dcap` / `get_ocv`), which previously returned frames with unspec'd,
hard-coded column names. Two tables are defined: the **capacity-curve table**
(`config.CurveCols`) and the **OCV-relaxation table** (`config.OcvCurveCols`).

Units note: the engine is unit-agnostic (units-by-value seam). `capacity` is
`raw cumulative capacity × converter`, where the caller supplies the float
`converter` (e.g. from `cellpycore.units.get_converter_to_specific`);
`potential` and `step_time` keep the raw-frame units (spec'd in
`harmonized-raw.md`: volt, second).

## Capacity-curve table (`CurveCols`)

Output of `curves.get_cap_curve` (all columns) and of
`curves.get_charge_curve` / `curves.get_discharge_curve` (the
`potential` / `capacity` pair only).

| Column name | Data type | Unit | Sample data | Description |
| --- | --- | --- | --- | --- |
| cycle_num | int | - | 12 | Cycle number (present when `label_cycle_number=True`; float when NaN separator rows are inserted) |
| potential | float | volt (V) | 3.4561 | Potential; NaN on separator rows (`insert_nan=True`) |
| capacity | float | converter-defined | 123.45 | Cumulative branch capacity × converter, after the method's shift arithmetic (`back-and-forth` / `forth` / `forth-and-forth`) |
| direction | float | - | -1.0 | −1 for the cycle's first branch, +1 for the last, NaN on separator rows (present when `categorical_column=True`) |

Column order: `cycle_num` (when present), `potential`, `capacity`,
`direction` (when present); `capacity_then_voltage=True` swaps
`capacity` before `potential`.

The cycle's *first* branch is the discharge branch when the test mode is
`TestMode.INVERTED` (legacy `cycle_mode="anode"`), else the charge branch.

## OCV-relaxation table (`OcvCurveCols`)

Output of `curves.get_ocv_curve`.

| Column name | Data type | Unit | Sample data | Description |
| --- | --- | --- | --- | --- |
| cycle_num | int | - | 12 | Cycle number |
| step_num | int | - | 13 | Step number |
| step_time | float | second (s) | 15.1231 | Time within the relaxation step (interpolation x-axis when `interpolated=True`) |
| potential | float | volt (V) | 3.4561 | Relaxation potential |

## Parity and intentional differences vs legacy cellpy

The parity oracle is the Stage-0 curve-snapshot suite (jepegit/cellpy#433),
vendored under `tests/data/curve_goldens/` and asserted by
`tests/test_curves.py` (value parity at rtol 1e-9 across the option matrix).
Documented intentional differences:

1. **Column names are the spec'd native ones** (`potential`, `cycle_num`, …);
   legacy names (`voltage`, `cycle`, `charge_capacity`, …) are applied by the
   cellpy wrapper, not by core.
2. **Cycle iteration order is deterministic** (sorted); legacy iterated an
   unordered `set`.
3. The legacy `usteps` channel and `dynamic` (cellpy-file streaming) are not
   ported (no `ustep` column in the native step table; streaming is app-side).
4. Interpolation is numpy-based linear interpolation — mathematically
   identical to legacy scipy `interp1d(kind="linear", bounds_error=False)` on
   the strictly monotonic segments this module produces; core gains no scipy
   dependency.
