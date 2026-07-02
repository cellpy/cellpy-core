# Release procedure — tagging, PyPI publish, and the cellpy re-pin checklist

**Context.** cellpy-core is published to **PyPI as `cellpycore`** so consumers (cellpy)
can pin releases instead of tracking `@main`. Verified end-to-end 2026-07-02:
`v0.1.1` tag → `release.yml` green → `cellpycore 0.1.1` on PyPI (issue #44).

## The moving parts

- **Version** lives in `pyproject.toml` (`project.version`), bumped with
  `uv version --bump <patch|minor|major>`.
- **`release` shell alias** (`.aliases`, source it into your shell) cuts a GitHub
  release whose tag always matches the *committed* version:
  - `release` — tag the already-committed version (e.g. after `/iflow-close bump`).
  - `release patch|minor|major` — bump → commit (`v<x.y.z>` message) → push →
    `gh release create v<x.y.z> --generate-notes`, one consistent step.
  - Guards: refuses on dirty tree, uncommitted version change, or pre-existing tag
    (local or origin).
- **`.github/workflows/release.yml`** fires on GitHub *release published*:
  `uv sync` → `ruff check src/ tests/` → `pytest` → `uv build` →
  PyPI **trusted publishing** (`pypi` environment, `id-token: write` — no API token
  stored in the repo).

## Cutting a release (happy path)

```bash
# from main, clean tree, after the PRs you want in the release are merged
git switch main && git pull --ff-only
release patch          # or minor / major
# then watch: gh run watch  (release.yml: test job must pass before publish runs)
```

Failure mode seen once (v0.1.0): ruff failure in the test job blocks publish — the
GitHub release/tag exists but PyPI never gets the version. Fix the tree, then cut a
**new** patch release (tags are never reused; the alias enforces this).

## cellpy-side re-pin checklist (per release)

`cellpy/pyproject.toml` has two sources of truth, on purpose
(see `cellpy-core-migration.md` §2):

1. `[project.dependencies]` — the **release/consumer truth**. Point it at PyPI:
   `"cellpycore>=0.1.1"` (or an exact `==` pin before a cellpy release).
2. `[tool.uv.sources] cellpycore = { path = "../cellpy-core", editable = true }` —
   the **local-dev override**; keep it, it never ships in the wheel.

Steps after each cellpy-core release:

- [ ] Update the `cellpycore` spec in cellpy's `[project.dependencies]`.
- [ ] `uv lock` (or `uv sync`) in cellpy to refresh `uv.lock`.
- [ ] Run cellpy's seam tests (`pytest tests/test_slim.py`) — with the editable
      override temporarily disabled if you want to test the *published* package.
- [ ] Before tagging a cellpy release: pin an exact cellpy-core version so the
      release maps to a known core revision.

**Gotcha (v0.1.1):** the tag was cut *before* PR #57 merged, so PyPI 0.1.1 still
contains the removed selector pair. Version-to-feature mapping is only guaranteed
when releases are cut from up-to-date `main` — release *after* merging, not before.

**Links.** Issue #44; `cellpy-core-migration.md` §2/§5; jepegit/issue-flow (pattern
source for the alias + workflow).
