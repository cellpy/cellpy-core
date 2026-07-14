# Development Guide

This document outlines the development practices, standards, and workflows for the
cellpy-core library.

## Table of Contents

1. [cellpy-core in the cellpy 2 architecture](#cellpy-core-in-the-cellpy-2-architecture)
2. [Code Documentation](#code-documentation)
3. [Branching and Merging Strategy](#branching-and-merging-strategy)
4. [Code Structure and Principles](#code-structure-and-principles)
5. [Development Workflow](#development-workflow)
6. [Testing Guidelines](#testing-guidelines)
7. [Code Quality Standards](#code-quality-standards)
8. [Related documentation](#related-documentation)

## cellpy-core in the cellpy 2 architecture

Cellpy 2 is a **layered, two-package system**. `cellpycore` is the small, pure,
polars-based **compute engine** — it owns shapes and tools (schemas, step/summary
engines, metadata models, unit converters, the legacy mapping). The `cellpy`
application package owns content and policy (configuration, instrument loaders,
metadata population, persistence, plotting, batch).

Everything crossing the seam is **plain values** — never config objects, pint
quantities, or file handles. Translation between the v1 dialect and the native
schema happens once at I/O boundaries in cellpy, not per engine call.

```text
┌─────────────────────────────────────────────────────────────┐
│ APP LAYER (cellpy) — loaders, config, persistence, plotting │
├────────────────── seam: plain values only ──────────────────┤
│ ENGINE (cellpycore) — polars frames, native schema          │
│   Data · make_step_table · make_summary · metadata tooling  │
│   OldCellpyCellCore + legacy/ — bridge for v1.x maintenance │
└─────────────────────────────────────────────────────────────┘
```

**cellpy-core non-goals:** instrument loaders, file I/O (beyond test fixtures),
runtime configuration, plotting, and populated cell metadata on the hot path.
The engine degrades gracefully when metadata is absent.

Authoritative architecture plans live in the sibling
[`architecture-plan`](https://github.com/cellpy/architecture-plan) repository
(check out next to this repo in a
[cellpy-workspace](https://github.com/cellpy/architecture-plan#sibling-repositories)
layout). Start with
[`cellpy2-architecture-plan.md`](https://github.com/cellpy/architecture-plan/blob/main/cellpy2-architecture-plan.md).
Cross-repo integration rules for contributors are in
[cellpy-core-migration.md](https://github.com/cellpy/cellpy-core/blob/main/.issueflows/04-designs-and-guides/cellpy-core-migration.md)
(also under `.issueflows/04-designs-and-guides/` in this repo).

## Code Documentation

### Docstring Format

We use the **Google docstring format** for all Python code documentation. This format
provides clear, readable documentation that works well with most documentation
generators.

#### Basic Structure

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """Brief description of the function.

    More detailed description if needed. This can span multiple lines
    and should explain the purpose and behavior of the function.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter. Defaults to 10.

    Returns:
        Description of what the function returns.

    Raises:
        ValueError: Description of when this exception is raised.
        TypeError: Description of when this exception is raised.

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
    pass
```

#### Class Documentation

```python
class ExampleClass:
    """Brief description of the class.

    More detailed description of the class purpose and behavior.
    This can include information about the class design, usage patterns,
    and any important implementation details.

    Attributes:
        attribute1: Description of the first attribute.
        attribute2: Description of the second attribute.

    Example:
        >>> obj = ExampleClass("value1", "value2")
        >>> obj.method()
    """

    def __init__(self, param1: str, param2: str):
        """Initialize the ExampleClass.

        Args:
            param1: Description of the first parameter.
            param2: Description of the second parameter.
        """
        self.attribute1 = param1
        self.attribute2 = param2
```

#### Module Documentation

```python
"""Module-level docstring.

This module provides functionality for [description of module purpose].
It contains classes and functions for [specific functionality].

Example:
    Basic usage example here.
"""
```

### Documentation Standards

- **All public functions, classes, and methods must have docstrings**
- **Use type hints for all function parameters and return values**
- **Include examples in docstrings when the functionality is complex**
- **Document all exceptions that functions may raise**
- **Keep docstrings up-to-date with code changes**

## Branching and Merging Strategy

### Branch Structure

We follow **GitHub Flow** on `main`:

- **`main`**: production-ready code; protected, squash-merged PRs only
- **`<N>-<short-slug>`**: issue work branches (e.g. `121-arch-docs-sync`)

Issue tracking and the `/iflow-*` Agent Skills live under `.issueflows/` — see
[Cursor issue workflow](issue-workflow.md) for the full lifecycle (`/iflow-pick` →
`/iflow-plan` → `/iflow-start` → `/iflow-close`).

### Branch Naming Convention

- **Issues**: `<github-issue-number>-<short-slug>`
  - Example: `70-step-cols-contract`
- Avoid long-lived `feature/*` or `bugfix/*` prefixes unless a release branch
  explicitly needs them.

### Workflow Process

1. **Pick or create an issue** on GitHub (or resume parked work via `/iflow-pick`)
2. **Branch from `main`**: `git switch -c <N>-<short-slug>`
3. **Make changes** with clear commits; keep PRs focused
4. **Push** and open a PR targeting `main`
5. **Request review**; address feedback
6. **Squash-merge** once CI is green

### Commit Message Standards

Use clear, descriptive commit messages. Commit often — imperfect messages beat
monthly perfect ones.

For Conventional Commits:

```
type(scope): brief description

Longer description if needed, explaining what and why.

Fixes #issue-number
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**

```
feat(summarizers): add incremental summary refresh path
fix(config): correct RawCols dtype map for epoch_time_utc
docs(guide): sync development guide with architecture-plan
```

## Code Structure and Principles

Design evolves with the project; treat this section as the current guide and open
an issue when something drifts.

### Project layout

```
src/cellpycore/
├── __init__.py          # Curated public API re-exports
├── cell_core.py         # Data, CellpyCellCore, OldCellpyCellCore
├── config.py            # Schema, RawCols, StepCols, CycleCols
├── summarizers.py       # make_step_table, make_summary, add_step_c_rate
├── extractors.py        # Step/cycle extraction helpers
├── merge.py             # merge_data, update_data
├── timestamps.py        # Timestamp normalization helpers
├── exceptions.py        # CellpyError hierarchy root
├── metadata/            # Test/cell metadata models + io scaffolding
├── units/               # Unit spec + converters (optional [units] extra)
├── legacy/              # Bridge-only: headers, mapping, selectors
└── testing/             # mock_data for tests and examples
```

The **public API** is the names re-exported from `cellpycore.__init__` (`Data`,
`make_step_table`, `make_summary`, schema types, etc.). Subpackages such as
`metadata`, `units`, and `legacy` are importable but not guaranteed stable at the
top level unless listed in `__all__`.

**Native path:** `Data.from_raw_frame` → `make_step_table` → (optional)
`add_step_c_rate` → `make_summary`. Order matters — the summary reads
`data.steps`.

**Legacy bridge:** `OldCellpyCellCore` and `legacy/` serve cellpy v1.x
maintenance (pandas frames, old header names). Slim standalone consumers should
use `CellpyCellCore` / `Data` with the native schema — see
[Standalone use](../user-guide/standalone-use.md).

### Design Principles

#### 1. Schema injection

Column names for raw / cycle / step **group keys** and summary aliases come from
an injected `config.Schema`. Do not hardcode header strings in engine hot paths.
Per-step stat column stems (`<signal>_<stat>`) are a **fixed engine contract**
(not schema-injected); see `StepCols` and issue #70.

#### 2. Polars-native engine

The hot path is polars. Pandas appears only in the legacy bridge and parquet
fixtures. Pass plain unit conversion factors by value — no pint quantities on the
engine seam.

#### 3. Immutable-by-convention frames

Engine helpers should not mutate input polars frames in place. `Data` slots
(`raw`, `steps`, `summary`) are updated by orchestration functions; underlying
frame columns are not silently aliased mid-pipeline.

```python
# Good: return a filtered view / new frame
def filter_by_step_type(steps: pl.DataFrame, step_type: str) -> pl.DataFrame:
    return steps.filter(pl.col("step_type") == step_type)
```

#### 4. Functional core

Prefer pure functions in `extractors` and `summarizers` where practical. Side
effects (file reads, env lookups) belong in cellpy, not here.

#### 5. Metadata graceful degradation

Core ships metadata **scaffolding** (`cellpycore.metadata`) but never requires
populated metadata on `Data`. Attaching real metadata is opt-in upstream (cellpy).

#### 6. Parity by tests

Legacy behavior is guarded by contract tests and golden parquet fixtures in
`tests/data/`, not by manual vigilance. Extend fixtures when porting more surface
from cellpy.

### Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `cell_core.py` | `Data` container; `CellpyCellCore` orchestration; `OldCellpyCellCore` legacy bridge; `validate_raw_frame` / `cast_raw_frame` |
| `config.py` | `Schema`, `RawCols`, `StepCols`, `CycleCols`, `default_schema()` |
| `summarizers.py` | Step table and per-cycle summary engines; optional `add_step_c_rate` |
| `extractors.py` | Low-level step/cycle boundary and classification helpers |
| `merge.py` | Merge and incremental update of `Data` objects |
| `metadata/` | `TestMeta` / `CellMeta` models and serialization helpers |
| `units/` | `CellpyUnits` spec and converters (`pip install cellpycore[units]`) |
| `legacy/` | v1 header tables, `mapping.py`, bridge-only `selectors.py` |
| `testing/` | `mock_data` generators for unit tests and docs examples |

### Code organization patterns

#### Error handling

```python
import logging

from cellpycore.exceptions import CellpyError

logger = logging.getLogger(__name__)

def process_data(data: Data) -> None:
    """Process data with explicit error handling."""
    try:
        make_step_table(data)
    except CellpyError:
        raise
    except Exception as e:
        logger.error("Unexpected error in data processing: %s", e)
        raise
```

Raise `CellpyError` subclasses for domain failures; avoid bare `Exception` at
public boundaries.

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository** (and optionally sibling `architecture-plan` / `cellpy`
   for cross-repo work)
2. **Install dependencies**: `uv sync --all-extras --dev`
3. **Install pre-commit hooks** (one-time):

   ```bash
   uv run pre-commit install
   ```

   Hooks run `ruff check --fix` and `ruff format` on staged Python files
   (`.pre-commit-config.yaml`).

4. **Run tests** to confirm the environment:

   ```bash
   uv run pytest
   ```

Use `uv add <package>` for new dependencies. See
[Astral's uv documentation](https://docs.astral.sh/uv/).

### Development Process

1. **Create an issue branch** from `main` (`<N>-<short-slug>`)
2. **Write tests first** when behavior is non-obvious (TDD where it helps)
3. **Implement** following this guide and `.issueflows/04-designs-and-guides/`
4. **Update docs** when public API or architecture boundaries change
5. **Run** `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`
6. **Open a PR** referencing the issue

### Code Review Process

- All changes reviewed before merge
- Address review comments before merge
- Keep PRs focused and reasonably sized

## Testing Guidelines

`pytest` is the test runner. CI runs on GitHub Actions (see
`.github/workflows/simpletest.yml`).

### Test structure

- **Unit tests** — individual functions and edge cases
- **Integration tests** — module interactions and the `Data` pipeline
- **End-to-end / golden tests** — parity against vendored parquet in `tests/data/`
  (skipped when fixtures are absent)

Benchmarks are marked `@pytest.mark.benchmark` and deselected by default; opt in
with `uv run pytest -m benchmark`.

### Test naming

```python
def test_make_step_table_with_valid_raw_returns_expected_step_count():
    """Step table row count matches golden fixture."""
    pass

def test_validate_raw_frame_missing_column_raises():
    """Missing RawCols column raises CellpyError."""
    pass
```

### Test coverage

- Aim for high coverage on engine paths
- Test edge cases and error conditions
- Legacy bridge tests assert header/unit parity with cellpy; native-path tests
  use polars frames and `default_schema()`

## Code Quality Standards

### Linting and formatting

- **Ruff** for lint and format (`uv run ruff check`, `uv run ruff format --check`)
- Type hints on public APIs
- Line length 88 (ruff default)

### Performance

- Profile hot paths on large fixtures when changing summarizers
- Prefer polars expressions over Python loops on big frames
- Benchmark suite available for regression checks

### Documentation requirements

Docs live in `docs/`, built with
[Zensical](https://zensical.org) (`zensical.toml`; Read the Docs via
`.readthedocs.yaml`). Preview:

```bash
uv run --group docs zensical serve
```

The [API reference](../api/index.md) is generated from Google-style docstrings
via mkdocstrings (`::: cellpycore` in `docs/api/`).

- Document all public APIs
- Keep docs aligned with code and architecture-plan when boundaries move
- Use clear, concise language

### Additional tooling

- **`.cursor/`** — Agent Skills (`/iflow-*`) and project rules for AI-assisted
  development
- **`.aliases`** — optional shell aliases (`source .aliases`)

## Related documentation

| Topic | Location |
|-------|----------|
| User-facing overview | [docs/index.md](../index.md) |
| Standalone consumer guide | [user-guide/standalone-use.md](../user-guide/standalone-use.md) |
| Input format spec | [specifications/harmonized-raw.md](../specifications/harmonized-raw.md) |
| Issue workflow (Agent Skills) | [development/issue-workflow.md](issue-workflow.md) |
| Agent project brief | `.issueflows/04-designs-and-guides/this-project.md` |
| Cross-repo migration | `.issueflows/04-designs-and-guides/cellpy-core-migration.md` |
| Cellpy 2 architecture plans | [github.com/cellpy/architecture-plan](https://github.com/cellpy/architecture-plan) |

---

For questions about these guidelines, open an issue or discuss in a pull request.
