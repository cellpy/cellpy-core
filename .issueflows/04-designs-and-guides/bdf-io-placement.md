# BDF read/export — placement decision

Issue: [#100](https://github.com/cellpy/cellpy-core/issues/100)

## Context

The Battery Data Alliance defines the **Battery Data Format (BDF)**: a set of
standardized, snake_case column notations with fixed units (e.g.
``current_ampere``, ``voltage_volt``, ``cycle_count``,
``cycle_charging_capacity_ah``) and obligations (required / recommended /
optional). Spec:
<https://battery-data-alliance.github.io/battery-data-format-ontology/battery-data-format.html>

cellpy would like to read and export BDF, but file/format IO is explicitly a
non-goal of the cellpy-core engine (see `this-project.md`). The open question
was where BDF tooling should live: inside cellpy-core, or in a dedicated
IO/exchange repo (e.g. a future *cellpy-io*).

## Decision (interim)

- BDF tooling lives **in this repo under `scripts/bdf/`** as an experimental,
  self-contained prototype package (`cellpy_bdf`), with its **own nested
  `pyproject.toml`** so it can be run and tested in isolation via
  `uv run --project scripts/bdf ...`.
- It is **not part of the public API**: nothing in `src/cellpycore` imports
  it, it is excluded from the sdist (`/scripts` in the hatch exclude list) and
  from the wheel (which only packages `src/cellpycore`), and root CI does not
  collect its tests (`testpaths = ["tests"]`).
- The dependency direction is one-way: the prototype imports `cellpycore`
  (for `RawCols` and the timestamp helpers), never the reverse.
- A separate **cellpy-io** repo remains the candidate long-term home for
  format adapters. This placement is deliberately cheap to move.

## Alternatives considered

- **Core module (`cellpycore.io.bdf`)** — rejected: file IO and unit
  conversion are engine non-goals; would grow the public API before the
  format ownership question is settled.
- **Separate repo now (cellpy-io)** — rejected for now: too much ceremony for
  a prototype; revisit once the adapter has stabilized and a second format
  needs a home.
- **PEP 723 single-file scripts** — fallback if the nested `pyproject.toml`
  had interfered with the root `uv` setup. Verified it does not (root
  `uv sync` / `uv lock` / `pytest` / `ruff` unaffected), so the package form
  was kept.

## Revisit criteria

Move the prototype out of `scripts/` (to cellpy-io or a core extra) when any
of these happen: a second exchange format needs the same scaffolding, cellpy
proper wants to depend on BDF export, or the BDF controlled vocabulary
stabilizes enough to freeze a public API around it.
