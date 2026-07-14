# Plan — issue #118 (Stage 1.17)

1. **Schemas:** `config.CurveCols` (cycle_num, potential, capacity, direction)
   and `config.OcvCurveCols` (cycle_num, step_num, step_time, potential), spec'd
   in `docs/specifications/curve-table.md`, pinned by the
   `test_config_columns.py` pattern.
2. **`cellpycore/curves.py`:**
   - `select_step_numbers` — port of legacy `get_step_numbers` (dict flavour):
     helper types (`ocv`, `charge_discharge`), `all_combined_types`
     (legacy `allctypes`), taper trimming, steps-to-skip, `[0]` placeholder.
   - `get_charge_curve` / `get_discharge_curve` — port of `_get_cap`
     (per-step raw selection sorted by step number, capacity × converter,
     `NoDataFound` on empty).
   - `get_cap_curve` — faithful port of `get_cap`: back-and-forth / forth /
     forth-and-forth shift arithmetic, insert_nan separators, categorical
     direction column, cycle labels, inter_cycle_shift, interpolate_along_cap
     reversals, capacity_then_voltage reorder; `TestMode.INVERTED` replaces
     `cycle_mode == "anode"`.
   - `get_ocv_curve` — port of `get_ocv` incl. the isin-on-both-columns
     selection semantics and per-(cycle, step) interpolation.
   - Interpolation ported to numpy (linear, NaN outside range, strictly
     monotonic segment splitting, constant-x passthrough, max_segments
     bailout) — no scipy dependency for core.
3. **Seam:** units by value (`converter: float`); frames in/out polars.
4. **Parity oracle:** the 7 cellpy #433 curve snapshots vendored under
   `tests/data/curve_goldens/` (regenerate cellpy-side, re-vendor); native
   pipeline = harmonized fixture → `Data.from_raw_frame` → `make_step_table`
   → curves; comparison maps native → legacy names, value parity at rtol 1e-9.
5. **Intentional differences documented** in the module docstring + spec doc:
   native names, deterministic cycle order, no usteps/dynamic, numpy interp.
