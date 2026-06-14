# Plan for issue #12: Port `make_step_table` into cellpy-core (bring `CellpyLimits` with it)

## Current state (important — issue is partly stale)

Most of task 1 is **already done**. Investigation findings:

- `summarizers.make_step_table(...)` is fully implemented (`src/cellpycore/summarizers.py`,
  lines ~59–413) — a near-verbatim **pandas** port of `cellpy`'s
  `cellreader.py::make_step_table` (groupby + agg `mean/std/min/max/first/last/delta`,
  mask-based step-type classification, flatten, sort).
- `CellpyCellCore.make_core_step_table(...)` already delegates to it
  (`src/cellpycore/cell_core.py`, lines ~316–374). The `# TODO: implement make step table`
  marker is stale (the line still exists as a comment, but the method exists).
- `cellpy` already drives it across the seam: `cellreader.py::make_step_table` calls
  `self.core.make_core_step_table(..., raw_limits=self.raw_limits, nom_cap=nom_cap_abs)`
  (lines ~3071–3084). `raw_limits` and `nom_cap` are passed **by value**.

So the literal "port the logic" task is complete. What is genuinely **not** done:

1. **`CellpyLimits` is not in core.** Core only has a placeholder `DEFAULT_RAW_LIMITS`
   dict in `summarizers.py` with every value `= 0.001` (marked "TODO: implement
   properly"). Legacy `CellpyLimits` (`cellpy/parameters/internal_settings.py:444`) has
   the *same keys* but real defaults (`current_hard=1e-13`, `stable_current_hard=2.0`,
   `stable_voltage_hard=2.0`, `stable_charge_hard=0.9`, …).
2. **Step-type constants placement undecided.** `STEP_TYPES` / `CAPACITY_MODIFIERS` in
   `legacy.py` are still flagged `# NOT USED (YET?)`.
3. **No parity / step-table tests** in `tests/` (only schema/import/creation tests exist).
4. **(architectural)** The ported engine is **pandas + legacy schema only**. It reads
   `schema.raw.*_txt` names (e.g. `data_point_txt`, `current_txt`, `voltage_txt`) which
   exist on legacy `HeadersNormal` but **not** on native `config.RawCols` (which uses
   `datapoint_num`, `current`, `potential`, …). The native test fixture
   (`_helpers.create_raw_data`) produces a **polars** frame with native names, so the
   current `make_step_table` cannot consume the native data model at all. The issue
   comment (@jepegit, 2026-06-14) explicitly says the step engine should use **polars**.

## Goal (FULL scope — confirmed by user)

Migrate the core compute engine to **polars-native** and deliver all of #12 in **one PR**:
1. Bring `CellpyLimits` into core (`legacy.py`); make `DEFAULT_RAW_LIMITS` derive from it
   (standalone defaults now **match legacy** — confirmed acceptable).
2. Settle the step-type constants in `legacy.py` (canonical, drop "NOT USED").
3. **Rewrite the step-table engine to polars + the native `config` schema**, always
   emitting the full `StepCols` set (NaN for signals absent from `data.raw`).
4. **Rewrite the summary path (`make_core_summary`, `summarizers` summary functions,
   `selectors`) to polars-native too** (the user chose engine consistency now, not a
   follow-up).
5. Provide a **pandas↔polars + legacy↔native bridge in `OldCellpyCellCore`** so the
   `cellpy` seam (which drives the engine with pandas + legacy `*_txt` names) keeps
   working byte-stably.
6. Add parity / behaviour tests for both the native and legacy-bridge paths.

### Scope & risk warning (please read — KISS check)

This is a **large, high-risk** change: the entire core compute path
(`summarizers.py` ~876 lines + `selectors.py` + `cell_core.py`) is pandas today
(`narwhals`/`polars` are only in `config.py`/`_helpers.py`). Rewriting all of it to
polars-native **plus** a pandas↔polars round-trip bridge **in one PR** is the opposite of
incremental. The issue comment itself flags the round-trip as "not straightforward"
(polars has no index and disallows duplicate column names; pandas relies on both).

I will proceed as chosen, but I'm flagging two safety nets I strongly recommend even
within a single issue:
- keep each rewritten function behaviour-locked by a test written *before* the rewrite
  (capture current pandas output, assert the polars output matches), and
- still split into reviewable commits (CellpyLimits/constants → step engine → summary
  engine → bridge) even if it lands as one PR.

If at implementation time the round-trip bridge proves fragile, I will pause and re-confirm
rather than ship something that risks the cellpy seam.

## Constraints

- KISS: minimal, evidence-based change. No speculative abstractions.
- Keep the integrated `cellpy` path byte-for-byte safe: `cellpy` passes its own
  `raw_limits` by value, so changing core's standalone default must not affect the driven
  path.
- Thread-safe / schema-injected design must be preserved (engine reads names from the
  injected `Schema`).
- `uv` for all env/test commands; Python ≥3.13.

### Prior art

- `DEFAULT_RAW_LIMITS` (`cellpycore.summarizers`) — placeholder dict, keys identical to
  legacy `CellpyLimits`; new work: **migrate** — derive it from a `CellpyLimits` dataclass
  via `dataclasses.asdict(CellpyLimits())` so keys/defaults match legacy.
- `CellpyUnits`, `HeadersNormal/Summary/StepTable` (`cellpycore.legacy`) — verbatim copies
  of `cellpy/parameters/internal_settings.py`, built as `@dataclass(BaseSettings)`; new
  work: **mirror** — add `CellpyLimits` the same way, in the same module, so the bridge
  copies stay co-located and field-comparable (supports the future contract test,
  jepegit/cellpy#378).
- `CAPACITY_MODIFIERS` / `STEP_TYPES` (`cellpycore.legacy`) — currently unused module
  constants; new work: **coexist** (keep as the canonical list) or delete if confirmed
  dead — see Open questions.
- `make_core_summary` / `make_core_step_table` (`cell_core.py`) — establish the
  "core method delegates to a `summarizers` function using `self.schema`" convention;
  new work: mirror (no new entry points needed).

## Approach

**Phase A — `CellpyLimits` into core (the heart of #12):**

1. Add a `CellpyLimits` dataclass to `src/cellpycore/legacy.py` (next to `CellpyUnits`),
   copied field-for-field from `cellpy/parameters/internal_settings.py:444` (same
   `BaseSettings` base so it stays a contract-comparable mirror).
2. Replace the hand-written `DEFAULT_RAW_LIMITS` literal in `summarizers.py` with
   `DEFAULT_RAW_LIMITS = asdict(CellpyLimits())` (import from `legacy`). This makes the
   standalone default *match legacy* instead of the current all-`0.001` placeholder.
   - The integrated path is unaffected (cellpy passes its own `raw_limits`).
   - This is a **behaviour change for standalone core defaults only** — call it out
     (see Open questions).
3. Optionally expose `CellpyLimits` on `OldCellpyCellCore` (e.g. `self.raw_limits =
   asdict(CellpyLimits())`) so the legacy bridge has a real default. (Confirm before
   adding state.)

**Phase B — step-type constants placement:**

4. Keep `STEP_TYPES` / `CAPACITY_MODIFIERS` in `legacy.py`, drop the "NOT USED (YET?)"
   note, and (lightly) reference `STEP_TYPES` from the engine as the source of valid
   type strings, or document them as the canonical list. No new module unless the user
   prefers a dedicated `internal_settings.py`.

**Phase C — tests:**

5. Add `tests/test_step_table.py` exercising `OldCellpyCellCore().make_core_step_table`
   (legacy schema, pandas) on a small synthetic **pandas** raw frame with `HeadersNormal`
   column names. Assert:
   - output columns match `docs/data_format_specifications/step_table.md` / the flattened
     `HeadersStepTable` naming,
   - known steps classify correctly (charge / discharge / rest) given controlled current/
     voltage,
   - `nom_cap` / `add_c_rate` produce `rate_avr`,
   - `from_data_point` returns a DataFrame.
   Full cross-repo byte-parity against real `cellpy` testdata is **out of scope** (would
   require importing `cellpy` + shipped testdata); the synthetic test plus the existing
   field-by-field header equality covers regression risk.

**Phase D — polars-native step engine + native schema (IN SCOPE):**

6. Rewrite `make_step_table` to consume native polars `data.raw` (native `RawCols` names)
   and emit the **full** native `StepCols` set. Use polars `group_by([cycle_num, step_num,
   sub_step_num]).agg(...)` with `mean/std/min/max/first/last` + a `delta` expression
   (`100*(last-first)/abs(first)`, zero-start special case as in legacy).
   - **Full column policy (confirmed):** always emit every `StepCols` aggregate. For
     signals not present in `data.raw` (e.g. `power`, `charge_energy`, `discharge_energy`
     are absent from the native `create_raw_data`), emit the columns filled with null/NaN
     rather than omitting them. This keeps the output schema stable and spec-complete.
   - Step-type classification: port the mask logic to polars expressions, schema-injected,
     using the `CellpyLimits`-derived limits. Keep semantics identical to legacy.

**Phase E — polars-native summary path (IN SCOPE, user chose consistency now):**

7. Rewrite the summary functions in `summarizers.py` (`generate_absolute_summary_columns`,
   `*_to_summary`, specific/equivalent-cycle helpers) and `selectors.py` to polars
   expressions, schema-injected. Behaviour-lock each with a before/after test capturing the
   current pandas output.

**Phase F — cellpy seam bridge (IN SCOPE):**

8. `cellpy` drives the engine via `OldCellpyCellCore` with a **pandas** `data.raw` and
   **legacy `*_txt`** names. Add a bridge in `OldCellpyCellCore` (and/or the
   `make_core_*` methods) that: (a) converts incoming pandas→polars, (b) maps legacy
   names→native via the schema, runs the polars engine, then (c) maps native→legacy and
   converts polars→pandas on the way out. Must handle pandas index + duplicate-column
   tolerance vs polars' lack thereof (the round-trip risk the issue comment names).
   Re-run cellpy's own `make_step_table`/`make_summary` tests against the editable core to
   confirm parity.

## Files to touch

- `src/cellpycore/legacy.py` — add `CellpyLimits` dataclass; settle `STEP_TYPES` /
  `CAPACITY_MODIFIERS` (drop "NOT USED"; make canonical).
- `src/cellpycore/summarizers.py` — derive `DEFAULT_RAW_LIMITS` from `CellpyLimits`;
  rewrite `make_step_table` (polars, full native `StepCols`) and all summary helpers to
  polars.
- `src/cellpycore/selectors.py` — rewrite to polars.
- `src/cellpycore/cell_core.py` — `OldCellpyCellCore` pandas↔polars + legacy↔native
  bridge; real `raw_limits` default; remove stale `# TODO: implement make step table`.
- `tests/test_step_table.py`, `tests/test_summary.py` — **new**, native + legacy-bridge
  behaviour tests (incl. before/after lock tests captured pre-rewrite).
- `.issueflows/04-designs-and-guides/` — new note recording the polars-native engine
  decision, the bridge design, and the round-trip rules (index/duplicate columns).

## Test strategy

- **Lock-first:** before rewriting each function, capture its current pandas output (small
  synthetic input) and assert the polars rewrite reproduces it — this is the regression
  guard for an engine swap.
- `uv run pytest` — full suite green.
- New tests:
  - **native path:** `CellpyCellCore().make_core_step_table` / `make_core_summary` on a
    polars `data.raw` from `_helpers.create_raw_data`; assert full `StepCols`/`CycleCols`
    columns, charge/discharge/rest classification, `rate_avr`/`from_data_point`.
  - **legacy-bridge path:** `OldCellpyCellCore()` on a pandas raw frame with
    `HeadersNormal` names; assert flattened `HeadersStepTable` columns + classification
    (locks the cellpy seam).
- Cross-repo parity: run `cellpy`'s existing `make_step_table` / `make_summary` tests
  against the editable `cellpy-core`.
- Sanity: `asdict(CellpyLimits())` keys equal current `DEFAULT_RAW_LIMITS` keys (verified
  in planning — they match).

## Resolved decisions (from planning Q&A)

- **Scope:** full — all of #12, including the polars rewrite, in one PR.
- **Location:** `CellpyLimits` + step-type constants live in `legacy.py`.
- **Defaults:** standalone `DEFAULT_RAW_LIMITS` now matches legacy `CellpyLimits` values.
- **Engine:** polars-native engine + explicit pandas↔polars / legacy↔native bridge in
  `OldCellpyCellCore` (not narwhals).
- **Summary path:** migrated to polars in this issue too (engine consistency now).
- **Columns:** always emit the full `StepCols` set (NaN for absent signals).
- **Phasing:** single PR (with the safety nets in the risk warning above).

## Open questions (remaining)

- None blocking. Confirm the plan to proceed to `/issue-start`. (I will still pause and
  re-confirm if the pandas↔polars seam bridge proves fragile during implementation.)
