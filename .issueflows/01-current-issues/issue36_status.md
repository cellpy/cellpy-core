# Issue 36 — Status

Interactive `/iflow-fix` session: re-evaluate the native header schema and
promote selected legacy-only columns into cellpy-core where they represent real
signals (not legacy cruft).

- [ ] Done

## Iterative fixes log

- 2026-06-24 — Added per-cycle cell-temperature summary headers to `CycleCols`
  (`temperature_cell_mean` / `_max` / `_min` / `_last`), closing the asymmetry
  where native raw ingests `aux_temperature_cell` but the cycle summary had no
  temperature column. `_mean` / `_last` map to legacy `temperature_mean` /
  `temperature_last` (moved out of `LEGACY_ONLY_CYCLE` into `CYCLE_PAIRS`);
  `_max` / `_min` added to `NATIVE_ONLY_CYCLE`. Header-declaration only — engine
  population in `make_summary` deferred. Updated `config.py`,
  `header_mapping.py`, `docs/data_format_specifications/cycle_table.md`,
  `tests/test_config_columns.py`. Full suite green (50 passed).
