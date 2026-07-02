# Issue #42: Engine: reset-granularity normalization for cumulative raw inputs

Source: https://github.com/cellpy/cellpy-core/issues/42

## Original issue text

Deferred follow-up recorded in `.issueflows/04-designs-and-guides/step-table-polars-migration.md` ("Reset-granularity normalization ... a deliberate future follow-up, not done now").

## Context

The harmonized raw capacity columns (`cumulative_charge_capacity` / `cumulative_discharge_capacity`) mandate **cycle-cumulative** semantics (per cycle, per direction, reset at each cycle boundary). The summary path depends on this (it reads the cycle's last raw datapoint as that cycle's capacity).

## Scope

- Add an engine normalization step that also accepts **step-cumulative** and **test-cumulative** raw from other cyclers and normalizes them to the cycle-cumulative convention before aggregation.
- Keep cycle-cumulative inputs a no-op; goldens (STEP-06) unchanged.
- Add fixtures/tests for the non-cycle-cumulative input variants.

Lower priority: only the cycle-cumulative Arbin path is exercised today.
