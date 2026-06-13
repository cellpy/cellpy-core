# Integrating `cellpy-core` into `cellpy` — strategy and findings

Durable record of how the legacy `cellpy` library will start consuming `cellpy-core`,
and what must be prepared **inside `cellpy`** before that is safe. This is project
memory: it captures the investigation results, the decisions taken, and the
recommended first steps so the next worker does not have to re-derive them.

Companion GitHub issue lives on the **`cellpy`** repo (jepegit/cellpy) — see
"Tracking" at the bottom.

## Context & goal

- `cellpy` (jepegit/cellpy, v1.0.3, Python 3.10–3.13, setuptools build) is the large,
  mature consumer. The "find steps and cycles + build per-step / per-cycle tables"
  logic currently lives in `cellpy/readers/cellreader.py` (~305 KB) and
  `cellpy/readers/core.py`.
- `cellpy-core` (this repo, v0.1.0, Python ≥3.13, hatchling build, narwhals/polars/
  duckdb) is the small, fast re-implementation of that core processing.
- Goal: let `cellpy` delegate its core processing to `cellpy-core` **without** publishing
  `cellpy-core` to PyPI yet (git / editable dependency during development).

## Key findings

1. **`cellpy` imports nothing from `cellpycore` today** — integration is greenfield, not
   half-wired.
2. **Branch `334-isolate-parts-needed-for-cellpy-core` is the in-tree ancestor of
   `cellpy-core`.** It created `cellpy/slim/` (`cell_core.py`, `summarizers.py`,
   `selectors.py`, `units.py`) — the files `cellpy-core` was later extracted from and
   evolved (own `Data`, `config.Cols`, `legacy.py`, units removed from the base class).
3. **Branch 334 already proves the "isolate the Data object" seam works.** In its
   `cellreader.py`:
   - `self.core = CellpyCellCore(...)` is constructed on `CellpyCell`.
   - the `data` property returns `self.core._data` (ownership of `Data` moved into core).
   - `make_summary` delegates to `self.core.make_core_summary(...)` /
     `add_scaled_summary_columns(...)`.
   - identity/unit accessors delegate to `self.core._...`.
   - `tests/test_slim.py` documents/exercises the seam.
4. **The delegation contract is currently byte-for-byte safe.** `cellpycore/legacy.py`
   carries verbatim copies of `cellpy`'s authoritative settings:
   - `HeadersNormal`, `HeadersSummary`, `HeadersStepTable` — **identical** field names
     and values (verified field-by-field against `cellpy/parameters/internal_settings.py`).
   - `CellpyUnits` — **identical** (incl. `resistance="ohm"`; the `"Ohms"` in the
     docstring is a shared cosmetic artifact, not a value divergence).
5. **`make_step_table` is NOT ported to core yet** (both `slim` and `cellpy-core` carry
   `# TODO: implement make step table`). The step half still lives in `cellreader.py`.

## Decisions taken

1. **Mine branch 334, do not merge it.** It is 136 ahead / 24 behind master with a
   ~1-year-old merge-base (2025-07-01). Both sides heavily rewrote `cellreader.py` in
   **overlapping regions** (class header/properties ~330–470; summary methods
   ~5400–6270, where master independently added `add_to_summary` and cycle-selection
   methods). A raw merge is high-pain and risks silently dropping master features.
   The seam is ~5 small edit points → re-derive on fresh master instead.
2. **Target `cellpycore.OldCellpyCellCore`** (the legacy bridge class) for the first
   integration, not the lean base — it restores the old headers/units that `cellpy`
   still expects.
3. **Consume `cellpy-core` as a git / editable dependency** during development (no PyPI
   release required). Pin to tag/commit for releases.

## The seam (re-derived onto current master)

Minimal first integration PR in `cellpy` (mirrors what 334 proved, against the real
package):

1. Add `cellpycore` as a git/editable dependency.
2. On `CellpyCell`: construct `self.core = OldCellpyCellCore(...)`.
3. Move `Data` ownership: `data` property reads/writes `self.core._data`.
4. Route `make_summary` (and master's newer `add_to_summary` / cycle-selection methods)
   through `self.core`.
5. Leave `make_step_table` in `cellreader.py` for now.
6. Port `tests/test_slim.py` (from 334) as the seam's acceptance test; keep the full
   suite green.

## Open decisions (resolve early — cheap, unblocking)

- **Python floor.** `cellpy-core` requires `>=3.13`; `cellpy` supports 3.10–3.13.
  Either raise `cellpy`'s floor to 3.13, or lower `cellpy-core`'s. Decide before wiring
  the dependency.
- **Build backend.** Moving `cellpy` from setuptools+`requirements.txt`+`setup.py` to
  hatchling+uv (matching core) is desirable for tooling parity but is **independent** of
  the integration — do it as its own low-priority PR. Already tracked by existing
  jepegit/cellpy#354 ("update build procedure"). Note `setup.py` carries `package_data`,
  `entry_points`, and `extras_require` that must be translated faithfully.

## Follow-ups (after the first seam PR)

- **Contract tests** asserting `cellpycore.legacy` headers/units equal
  `cellpy.parameters.internal_settings` field-by-field, so the duplicated copies cannot
  silently drift → jepegit/cellpy#378.
- **Port `make_step_table`** into `cellpy-core` (the remaining half of the core),
  **bringing `CellpyLimits` with it** (step-type detection thresholds, not yet copied
  into core) → cellpy/cellpy-core#12.
- Settle the column-header harmonization (`config.Cols` ↔ legacy `Headers*`) → existing
  cellpy/cellpy-core#4 (SPEED-30, header enum structure); see also
  `column-headers-review.md`.

## Recommended sequencing

1. Diff/triage branch 334 → confirmed: **mine, don't merge** (done; recorded above).
2. Resolve the **Python floor** (small, independent).
3. Land the **Data/processing seam** wired to `OldCellpyCellCore` + git dependency.
4. Add **contract tests**.
5. **Build-backend** swap (independent, whenever convenient).
6. Port **`make_step_table`** (+ `CellpyLimits`) into core.

## Tracking

- `cellpy` repo (jepegit/cellpy): GitHub issue
  [#377](https://github.com/jepegit/cellpy/issues/377) — "Prepare cellpy to consume
  cellpy-core (isolate the Data object via a core seam)".
- Blueprint branch: `334-isolate-parts-needed-for-cellpy-core` (do not merge; reference).
- Related core doc: `.issueflows/04-designs-and-guides/column-headers-review.md`.
