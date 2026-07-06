# Issue #100: BDF read/export: decide placement (scripts vs cellpy-io)

Source: https://github.com/cellpy/cellpy-core/issues/100

## Original issue text

## Context

Should BDF format read/export live in cellpy-core or a separate repo (e.g. cellpy-io)?

Interim idea from `SCRATCHPAD.md`: add a `scripts/` folder in cellpy-core for experimental BDF tooling until ownership is decided.

## Questions

- Is BDF I/O in scope for the core engine library, or an I/O/exchange layer?
- Does cellpy-io (or similar) already exist / is planned as the home for format adapters?
- What is the minimum viable script (read only, export only, round-trip)?

## Interim proposal

- Park a prototype under `scripts/` in this repo (not part of the public API).
- Document the open decision and link from ROADMAP or designs-and-guides when resolved.

## Acceptance criteria

- [ ] Decision recorded in `.issueflows/04-designs-and-guides/` (or ROADMAP)
- [ ] If interim script: lives under `scripts/`, not imported by `cellpycore` package

## Comments (curated summary)

- **Additional tasks**:
  - Implement the interim proposal: put the BDF prototype in a subfolder inside `scripts/` so it can be treated as a package.
  - Try adding a `pyproject.toml` inside that subfolder; if it interferes with the root cellpy-core `pyproject.toml`, fall back to PEP 723 inline script metadata instead.
- **Clarifications / constraints**:
  - Decision made: the **interim proposal** was chosen (prototype lives in this repo under `scripts/`, not in a separate cellpy-io repo for now).
  - BDF format specification reference: https://battery-data-alliance.github.io/battery-data-format-ontology/battery-data-format.html

_Note: this section is an interpretive summary of the comment thread, not a verbatim dump. Source comments: 2, last comment by @jepegit on 2026-07-06._
