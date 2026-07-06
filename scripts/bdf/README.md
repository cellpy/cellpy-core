# cellpy-bdf — experimental BDF read/export prototype

Prototype adapter between the cellpy-core **harmonized-raw** schema
(`cellpycore.config.RawCols`) and the Battery Data Alliance
**[Battery Data Format (BDF)](https://battery-data-alliance.github.io/battery-data-format-ontology/battery-data-format.html)**
column notations.

**Status: experimental, not part of the cellpy-core public API.** Nothing in
`cellpycore` imports this package; it is excluded from the sdist/wheel and
from root CI. The placement decision (and when to move it out, e.g. to a
cellpy-io repo) is recorded in
[`.issueflows/04-designs-and-guides/bdf-io-placement.md`](../../.issueflows/04-designs-and-guides/bdf-io-placement.md)
(issue #100).

## Usage

This folder is a standalone `uv` project (own `pyproject.toml`, depends on the
in-repo `cellpycore` via a path source). Run everything from the repo root
with `--directory` (which also changes the working directory, so pytest picks
up this project's config instead of the repo root's):

```bash
# run the prototype's tests
uv run --directory scripts/bdf pytest

# use it in a script
uv run --directory scripts/bdf python - <<'EOF'
from cellpycore.testing.mock_data import create_raw_data
from cellpy_bdf import export_bdf, read_bdf

frame = create_raw_data()                      # harmonized-raw polars frame
export_bdf(frame, "/tmp/example_bdf.parquet")  # BDF-named parquet (or .csv)
back = read_bdf("/tmp/example_bdf.parquet")    # back to harmonized-raw names
EOF
```

## Conventions

- **Cycle-reset capacities:** cellpy-core capacities/energies are cumulative
  per cycle, per direction — mapped to the BDF `cycle_*_ah` / `cycle_*_wh`
  terms, not the never-resetting test-level family.
- **Timestamps:** `epoch_time_utc` (int64 ns, UTC) <-> `unix_time_second`
  (float s), converted on export/read.
- **Units:** the engine is unit-agnostic; pass by-value `conversion_factors`
  (keyed by BDF notation) when the raw data is not already in BDF units.
  Factors are multiplied in on export and divided out on read.
- **Preservation:** cycles are never renumbered and `step_type` values pass
  through as reported, per the BDF spec.
