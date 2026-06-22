# Migrating cellpy onto cellpy-core — local dev setup, parity tests, and the metadata boundary

**Required reading** before doing any cross-repo work between `cellpy` (jepegit/cellpy)
and `cellpy-core` (cellpy/cellpy-core): wiring the dependency, keeping the old library
green while core evolves, and deciding what does (and does not) belong in core.

This is the *practical* companion to the strategy/findings in
[`cellpy-core-integration-into-cellpy.md`](cellpy-core-integration-into-cellpy.md). Read
that one for the seam design and sequencing; read this one for how to actually develop the
two repos together and where the boundary sits.

## 1. Golden rule: branch, don't fork

Do integration work on a **branch** of the existing `cellpy` repo (optionally surfaced as a
`git worktree` for side-by-side editing), **never** in a fresh clone of cellpy. A separate
"cellpy-next" repo recreates the branch-334 divergence problem (136 ahead / 24 behind, a
painful eventual merge) that we explicitly decided to avoid ("mine branch 334, do not
merge it"). A branch keeps history, issues/PRs, tags and CI unified.

```bash
# side-by-side without a second clone:
git -C ../cellpy worktree add ../cellpy-integration 377-core-seam
```

## 2. Local dev wiring (uv path source)

`cellpy` already depends on core via a **git** reference (the release/consumer truth):

```toml
# cellpy/pyproject.toml -> [project.dependencies]
"cellpycore @ git+https://github.com/cellpy/cellpy-core.git@main",
```

For day-to-day development, add a **local editable override** so edits in the sibling
working copy are picked up immediately — no commit/push/re-pin cycle:

```toml
# cellpy/pyproject.toml
[tool.uv.sources]
cellpycore = { path = "../cellpy-core", editable = true }
```

Key properties:

- **Two sources of truth, on purpose.** `[tool.uv.sources]` is **not** written into the
  built wheel metadata. A released/installed `cellpy` still uses the `git+https…@<ref>`
  reference in `[project.dependencies]`; the path source only applies inside this
  workspace. (`[tool.hatch.metadata] allow-direct-references = true` is what permits the
  direct git reference.)
- **`editable = true`** → core is an editable install; since core is pure Python, changes
  are live without reinstall.
- **Relative path** `../cellpy-core` matches the `…/cellpy` + `…/cellpy-core` sibling
  layout.
- **Pin for releases.** Before tagging a `cellpy` release, change `@main` to a specific
  cellpy-core **tag/commit** so the release maps to a known core revision.
- **Ad-hoc equivalents:** `uv add --editable ../cellpy-core` (edits pyproject + lock) or a
  one-off `uv pip install -e ../cellpy-core`.

Python floors already agree (`requires-python = ">=3.13"` in both), so nothing blocks the
wiring.

## 3. Keep old cellpy working: parity tests

The biggest hidden risk of two libraries is **silent drift** in the duplicated
headers/units. Defend it with tests, not vigilance:

- **Contract tests** asserting `cellpycore.legacy` (`HeadersNormal` / `HeadersSummary` /
  `HeadersStepTable` / `CellpyUnits`) equals `cellpy.parameters.internal_settings`
  field-by-field (tracked: jepegit/cellpy#378).
- **Golden fixtures** as a cross-library oracle: cellpy-core already vendors
  `tests/data/arbin_cc_*.parquet` and asserts cellpy's published goldens (103 steps / 18
  cycles / cycle-1 `data_point` 1457). Extend as more of the core is ported.
- Target the legacy bridge `OldCellpyCellCore` for the first integration so cellpy sees the
  headers/units it already expects (the seam is ~5 edit points, not a rewrite).

## 4. The metadata boundary (scaffolding in core; population is opt-in upstream)

**Decision.** cellpy-core may own the **scaffolding and tooling** for test/cell metadata —
schemas/specs (e.g. the `TestMeta` table in
[`docs/data_format_specifications/harmonized_raw.md`](../../docs/data_format_specifications/harmonized_raw.md)),
the compact `RawCols.test_id` grouping key, and helpers for (de)serialization, merging and
conversion. **It does not require that populated metadata be a first-class part of core's
`Data` object.** Whether to attach real metadata to a data object is the **next level's**
call: e.g. `cellpy` v2.0 may add it to its `.data` instance / class / subclass.

**Why.** Core stays lean, fast, and loader-free; metadata richness and policy (which fields,
controlled vocabularies, where it is sourced, how it is persisted) belong to the consumer.
Core provides the *shape and the tools*; the consumer decides the *content and ownership*.

**Current state / anchors.**
- `Data.meta_test_dependent` is today a single scalar (`MockMetaTestDependent`) — see
  `src/cellpycore/cell_core.py:25`. The `cycle_mode` property carries
  `# TODO: v2.0 edit this from scalar to list` (`cell_core.py:113-140`): the scalar→keyed
  move is explicitly a v2.0 concern, not something core forces now.
- The normalized per-test model (compact `raw.test_id` + a `TestMeta` table keyed by
  `test_id`, composite group keys `(test_id, cycle_num, step_num, …)`) is designed in
  [`test-metadata-and-merging.md`](test-metadata-and-merging.md) but **not yet
  implemented** as a class.

**Practical shape of the boundary.**
- *In core (allowed):* `TestMeta`/`CellMeta` schema or dataclass, field definitions,
  (de)serialization, merge helpers, `test_id` plumbing, timestamp/unit conversion utilities.
  These are tooling — usable, but not mandatory to populate.
- *Upstream (opt-in):* the actual per-test metadata values and the decision to hang them off
  a `Data` (sub)class. cellpy v2.0 composes/subclasses to hold them; core does not assume
  they exist on the hot path.
- *Guard:* keep the core summary/step engine working when metadata is absent (mock/empty) —
  it must degrade gracefully, never require populated metadata.

## 5. Sequencing & tracking

Follow the sequencing in
[`cellpy-core-integration-into-cellpy.md`](cellpy-core-integration-into-cellpy.md) §"Recommended
sequencing": resolve Python floor (done) → land the Data/processing seam on
`OldCellpyCellCore` + the dependency wiring above → add contract tests → build-backend
parity → port `make_step_table` (+ `CellpyLimits`).

- cellpy seam issue: jepegit/cellpy#377.
- Contract tests: jepegit/cellpy#378.
- Port `make_step_table` (+ `CellpyLimits`): cellpy/cellpy-core#12.
- Header harmonization: cellpy/cellpy-core#4; see `column-headers-review.md`.
- Timestamp representation (int64 ns internal): cellpy/cellpy-core#32.
