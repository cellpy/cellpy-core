# Issue #96 — Plan

## Goal

Add `Cols.ordered_names()` — a single, canonical way to enumerate native column
name strings in declaration order — and migrate callers off fragile `vars(RawCols)`
/ misuse of `dataclasses.fields()`.

## Constraints

- No separate `__column_order__` tuple (maintainer comment; two sources of truth).
- Implement on `Cols` base class; `RawCols`, `StepCols`, `CycleCols` inherit.
- Scope: helper + migrate known callers + tests/docs in docstring. No engine /
  legacy header changes.

### Prior art

- `tests/test_config_columns._declared_columns()` — iterates `cls.__annotations__`
  (same ordering source; to be replaced by `ordered_names()` in tests).
- `dev/make_harmonized_raw.py` — `vars(RawCols)` + `_` filter for parquet column
  order (migrate to `ordered_names()`).
- `tests/test_harmonized_fixture._rawcols_names()` — same `vars()` pattern (migrate).
- `tests/test_header_mapping._native_values()` — set from `__annotations__`; order
  not needed; **leave as-is**.
- `column-headers-review.md` — three-layer header story; no update needed for this
  small API helper.

## Approach

Add a `@classmethod` on `Cols`:

```python
@classmethod
def ordered_names(cls) -> list[str]:
    cols = cls()
    return [
        getattr(cols, name)
        for name in cls.__annotations__
        if not name.startswith("_")
    ]
```

Design choices (grill-me resolved):

| Decision | Choice |
|----------|--------|
| Ordering source | `cls.__annotations__` declaration order |
| Return value | Column name strings (attribute values) |
| Resolution | `getattr(cls(), name)` — instance lookup for `FlexibleCols` compat |
| `_` prefix | Excluded |
| `__version__` | Not in subclass `__annotations__`; excluded automatically |
| Docs | `ordered_names()` docstring `Note:` — prefer over `vars()` / `dataclasses.fields()` |
| Tests | Drop `_declared_columns`; assert `ordered_names() == *_EXPECTED`; add `_` filter unit test |
| Fixture test | `list(df.columns) == RawCols.ordered_names()` (order + schema) |

Verified: for `RawCols` today, `vars(RawCols)` and `__annotations__` yield the
same 29 names in the same order — parquet regen not expected, but run
`dev/make_harmonized_raw.py` if the order assertion fails.

## Files to touch

| File | Change |
|------|--------|
| [`src/cellpycore/config.py`](src/cellpycore/config.py) | Add `Cols.ordered_names()` classmethod + Google docstring |
| [`tests/test_config_columns.py`](tests/test_config_columns.py) | Remove `_declared_columns`; use `ordered_names()`; add `_` prefix filter test |
| [`dev/make_harmonized_raw.py`](dev/make_harmonized_raw.py) | Replace `vars(RawCols)` loop with `RawCols.ordered_names()` |
| [`tests/test_harmonized_fixture.py`](tests/test_harmonized_fixture.py) | Replace `_rawcols_names()`; assert ordered column list |

## Test strategy

```bash
uv run pytest tests/test_config_columns.py tests/test_harmonized_fixture.py
uv run pytest
```

New / updated coverage:

- `test_raw_cols_match_spec` / step / cycle — `assert cls.ordered_names() == *_EXPECTED`
- `test_ordered_names_skips_underscore_prefixed` — minimal `Cols` subclass smoke test
- `test_harmonized_columns_match_rawcols` — ordered list equality

## Open questions

None — all branches resolved in grill-me.
