# Test data fixtures

Small, real cycling-data fixtures used by the test suite. They let the compute
engine be tested on genuine instrument output **without** depending on instrument
loaders (Arbin ODBC, Maccor/Neware parsers, …) — cellpy-core is the *core* engine
and stays loader-free.

## Files

| File | Source (cellpy repo) | Shape | Role |
|------|----------------------|-------|------|
| `arbin_cc_raw.parquet` | `testdata/data/20160805_test001_45_cc_01.res` | 10 261 rows, 18 cols, 18 cycles | Canonical golden oracle |
| `arbin_cc_steps_expected.parquet` | *(derived)* | 103 steps | Frozen snapshot of the current engine's step table |
| `arbin_cc_summary_expected.parquet` | *(derived)* | 18 cycles, 27 cols | Frozen snapshot of the current per-cycle summary |
| `arbin_cc_steptypes_cellpy.csv` | `testdata/data/steps.csv` | 103 steps, 4 cols | **Independent** cellpy step-type golden (cross-repo parity, Phase 4) |
| `arbin_small_raw.parquet` | `testdata/data/20200624_test001_cc_01.h5` | 47 rows, 1 cycle, 3 steps | Tiny fast fixture (no ODBC) |
| `arbin_cc_harmonized_raw.parquet` | *(derived from `arbin_cc_raw.parquet`)* | 10 261 rows, 28 cols, 18 cycles | Same data in the **harmonized** schema (`RawCols` naming) |

The original raw frames use the legacy `HeadersNormal` column naming
(`data_point`, `voltage`, `charge_capacity`, …) that the engine currently
consumes. `arbin_cc_harmonized_raw.parquet` is the one exception: it is the same
Arbin data renamed into the **harmonized raw** schema
(`cellpycore.config.RawCols`: `datapoint_num`, `potential`,
`cumulative_charge_capacity`, …) — see
[`docs/data_format_specifications/harmonized_raw.md`](../../docs/data_format_specifications/harmonized_raw.md).

## Golden numbers

Mirrored from cellpy's own suite (`tests/test_cell_readers.py`) and verified to
be reproduced by cellpy-core's engine on `arbin_cc_raw.parquet`:

- step-table rows: **103**
- summary cycles: **18**
- cycle-1 last `data_point`: **1457**

`arbin_cc_steptypes_cellpy.csv` is a stronger, **per-step** cross-library check: it is
cellpy's own committed `steps.csv` golden (cycle/step/type/info), which predates the
cellpy→cellpy-core engine integration, so reproducing it byte-for-byte proves genuine
cross-repo parity rather than a self-snapshot.

## Provenance & license

Source files come from the [cellpy](https://github.com/jepegit/cellpy) repository
(battery test data originating from IFE, Norway). cellpy is MIT-licensed; these
small derived snapshots are vendored here under the same terms for testing only.

## Regenerating

Fixtures are produced by `dev/regenerate_test_data.py` in two stages (different
environments, because the engine working copy and the instrument loaders live in
different venvs):

```bash
# Stage A — raw export (needs cellpy + Arbin ODBC for the .res); run in cellpy's env
cd ../cellpy && uv run python ../cellpy-core/dev/regenerate_test_data.py

# Stage B — engine snapshot (needs the cellpy-core working copy); run in cellpy-core's env
cd ../cellpy-core && uv run python dev/regenerate_test_data.py
```

Set `CELLPY_REPO` if the cellpy checkout is not the sibling `../cellpy`.

Regenerate the `*_steps_expected.parquet` / `*_summary_expected.parquet` snapshots
**intentionally** (and review the diff) only when a step-table or summary change is
expected.

`arbin_cc_harmonized_raw.parquet` is produced separately (pure-polars, no cellpy
needed) by `dev/make_harmonized_raw.py`, which renames `arbin_cc_raw.parquet` into
the `RawCols` schema. Re-run it after any `RawCols` change so the fixture tracks
the schema:

```bash
uv run python dev/make_harmonized_raw.py
```
