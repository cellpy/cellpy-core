# Issue #100 — plan: BDF read/export placement (interim `scripts/` prototype)

## Goal

Record the placement decision (interim: BDF tooling lives in this repo under
`scripts/`, not in a separate cellpy-io repo) and land a minimal BDF
export/read prototype as a self-contained package under `scripts/bdf/`, never
imported by the `cellpycore` package.

## Constraints

- Decision already made in the issue comments: **interim proposal** chosen;
  prototype goes in a subfolder of `scripts/` treated as a package. Try a
  nested `pyproject.toml`; if it interferes with the root
  `pyproject.toml` / `uv` setup, fall back to PEP 723 inline script metadata.
- Acceptance criteria: decision recorded in
  `.issueflows/04-designs-and-guides/` (or ROADMAP); interim code lives under
  `scripts/`, **not imported by** the `cellpycore` package.
- BDF spec reference:
  <https://battery-data-alliance.github.io/battery-data-format-ontology/battery-data-format.html>
  (snake_case column notations with units, e.g. `current_ampere`,
  `cycle_count`, `cycle_charging_capacity_ah`; obligations
  required/recommended/optional; converters must not renumber cycles).
- Core non-goals hold (`this-project.md`): no file IO and no unit conversion
  in the engine itself — that is exactly why this lives in `scripts/`.
- Repo config already cooperates: `/scripts` excluded from sdist, wheel builds
  only `src/cellpycore`, pytest `testpaths = ["tests"]` (root CI will not
  collect prototype tests). Ruff lints `scripts/` — keep it clean.

### Prior art

- `cellpycore.config.RawCols` — authoritative harmonized-raw column names
  (mirrors `docs/specifications/harmonized-raw.md`); the mapping table must
  key off these attributes, not hard-coded strings. Reuse.
- `cellpycore.testing.mock_data` — mock raw frames for the round-trip test.
  Reuse.
- `cellpycore/metadata/io.py` (`to_dict` / `to_json`) — only existing
  export-style helpers; different domain (metadata), coexist.
- Toolbox `.issueflows/00-tools/` empty; graph report has no BDF nodes.
- No `scripts/` folder exists yet — created fresh by this issue.

## Approach

1. **Decision doc** — new
   `.issueflows/04-designs-and-guides/bdf-io-placement.md`: context, the
   decision (interim `scripts/bdf/` prototype; cellpy-io remains the candidate
   long-term home), alternatives considered (core module, separate repo now),
   revisit criteria, link to issue #100 and the BDF spec.
2. **ROADMAP** — one line under the relevant section linking the decision doc;
   remove/annotate the stale BDF entry in `SCRATCHPAD.md`.
3. **Prototype package `scripts/bdf/`** (own nested `pyproject.toml`, project
   name `cellpy-bdf`, deps: `polars`, `pyarrow`, `cellpycore`):
   - `src/cellpy_bdf/mapping.py` — declarative mapping table harmonized-raw
     attribute -> BDF notation (e.g. `current` -> `current_ampere`,
     `potential` -> `voltage_volt`, `cycle_num` -> `cycle_count`,
     `step_num` -> `step_count`, `test_time` -> `test_time_second`,
     per-cycle-reset capacities/energies -> `cycle_*_ah` / `cycle_*_wh`),
     resolved against an injected `Schema` (native default).
   - `src/cellpy_bdf/export.py` — `export_bdf(frame, path, *, schema=None,
     conversion_factors=None)`: rename + select per mapping, apply by-value
     conversion factors (default 1.0, engine convention), write parquet
     (and csv via suffix).
   - `src/cellpy_bdf/read.py` — `read_bdf(path, *, schema=None)`: inverse
     rename back to harmonized-raw names, return polars frame usable by
     `Data.from_raw_frame`.
   - `tests/test_roundtrip.py` — mock-data round-trip: harmonized frame ->
     BDF parquet -> back, frame equality on mapped columns.
   - Package is standalone: **not** a uv workspace member, no imports from
     `src/cellpycore` into it (only the reverse: it imports `cellpycore`).
4. **Nested-pyproject verification** (the comment's open point) — after adding
   the folder, verify root tooling is undisturbed: `uv sync`, `uv run pytest`,
   `uv lock --check` (or diff), `uv run ruff check`. If interference shows up,
   collapse the prototype to PEP 723 single-file scripts
   (`scripts/bdf/export_bdf.py` with `# /// script` metadata) and note that in
   the decision doc.

## Files to touch

- `.issueflows/04-designs-and-guides/bdf-io-placement.md` — new decision doc.
- `ROADMAP.md` — link to the decision doc.
- `SCRATCHPAD.md` — mark BDF idea as resolved by issue #100.
- `scripts/bdf/pyproject.toml` — nested prototype project.
- `scripts/bdf/README.md` — how to run (`uv run --project scripts/bdf ...`),
  prototype status, spec link.
- `scripts/bdf/src/cellpy_bdf/{__init__.py,mapping.py,export.py,read.py}` —
  prototype code.
- `scripts/bdf/tests/test_roundtrip.py` — round-trip test (run via
  `uv run --project scripts/bdf pytest tests`, not root CI).
- `.issueflows/01-current-issues/issue100_status.md` — status tracking.

## Test strategy

- Root suite untouched and green: `uv run pytest`; lint `uv run ruff check`
  and `uv run ruff format --check` (CI commands).
- Prototype: `uv run --project scripts/bdf pytest tests` for the round-trip
  test; plus a manual end-to-end run exporting mock data and reading it back.
- Explicit nested-pyproject interference check: `uv sync` + `uv lock` diff at
  repo root after adding `scripts/bdf/pyproject.toml`.

## Open questions

1. **MVP scope** — issue asks read-only / export-only / round-trip.
   Recommendation: **round-trip** (export + read), since the round-trip test
   is what validates the mapping in both directions and costs little extra.
2. **Container format** — BDF terms are column notations; recommend parquet as
   primary output with csv as a convenience (by file suffix). OK?
3. **Units** — BDF requires SI-ish units (A, V, Ah, Wh, s); core is
   unit-agnostic. Recommendation: caller passes by-value conversion factors
   (default 1.0) mirroring the engine convention — no pint on the hot path.
4. **cellpycore dependency direction** — prototype imports `cellpycore` (for
   `RawCols` / mock data). Acceptance only forbids the reverse. Confirm OK.
5. **CI** — keep prototype tests out of CI for now (it is explicitly
   experimental)? Recommendation: yes, revisit when placement is final.
