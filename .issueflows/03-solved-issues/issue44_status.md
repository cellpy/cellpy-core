# Issue #44 status — Release: tag cellpy-core (and decide PyPI publish)

- [x] Done

## What has been done

- User added `.github/workflows/release.yml`: on GitHub release publish → ruff + pytest → `uv build` → PyPI publish (trusted publishing via `pypi` environment, `id-token: write`).
- User added a release alias (commit `06831f0`) to trigger releases, modeled on jepegit/issue-flow.
- Release `v0.1.0` was published 2026-07-02, but its CI test job failed on ruff F401 — PyPI publish never ran. Fix landed via PR #53.
- **2026-07-02 (evening): release verified end-to-end.** `v0.1.1` tagged, `release.yml` ran green, and `cellpycore 0.1.1` is live on PyPI. The release/tagging convention works.
- Note: tag `v0.1.1` points at `63066bf`, which **pre-dates** the #45 selector removal (merged to `main` as `2da165e` after the tag). cellpy `master` is compatible with both (it no longer passes `selector=` and works against 0.1.1 and `main`). The next release will include the removal.

## Remaining work

- ~~Document the release procedure~~ — done 2026-07-02:
  `.issueflows/04-designs-and-guides/release-procedure.md` (alias, workflow,
  happy path, failure mode, per-release re-pin checklist).
- ~~Execute the cellpy-side re-pin~~ — done 2026-07-02: cellpy PR
  [jepegit/cellpy#400](https://github.com/jepegit/cellpy/pull/400)
  (branch `core44-pin-cellpycore-release`): `cellpycore>=0.1.1` from PyPI,
  editable `[tool.uv.sources]` override kept, `allow-direct-references`
  removed, `uv.lock` refreshed, seam tests green.
- ~~Merge PR #400~~ — merged 2026-07-02 17:21Z. **Issue fully resolved.**
