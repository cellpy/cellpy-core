# Issue #121 — plan

## Goal

Bring [`docs/development/guide.md`](../../docs/development/guide.md) in line with the
current `cellpycore` codebase and the authoritative cellpy 2 architecture in the
sibling [`architecture-plan`](https://github.com/cellpy/architecture-plan) repo — so
contributors see correct module layout, boundaries, branching, and design principles.

## Constraints

- **Docs-only** — no source-code changes in this issue.
- **Primary target** is `docs/development/guide.md`; keep other docs edits minimal
  (cross-links only where the guide points readers elsewhere).
- **architecture-plan is external** — cite it and summarize cellpy-core's role; do not
  copy the full plan set into cellpy-core docs.
- Match tone/structure of existing published docs ([`docs/index.md`](../../docs/index.md),
  [`user-guide/standalone-use.md`](../../user-guide/standalone-use.md)).
- Branch naming and issue workflow must match
  [`.issueflows/04-designs-and-guides/this-project.md`](../04-designs-and-guides/this-project.md)
  and [`docs/development/issue-workflow.md`](../../docs/development/issue-workflow.md).

### Prior art

- [`docs/development/guide.md`](../../docs/development/guide.md) — current dev guide;
  **stale**: flat `selectors.py`/`units.py` tree, `feature/*` branches, pandas+polars
  parity framing, "units might not be in core".
- [`docs/index.md`](../../docs/index.md) + [`user-guide/standalone-use.md`](../../user-guide/standalone-use.md) —
  **accurate** public-facing architecture summary (polars-native, schema-injected,
  `Data` pipeline).
- [`docs/development/design-notes.md`](../../docs/development/design-notes.md) — early
  SPEED notes; also stale (root `selectors`, metadata "out of core") — **out of scope**
  unless we add a one-line "superseded by guide" note at top.
- [`.issueflows/04-designs-and-guides/this-project.md`](../04-designs-and-guides/this-project.md) —
  agent brief with correct entry points, conventions, test commands.
- [`.issueflows/04-designs-and-guides/cellpy-core-migration.md`](../04-designs-and-guides/cellpy-core-migration.md) —
  cross-repo boundary, metadata scaffolding, parity tests.
- [`architecture-plan/cellpy2-architecture-plan.md`](../../../architecture-plan/cellpy2-architecture-plan.md) —
  authoritative cellpy 2 layering (engine vs app), design patterns, seam rules.
- [`architecture-plan/README.md`](../../../architecture-plan/README.md) — where plans live.
- [`src/cellpycore/__init__.py`](../../src/cellpycore/__init__.py) — curated public API.
- None found in `00-tools/` (toolbox empty).

## Approach

### 1. Gap audit (already done)

| Area | guide.md says | reality / architecture-plan |
|------|---------------|----------------------------|
| Package tree | 6 flat modules incl. root `selectors.py`, `units.py` | 24 files: `extractors`, `summarizers`, `config`, `cell_core`, `merge`, `metadata/`, `units/`, `legacy/`, `testing/` |
| Engine role | Generic modular lib | **Compute engine** in two-package cellpy 2; plain values cross seam; no loaders/IO/config |
| Data model | `DataFrame` examples | `Data` container + injected `Schema` (`RawCols`/`StepCols`/`CycleCols`); polars-native |
| Legacy | Not mentioned | `OldCellpyCellCore` + `legacy/` bridge (pandas, old headers); not public slim API |
| Branching | `feature/*`, `bugfix/*`, `nn-add-something*` | `<N>-<short-slug>` per issue-flow; squash merge on GitHub |
| Units | "might not be in core" | `cellpycore.units` ships as optional `[units]` extra |
| Testing | "Pandas, Polars" equally | Polars-native engine; pandas only via legacy bridge / fixtures |
| Architecture ref | None | `architecture-plan` sibling + `.issueflows/04-designs-and-guides/` |

### 2. Rewrite guide sections (surgical, not full replace)

Keep good existing content (Google docstrings, ruff/pre-commit, Zensical, test naming).

**Replace / add:**

1. **New § "cellpy-core in the cellpy 2 architecture"** (after TOC or before Code Structure)
   - One paragraph: engine vs app layer (from architecture-plan §1).
   - Non-goals: instrument loaders, file persistence, config, plotting.
   - Link: architecture-plan README + `cellpy-core-migration.md`.
   - ASCII or mermaid mini-diagram of seam (optional, keep small).

2. **Replace "Project Architecture" tree** with actual layout:

   ```
   src/cellpycore/
   ├── cell_core.py      # Data, CellpyCellCore, OldCellpyCellCore
   ├── config.py         # Schema, RawCols, StepCols, CycleCols
   ├── summarizers.py    # make_step_table, make_summary, add_step_c_rate
   ├── extractors.py     # step/cycle extraction helpers
   ├── merge.py          # merge_data, update_data
   ├── metadata/         # models + io scaffolding (population opt-in upstream)
   ├── units/            # optional extra: spec + converters
   ├── legacy/           # bridge-only: headers, mapping, selectors
   └── testing/          # mock_data for tests/examples
   ```

3. **Replace "Module Responsibilities"** — map each module to real duties; note
   `legacy/selectors.py` is bridge-only; per-step stat column stems are fixed engine
   contract (issue #70).

4. **Update Design Principles** — align with architecture-plan §4 subset relevant to core:
   - immutable-by-convention frames (engines mutate `Data` slots, not input frames in place)
   - functional core (pure helpers in extractors/summarizers where possible)
   - schema injection (no hardcoded column names in engine hot path)
   - metadata graceful degradation
   - drop misleading generic `DataFrame` filter examples or retarget to polars + `Data`

5. **Fix Branching and Merging Strategy** — primary convention `<N>-<short-slug>`;
   link `docs/development/issue-workflow.md`; squash merges; Conventional Commits kept.

6. **Add "Related documentation"** footer — links to `this-project.md` equivalents
   (user guide, specs, API, issue-flow, architecture-plan).

### 3. Optional tiny touch-ups (only if natural)

- `docs/index.md` — no change expected (already accurate).
- `docs/development/design-notes.md` — add 2-line banner: historical SPEED draft;
  see development guide + architecture-plan for current truth. **Defer unless user wants.**

### 4. Ordering

Edit guide.md top-to-bottom in one PR-sized pass; verify internal links and TOC anchors.

## Files to touch

| File | Change |
|------|--------|
| [`docs/development/guide.md`](../../docs/development/guide.md) | Main rewrite per Approach §2 |
| [`docs/development/design-notes.md`](../../docs/development/design-notes.md) | Optional superseded banner (2 lines) |

## Test strategy

Docs-only — no pytest changes.

Manual verification:

```bash
uv run --group docs zensical build   # if available; else spot-check markdown links
```

Confirm:

- Module tree matches `src/cellpycore/` listing.
- Branch naming matches issue-flow docs.
- architecture-plan links use GitHub URLs (RTD won't host sibling repo).
- TOC anchors still valid after section adds/renames.

## Open questions

1. **design-notes.md** — add superseded banner, or leave untouched? *(Recommend: add
   short banner — low cost, stops agents reading stale structure.)*
2. **architecture-plan links** — GitHub `cellpy/architecture-plan` URLs OK, or prefer
   relative paths for local workspace checkout only? *(Recommend: GitHub URLs primary +
   note "sibling checkout in cellpy-workspace" for local dev.)*
