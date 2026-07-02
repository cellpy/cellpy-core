# Issue #44 status — Release: tag cellpy-core (and decide PyPI publish)

- [ ] Done

## What has been done

- User added `.github/workflows/release.yml`: on GitHub release publish → ruff + pytest → `uv build` → PyPI publish (trusted publishing via `pypi` environment, `id-token: write`).
- User added a release alias (commit `06831f0`) to trigger releases, modeled on jepegit/issue-flow.
- Release `v0.1.0` was published 2026-07-02, but its CI test job failed on ruff F401 (unused `pytest` import in `tests/test_creation.py`) — PyPI publish never ran.
- Fix landed: PR #53 squash-merged to `main` (`d0204df`). Ruff and pytest (94 passed) green locally.

## Remaining work

- Re-cut the release so the tag points at a fixed commit: either delete and recreate `v0.1.0` (tag + GitHub release) at `d0204df`+, or bump to `0.1.1` with `uv version --bump patch` and publish a fresh release.
- Verify `release.yml` runs green end-to-end and the package lands on PyPI.
- Document the release procedure (version bump via `uv`, tagging convention, alias usage) and the cellpy-side re-pin checklist (replace `@main` git ref with pinned tag / PyPI version) — anchors: `cellpy-core-migration.md` §2/§5.
