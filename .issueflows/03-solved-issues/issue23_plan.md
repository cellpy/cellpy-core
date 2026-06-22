# Plan for issue #23: Fix ir_to_summary — internal resistance assigned to the wrong cycle

## Goal

Replace the hard-coded, buggy IR selection in `summarizers.ir_to_summary` with a
**pluggable extractor** abstraction (new `extractors.py`). `ir_to_summary` (and
`make_core_summary`) gain an `ir_extractor` keyword argument that defaults to an
extractor which takes the **last datapoint's IR in the cycle's last charge step** →
`ir_charge` and the **last datapoint's IR in the cycle's last discharge step** →
`ir_discharge` per cycle (literal value, no skipping of zeros). This fixes the
off-by-one cycle attribution, makes the multiple-IR-step behaviour explicit, and lets
cellpy developers swap in their own IR logic without touching the engine.

## Decisions (confirmed with user, 2026-06-22)

- **Q1 — default "last IR":** option (a), **literal** — the `internal_resistance` of the
  **last raw datapoint** of the cycle's **last charge step** (resp. last discharge step);
  no skipping of zero/null values.
- **Missing → NaN, not 0.0.** Cycles with no charge (resp. discharge) step get **NaN**
  instead of the legacy `0.0`. (Deliberate behaviour change; reflected in the regenerated
  oracle and tests.)
- **Q2 — signature:** pure — `__call__(*, raw, steps, summary, schema) -> per-cycle frame`.
- **Q3 — naming:** base class `SummaryExtractor`, default `LastIRExtractor`, kwarg
  `ir_extractor`.
- **Q4 — oracle:** OK to regenerate `arbin_cc_summary_expected.parquet`; cellpy's legacy
  `_ir_to_summary` stays untouched (contract); only cellpy-core's native path is corrected.

## Constraints

- **Polars-native only.** #21 already ported `ir_to_summary` to polars on the native
  schema; the extractor stays polars and is pure (operates on frames, returns a frame).
- **Extensibility is a project goal** ("easy for developers of the full cellpy library to
  use and extend it") — so a strategy abstraction is justified here despite KISS. But:
  **build exactly one extractor now** (the default). Do *not* refactor `c_rates_to_summary`
  / end-voltage onto the abstraction in this issue (design the base class so they *could*
  adopt it later; note as future follow-up).
- **Don't collide with `selector`.** `make_core_summary` already has a `selector` kwarg
  and `selectors.py` does cycle-end *row* selection. An **extractor** is a different
  concept (per-cycle *value* extraction strategy) — keep the names/docs clearly distinct.
- **Oracle is buggy-locked.** `tests/data/arbin_cc_summary_expected.parquet` (18×27)
  freezes the current wrong `ir_charge`/`ir_discharge`. The new default changes those
  values, so the oracle must be regenerated via `dev/regenerate_test_data.py` as an
  **intentional, reviewed** change (issue "Caution"). Step oracle is unaffected.
- **Legacy seam parity.** cellpy's own `_ir_to_summary` (cellpy repo) keeps the old
  behaviour (contract). Only cellpy-core's native path changes. Reconcile `test_golden.py`
  summary parity + the `OldCellpyCellCore` bridge together with the oracle regen.
- **Docstrings:** Google-style (project rule).

### Prior art

- `ir_to_summary` (`summarizers.py:681`) — current behaviour: per cycle, first
  `charge`/`discharge` step, IR of that step's **first** raw datapoint; missing → `0.0`.
  New work: **gut the selection**, delegate to an extractor; keep the join + `fill_null`.
- `c_rates_to_summary._first_rate` (`summarizers.py:650`) — sibling "per-cycle value from a
  step-type" helper (group-by cycle / `maintain_order` / left-join onto summary). New work:
  **mirror its shape** inside the default extractor; candidate to adopt the abstraction
  *later* (out of scope now).
- `_classify_steps` → `StepType.IR` (`summarizers.py:149`, `config.py:129`) — a dedicated
  `"ir"` step type already exists (instantaneous pulse, all deltas ≈ 0). New work: the
  **default** extractor keys off charge/discharge-step IR (per the chosen semantics); an
  `IRStepExtractor` keyed off the `"ir"` step type is a natural **alternative** the new
  abstraction makes trivial to add (not built now).
- `selector` kwarg + `selectors.create_selector` (`cell_core.py:161`, `selectors.py`) —
  existing per-cycle **row** selection. New work: coexist; extractor is value-extraction,
  named separately to avoid confusion.
- Legacy origin `cellreader.py::_ir_to_summary` (cellpy repo line 6360) — source of the
  `# THIS DOES NOT WORK PROPERLY` quirk. New work: do **not** re-port; cellpy keeps it.

## Approach

**New module `src/cellpycore/extractors.py`.**

A small callable-class hierarchy (the "boundaries" the issue asks for):

```python
class SummaryExtractor:
    """Callable that derives per-cycle summary column(s) from the engine frames.

    Returns a polars frame keyed by the cycle-number column carrying one or more
    columns to be left-joined onto the summary (nulls filled by the caller).
    """
    def __call__(self, *, raw, steps, summary, schema) -> "pl.DataFrame": ...

class LastIRExtractor(SummaryExtractor):
    """Default IR extractor: per cycle, the ``internal_resistance`` of the last raw
    datapoint of the cycle's last charge step -> ``ir_charge`` and the last datapoint
    of the cycle's last discharge step -> ``ir_discharge``. Cycles with no such step
    get NaN."""
```

**`ir_to_summary` becomes thin:**
1. `extractor = ir_extractor or LastIRExtractor()`.
2. `per_cycle = extractor(raw=raw, steps=steps, summary=summary, schema=schema)`.
3. Left-join `per_cycle` onto `summary` on the cycle-number column. Missing values stay
   **NaN** (no `fill_null(0.0)` — deliberate change from the legacy `0.0`).

**Thread the kwarg:**
- `summarizers.ir_to_summary(data, schema=None, ir_extractor=None)`.
- `cell_core.CellpyCellCore.make_core_summary(..., ir_extractor=None)` → passes it down
  (line 205). Mirror in `OldCellpyCellCore.make_core_summary` (line 617) so the cellpy
  bridge can pass one too (defaults preserve today's call sites).

**Default semantics — "last IR value" (confirmed):** per cycle, identify the cycle's
**last charge step** (resp. last discharge step) in natural (maintain_order) order, and
read the `internal_resistance` of that step's **last raw datapoint** — literal value, no
zero/null skipping. Missing step → **NaN**.

**Phasing inside `/issue-start`:**
- *A (read-only):* on `arbin_cc_raw.parquet` (18 cycles, real IR 0–56) produce a small
  before/after per-cycle table showing the confirmed rule (last datapoint of last
  charge/discharge step) vs the current first-datapoint rule, to demonstrate the off-by-one
  is corrected. (Rule itself already decided — this is verification, not exploration.)
- *B:* implement `extractors.py` + thin `ir_to_summary` (NaN for missing) + kwarg
  threading + docstrings.
- *C:* regenerate the summary oracle (reviewed); reconcile `test_golden.py` + bridge; add
  tests (synthetic boundary-straddling fixture + multiple-IR-step + a custom-extractor
  swap test proving the kwarg works).

## Files to touch

- `src/cellpycore/extractors.py` — **new**: `SummaryExtractor` base + `LastIRExtractor`.
- `src/cellpycore/summarizers.py` — slim `ir_to_summary` to delegate to the extractor;
  add `ir_extractor` param; update docstring (drop the "oracle-locked quirk" note).
- `src/cellpycore/cell_core.py` — add `ir_extractor` kwarg to both `make_core_summary`s,
  pass through.
- `tests/data/arbin_cc_summary_expected.parquet` — regenerated oracle (reviewed).
- `tests/test_schema.py` — extend `test_ir_to_summary_native` (boundary-straddling +
  multiple-IR-step + custom-extractor swap).
- `tests/test_golden.py` — update summary-IR expectations if it pins the old values.
- `tests/test_config_columns.py` — only if column expectations shift (not expected).
- `.issueflows/04-designs-and-guides/` — new `summary-extractors.md` (the abstraction +
  IR semantics + oracle-regen decision), cross-linked from `step-table-polars-migration.md`.

## Test strategy

- `uv run pytest` — full suite green.
- New native unit tests: (1) IR step straddling a cycle boundary lands on the right cycle;
  (2) multiple IR steps per cycle → "last" rule; (3) passing a custom `ir_extractor`
  overrides the default (proves the contract).
- Manual before/after per-cycle IR table on `arbin_cc_raw.parquet` (record in status note).

## Open questions

All four resolved — see **Decisions (confirmed with user, 2026-06-22)** above. One small
implementation note carried into `/issue-start`: pick float `NaN` vs polars `null`
consistently for the "missing step" case (both render as missing). Lean toward float
`NaN` to match the column's float dtype and the user's "nan" preference, and verify the
regenerated oracle + downstream gravimetric/areal scaling handle it predictably.

## Scope note

One new small module + slimming one function + kwarg threading + one design note + oracle
regen — cohesive, one PR. The base class is intentionally minimal (one concrete extractor);
generalising `c_rates`/end-voltage onto it is a deliberate **future follow-up**.
