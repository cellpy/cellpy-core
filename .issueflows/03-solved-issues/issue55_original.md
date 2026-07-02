# Issue #55: Add validating front door for raw frames (Data.from_raw_frame)

Source: https://github.com/cellpy/cellpy-core/issues/55

## Original issue text

## Context

The slim-consumer story (a user who builds a polars DataFrame in the native `config.RawCols` schema themselves and wants step/cycle summaries straight from cellpy-core, without cellpy) currently has no validating entry point:

```python
core = CellpyCellCore(initialize=True)
core.data.raw = df   # accepts anything
```

A wrong column name or dtype only fails deep inside a polars expression in `summarizers`, with an error message that does not point back at the actual problem (the input frame not matching the schema).

## Proposal

Add a small validating constructor on `Data` (in `src/cellpycore/cell_core.py`):

```python
data = Data.from_raw_frame(df, validate=True)
```

Behavior:

- Wraps the frame in a fresh `Data` (with the usual `MockMetaTestDependent`, so the graceful-degradation metadata guarantee is untouched).
- When `validate=True` (default), checks the frame against `config.RawCols`:
  - required columns present (clear error listing missing ones);
  - dtype sanity for the load-bearing columns, in particular `epoch_time_utc` must be int64 (ns, UTC â€” the STEP-11 contract) and datapoint/cycle/step numbers integer;
  - optional columns (`test_id`, `internal_resistance`, â€¦) allowed absent.
- Fails fast with a single actionable error message instead of a deep polars stack trace.

Keep it KISS: one classmethod + one module-level validation helper, no schema-validation framework.

## Tests

- Happy path: valid native frame round-trips through `make_step_table` + `make_summary` identically to plain `data.raw = df`.
- Missing column â†’ error naming the missing column(s).
- Wrong dtype on `epoch_time_utc` â†’ error mentioning the int64-ns contract.
- `validate=False` skips checks entirely.

## Links

- Raised while discussing the future slim-consumer / cellpy v2 interaction pattern (roadmap doc `cellpy-core-integration-roadmap.md`).
- Related: #42 (reset-granularity normalization is the other half of "arbitrary external raw frames").
