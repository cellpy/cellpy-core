# cellpy-core

The core engine of [cellpy](https://github.com/jepegit/cellpy): fast,
thread-safe processing of battery-cycling raw data. Given a raw data frame
(polars, native schema — or pandas via the legacy bridge), it finds all steps
and cycles and builds per-step and per-cycle summary tables. It is designed to
be small, schema-injected, and easy for cellpy developers to build on and
extend; instrument loaders, file IO, and unit handling stay out of the core.

```python
import polars as pl
from cellpycore import Data, make_step_table, make_summary

data = Data.from_raw_frame(pl.read_parquet("my_native_raw.parquet"))
make_step_table(data, nom_cap=1.0)
make_summary(data)
print(data.steps, data.summary)
```

## Installing

Available on PyPI as [`cellpycore`](https://pypi.org/project/cellpycore/):

```bash
pip install cellpycore
```

Source: <https://github.com/cellpy/cellpy-core>

## Documentation

Full documentation (built with [Zensical](https://zensical.org), hosted on
Read the Docs): <https://cellpy-core.readthedocs.io/>

Key pages:

- [Using cellpy-core standalone (slim-consumer guide)](https://github.com/cellpy/cellpy-core/blob/main/docs/user-guide/standalone-use.md) —
  get step tables and per-cycle summaries from a native-schema polars frame
  without full cellpy.
- [Harmonized raw format specification](https://github.com/cellpy/cellpy-core/blob/main/docs/specifications/harmonized-raw.md)
- [The Data object](https://github.com/cellpy/cellpy-core/blob/main/docs/user-guide/data-object.md)
- [Example notebooks](https://github.com/cellpy/cellpy-core/tree/main/docs/examples)

Build the docs locally with `uv run --group docs zensical serve` (config in
`zensical.toml`; notebook-regeneration instructions in `docs/examples/index.md`).

## Developing

This project uses `uv` as the package manager and build tool. `uv` is a fast Python package installer and resolver, written in Rust.

### Prerequisites

1. Install `uv`:

```bash
pip install uv
```

### Development Workflow

1. Install all dependencies (creates `.venv` automatically):

```bash
uv sync
```

2. Adding new dependencies:

```bash
# Add a new package
uv add <package-name>

# Add a new development package
uv add --dev <package-name>
```

3. Running tests:

```bash
uv run pytest
```

### Common Commands

- Reinstall dependencies from the lock file: `uv sync`
- Remove a package: `uv remove <package-name>`
- Upgrade all packages within constraints: `uv sync --upgrade`
- Show the dependency tree: `uv tree`

For more information about `uv`, visit the [official documentation](https://github.com/astral-sh/uv).
