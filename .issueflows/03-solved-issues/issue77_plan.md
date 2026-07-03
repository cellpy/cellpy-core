# Issue #77 — Plan: package-folder refactor

## Goal

Reorganise legacy bridge code, unit helpers, and dev mock helpers into dedicated
subpackages — mirroring the existing [`metadata/`](../../src/cellpycore/metadata/)
layout — without changing runtime behaviour or breaking the `cellpycore.legacy` /
`cellpycore.units` import contracts relied on by cellpy.

## Constraints

- **Move-only:** no logic changes, no API redesign, no dependency changes.
- **Back-compat:** `from cellpycore.legacy import …` and `from cellpycore.units import …`
  must keep working (cellpy STEP-05 parity tests, issue #40 re-export contract).
- **Thread-safety / engine path:** do not touch `summarizers.py` / `extractors.py`
  hot-path behaviour.
- **Scope:** folder layout + import rewiring; no shims at old top-level paths.
- Follow [this-project.md](../04-designs-and-guides/this-project.md): `uv run pytest`,
  ruff before PR.

### Prior art

- [`cellpycore/metadata/`](../../src/cellpycore/metadata/) — target pattern:
  subpackage with `__init__.py` curated exports + focused modules (`models.py`,
  `io.py`). See [metadata-scaffolding.md](../04-designs-and-guides/metadata-scaffolding.md).
- [`cellpycore/settings_base.py`](../../src/cellpycore/settings_base.py) — already
  extracted from `legacy.py` to break cycles (issue #40); `legacy` re-exports
  `BaseSettings` / `DictLikeClass`.
- Issue #40 promotion — `CellpyUnits` lives in `units.py`; `legacy.py` re-exports
  it. Any move must preserve that re-export.
- Issue #67 — `legacy_selectors.py` split from broken `selectors.py`; bridge-only,
  defaults to `legacy_schema()`.
- Graph communities **10** (header mapping), **11** (legacy selectors / `legacy_schema`),
  **12** / **19** (units), **16** (`OldCellpyCellCore`) — all affected by import paths
  only.
- God nodes: `OldCellpyCellCore`, `HeadersNormal`, `CellpyUnits` — high fan-out;
  update importers carefully; cellpy only touches `legacy` / `units` top-level.
- Toolbox: none relevant (`00-tools/` empty).

## Approach

### Target layout

```
src/cellpycore/
  legacy/
    __init__.py       # re-export full legacy public surface (today's legacy.py)
    mapping.py        # today's header_mapping.py
    selectors.py      # today's legacy_selectors.py
  testing/
    __init__.py
    mock_data.py      # create_raw_data (today's _helpers.py body)
  units/
    __init__.py       # today's units.py (single module for now)
```

Old top-level modules **`header_mapping.py`**, **`legacy_selectors.py`**,
**`_helpers.py`**, **`legacy.py`**, **`units.py`** are **deleted** after moves
(no shims).

**Why not split `legacy.py` further now?** Issue asks for a folder, not a
decomposition. Keeping the body in `legacy/__init__.py` (or `legacy/_core.py`
imported by `__init__.py` if the file is awkwardly large) minimises diff noise.
`mapping.py` and `selectors.py` are already separate modules — they move as-is.

**Units package:** move `units.py` → `units/__init__.py` unchanged. Optional
later split (`spec.py` / `converters.py`) is out of scope.

**Mock data:** move `_helpers.py` body → `testing/mock_data.py`; update all
importers to `from cellpycore.testing.mock_data import create_raw_data`.

### Import rewiring (no shims)

| Old import | New import |
|---|---|
| `from cellpycore import header_mapping` | `from cellpycore.legacy import mapping` |
| `from cellpycore import legacy_selectors` | `from cellpycore.legacy import selectors` |
| `from cellpycore._helpers import create_raw_data` | `from cellpycore.testing.mock_data import create_raw_data` |
| `from cellpycore.legacy import …` | unchanged (package `__init__.py` preserves surface) |
| `from cellpycore.units import …` | unchanged (package `__init__.py` preserves surface) |

**Importers to update** (grep-verified):

| File | Change |
|---|---|
| [`cell_core.py`](../../src/cellpycore/cell_core.py) | `header_mapping` → `legacy.mapping`; update comments |
| [`tests/test_header_mapping.py`](../../tests/test_header_mapping.py) | `header_mapping` → `legacy.mapping` |
| [`tests/test_legacy_selectors.py`](../../tests/test_legacy_selectors.py) | `legacy_selectors` → `legacy.selectors` |
| [`tests/conftest.py`](../../tests/conftest.py) | `_helpers` → `testing.mock_data` |
| [`tests/test_creation.py`](../../tests/test_creation.py) | same |
| [`tests/test_schema.py`](../../tests/test_schema.py) | same |
| [`dev/demo_mock_data.py`](../../dev/demo_mock_data.py) | same |
| [`__init__.py`](../../src/cellpycore/__init__.py) | docstring path mentions only |
| [`this-project.md`](../04-designs-and-guides/this-project.md) | path references in entry-points section |

Docstrings in [`config.py`](../../src/cellpycore/config.py) that mention
`header_mapping` / `legacy_selectors` by old module path — update to new paths.

**Do not** add deprecated re-export shims at the old top-level module names.

### Ordering (avoid import cycles)

1. Create `units/` package first (no dependency on `legacy/` package layout).
2. Create `legacy/` package (`legacy/__init__.py` still imports `cellpycore.units`).
3. Move `header_mapping.py` → `legacy/mapping.py`; `legacy_selectors.py` →
   `legacy/selectors.py`; fix internal imports inside moved modules.
4. Create `testing/mock_data.py` from `_helpers.py`; delete `_helpers.py`.
5. Update all importers (table above); delete old top-level `legacy.py`, `units.py`.
6. Run full test suite + ruff; `graphify update .`.

### Out of scope (explicit)

- Moving `OldCellpyCellCore` out of `cell_core.py` (issue mentions it as
  example of legacy *concern*, not a move target).
- Splitting `units.py` or `legacy/__init__.py` into multiple files.
- cellpy repo changes (no direct imports of moved modules there).
- Rewriting archived issue-flow docs under `03-solved-issues/`.

## Files to touch

| Path | Change |
|---|---|
| `src/cellpycore/units/__init__.py` | **new** — body of current `units.py` |
| `src/cellpycore/units.py` | **delete** |
| `src/cellpycore/legacy/__init__.py` | **new** — body of current `legacy.py` |
| `src/cellpycore/legacy/mapping.py` | **move** from `header_mapping.py` |
| `src/cellpycore/legacy/selectors.py` | **move** from `legacy_selectors.py` |
| `src/cellpycore/testing/__init__.py` | **new** — minimal |
| `src/cellpycore/testing/mock_data.py` | **new** — body of `_helpers.py` |
| `src/cellpycore/legacy.py` | **delete** |
| `src/cellpycore/header_mapping.py` | **delete** |
| `src/cellpycore/legacy_selectors.py` | **delete** |
| `src/cellpycore/_helpers.py` | **delete** |
| `src/cellpycore/cell_core.py` | import + comment updates |
| `src/cellpycore/config.py` | docstring path updates |
| `src/cellpycore/__init__.py` | docstring path updates |
| `tests/test_header_mapping.py` | import updates |
| `tests/test_legacy_selectors.py` | import updates |
| `tests/conftest.py`, `tests/test_creation.py`, `tests/test_schema.py` | mock_data imports |
| `dev/demo_mock_data.py` | mock_data import |
| `.issueflows/04-designs-and-guides/this-project.md` | path references |
| `graphify-out/` | rebuild after code moves |

## Test strategy

```bash
uv run pytest                  # full suite must stay green
uv run ruff check && uv run ruff format --check
```

No new tests expected (behaviour unchanged). Existing coverage locks the move:

- `tests/test_header_mapping.py` — mapping totality + bridge parity
- `tests/test_legacy_selectors.py` — selector behaviour
- `tests/test_units_converters.py`, `tests/test_units_optional.py` — units package
- `tests/test_limits.py`, `tests/test_schema.py`, golden e2e — legacy re-exports

Manual smoke: `from cellpycore.legacy import CellpyUnits, HeadersNormal, NoDataFound`
and `from cellpycore.units import CellpyUnits, get_cellpy_units` both succeed;
`CellpyUnits` from both paths is the same class.

## Decisions (confirmed)

1. **`_helpers` → `cellpycore/testing/mock_data.py`**; delete `_helpers.py`.
2. **No shims** — update all importers; delete old top-level module files.
3. **Monolith `legacy/`** — `legacy.py` → `legacy/__init__.py`; only `mapping.py`
   and `selectors.py` as separate modules inside the package.

## Scope check

One behaviour-neutral PR (~15 files moved/added/deleted, import updates). Still
appropriate as a single PR.

---

**Status:** plan confirmed — ready for `/iflow-start`.
