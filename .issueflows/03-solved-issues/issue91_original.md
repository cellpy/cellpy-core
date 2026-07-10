# Issue #91: Release v0.1.4: docs (#90) and cellpy re-pin

Source: https://github.com/cellpy/cellpy-core/issues/91

## Original issue text

## Context

`v0.1.3` (2026-07-04) already ships the merge/update API from #86/#87. One commit on `main` since that tag:

- #90 — Zensical docs migration, Read the Docs config, example notebooks

`cellpy` still pins `cellpycore==0.1.2` in `[project.dependencies]` — needs re-pin after this release.

## Tasks

- [ ] Confirm `main` is green (ruff + pytest)
- [ ] Update changelog / release notes for 0.1.4 (docs + any misc since 0.1.3)
- [ ] Bump version (`uv version --bump patch` → 0.1.4) and commit
- [ ] Cut GitHub release (`release patch` or equivalent) from up-to-date `main`
- [ ] Verify `release.yml` passes and `cellpycore 0.1.4` appears on PyPI
- [ ] cellpy: bump `cellpycore` pin in `pyproject.toml`, refresh `uv.lock`, run seam tests (`tests/test_slim.py`)

## References

- `.issueflows/04-designs-and-guides/release-procedure.md`
- Issue #44 (release pipeline — done)
