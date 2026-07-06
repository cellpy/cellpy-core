# Issue #96: Add explicit column ordering to RawCols/CycleCols/StepCols

Source: https://github.com/cellpy/cellpy-core/issues/96

## Original issue text

## Context

Enumerating native column names via `vars(RawCols)` works but is easy to misuse (e.g. `dataclasses.fields(RawCols)` only returns inherited `__version__` from `BaseCols`).

Source: `SCRATCHPAD.md` (Ordered headers section).

## Proposal

Add explicit ordering to header classes, e.g.:

```python
class RawCols(Cols):
    __column_order__ = (
        "datapoint_num", "source_datapoint_num", "mask", ...
    )

    @classmethod
    def ordered_names(cls) -> list[str]:
        cols = cls()
        return [getattr(cols, name) for name in cls.__column_order__]
```

Apply the same pattern to `CycleCols` and `StepCols` where column order matters (fixtures, converters, parquet I/O).

## Acceptance criteria

- [ ] `RawCols.ordered_names()` (or equivalent) returns names in harmonized-raw spec order
- [ ] `dev/make_harmonized_raw.py` and tests can use the helper instead of `vars(RawCols)`
- [ ] Document that `fields(RawCols)` is not the right tool for column enumeration

## Comments (curated summary)

- **Additional tasks**:
  - Implement column ordering helper on the `Cols` base class so `RawCols`, `CycleCols`, and `StepCols` inherit it rather than duplicating logic per class.
- **Clarifications / constraints**:
  - Do not introduce a separate `__column_order__` tuple — re-listing column names creates two sources of truth.
  - Derive order from dataclass field declaration order; filter out fields whose names start with `_`.
- **Superseded / retracted**:
  - Per-class `__column_order__` tuple plus a classmethod that maps attribute names through that tuple (the pattern shown in the issue body).

_Note: this section is an interpretive summary of the comment thread, not a verbatim dump. Source comments: 1, last comment by @jepegit on 2026-07-05._
