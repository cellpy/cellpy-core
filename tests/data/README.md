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
| `arbin_small_raw.parquet` | `testdata/data/20200624_test001_cc_01.h5` | 47 rows, 1 cycle, 3 steps | Tiny fast fixture (no ODBC) |

All raw frames use the legacy `HeadersNormal` column naming (`data_point`,
`voltage`, `charge_capacity`, …) that the engine currently consumes.

## Golden numbers

Mirrored from cellpy's own suite (`tests/test_cell_readers.py`) and verified to
be reproduced by cellpy-core's engine on `arbin_cc_raw.parquet`:

- step-table rows: **103**
- summary cycles: **18**
- cycle-1 last `data_point`: **1457**

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

Regenerate the `*_steps_expected.parquet` snapshot **intentionally** (and review
the diff) only when a step-table change is expected.
