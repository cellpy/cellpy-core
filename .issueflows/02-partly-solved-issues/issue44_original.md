# Issue #44: Release: tag cellpy-core (and decide PyPI publish) so cellpy can pin a release ref

Source: https://github.com/cellpy/cellpy-core/issues/44

## Original issue text

End-goal enabler not captured as a roadmap STEP. Today `cellpy` consumes core via `cellpycore @ git+https://github.com/cellpy/cellpy-core.git@main` plus a local editable `[tool.uv.sources]` path (see `cellpy-core-migration.md` Â§2).

## Scope

- Establish a release/tagging convention for cellpy-core so `cellpy` can pin a specific **tag/commit** for releases instead of `@main` (the migration doc's "pin for releases" step).
- Decide whether/when to publish cellpy-core to **PyPI** (the original goal allowed git/editable during development only).
- Document the release procedure (CHANGELOG/versioning via `uv version --bump`) and the cellpy-side re-pin checklist.

Anchors: `cellpy-core-migration.md` Â§2/Â§5, `cellpy-core-integration-into-cellpy.md`.

## Comments (curated summary)

- **Additional tasks**:
  - Model the release flow on [jepegit/issue-flow](https://github.com/jepegit/issue-flow): version bump via `uv`, plus a small script/alias that triggers the release.
  - Verify the newly added `.github/workflows/release.yml` works end-to-end (PyPI publish on tag).
- **Clarifications / constraints**:
  - PyPI publishing is wanted (not just git tags); the user has (probably) already configured the PyPI side and added `.github/workflows/release.yml`.
- **Superseded / retracted**:
  - "I can set up PyPI if you provide instructions" — superseded by the later comment saying the setup (release workflow) is now in place; only verification/instructions-on-gaps remain.

_Note: this section is an interpretive summary of the comment thread, not a verbatim dump. Source comments: 2, last comment by @jepegit on 2026-07-02._
