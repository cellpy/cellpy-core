# Issue #138 — Plan: Equivalent Full Cycles (EFC) utility

Confirmed approach (user-approved 2026-07-18):

- **Both surfaces**: raw-level current integration + summary-level per-cycle columns.
- **Summary basis**: existing `test_cumulated_charge_capacity + test_cumulated_discharge_capacity` (unit-consistent with nom_cap, no conversion factor).
- **Skipped**: energy throughput, SoC-based EFC (issue marks optional/future); `make_summary(add_efc=True)` wiring (standalone functions match `equivalent_cycles_to_summary` precedent); legacy-bridge columns (native-only feature).

## Changes

1. `summarizers.py`: two free functions next to `equivalent_cycles_to_summary`:
   - `throughput_to_raw(data, schema=None, nom_cap_abs=1.0, conversion_factor=1.0, *, nom_cap=None)` — adds `test_cumulated_capacity_throughput` (= cum_sum(|current|·Δt·factor), windowed over test_id when present, negative Δt clipped to 0) and `equivalent_full_cycles` (= throughput / (2·nom_cap_abs)) to `data.raw`. `conversion_factor` converts current·time units to the capacity unit (e.g. A·s→mAh = 1000/3600), caller-supplied per codebase convention.
   - `efc_to_summary(data, schema=None, nom_cap_abs=1.0, normalization_cycles=None, step_txt=None, *, nom_cap=None)` — same two columns on the summary, throughput = cumulated charge + discharge capacity; supports `normalization_cycles` like its sibling.
2. `config.py` `CycleCols`: the two new column-name fields (raw function reuses the same names via `schema.cycle`).
3. `docs/specifications/cycle-table.md`: two new spec rows (conformance-locked).
4. `legacy/mapping.py`: names added to `NATIVE_ONLY_CYCLE` (no legacy counterpart).
5. `tests/test_config_columns.py`: names added to `CYCLE_EXPECTED`.
6. `tests/test_efc.py` (new): raw integration vs hand-computed Σ|I|Δt, rest-rows-add-nothing, monotonicity, conversion factor, pandas round-trip, summary identity vs cumulated capacities.
