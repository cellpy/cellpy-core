# Issue #91 plan — Release v0.1.4 + retroactive HISTORY backfill

## Goal

Correct `HISTORY.md` so shipped work is attributed to the right versions (everything
currently under `[Unreleased]` → **`[0.1.3]`**, dated 2026-07-04), add **`[0.1.4]`**
with **only** the Zensical / Read the Docs documentation work (#90), then cut the
`v0.1.4` release and re-pin `cellpy` off the stale `cellpycore==0.1.2` pin.

## Constraints

- **Version attribution (user):** Only the Zensical documentation migration belongs in
  `0.1.4`. No code/API bullets in the 0.1.4 section.
- **No PyPI re-release of 0.1.3** — backfill is changelog-only; `v0.1.3` on PyPI is
  already correct for code content.
- **Single source of truth:** Root [`HISTORY.md`](../../HISTORY.md) is included into the
  docs site via [`docs/changelog.md`](../../docs/changelog.md) (`--8<--` snippet); edit
  `HISTORY.md` only.
- **Release ritual:** Follow
  [`.issueflows/04-designs-and-guides/release-procedure.md`](../04-designs-and-guides/release-procedure.md)
  — bump committed on branch, tag from clean `main` after merge (or user runs `release`
  alias post-merge).
- **cellpy boundary:** Re-pin lives in `jepegit/cellpy` (separate branch/PR); keep
  editable `[tool.uv.sources]` path override unchanged per migration guide.

### Prior art

- [`release-procedure.md`](../04-designs-and-guides/release-procedure.md) — bump, `release`
  alias, `release.yml`, cellpy re-pin checklist.
- [`zensical-docs.md`](../04-designs-and-guides/zensical-docs.md) — what #90 landed
  (structure, RTD build, notebook → markdown pipeline).
- [`iflow-history-update`](../../.cursor/skills/iflow-history-update/SKILL.md) — Keep a
  Changelog promote pattern (`[Unreleased]` → `[x.y.z] - date` + fresh empty
  `[Unreleased]`).
- Issue #56 close — prior patch release that promoted `[Unreleased]` to `[0.1.2]` at
  `/iflow-close` time.
- **Toolbox:** none (`00-tools/` index empty).
- **Grep:** no release/changelog helper scripts; `.aliases` `release()` reads version from
  `pyproject.toml` and calls `gh release create`.

## Approach

### 1. Retroactive `[0.1.3]` section (changelog debt)

Move the **entire** current `[Unreleased]` bullet list into a new section:

```markdown
## [0.1.3] - 2026-07-04
```

(Use the actual `v0.1.3` tag date — 2026-07-04.)

**Add missing bullets** that shipped between `v0.1.2` and `v0.1.3` but were never
written to `HISTORY.md`:

| Change | Ref | Notes |
|--------|-----|-------|
| Merge/update e2e coverage | #89 | Golden-style tests for `merge_data` / `update_data` pipeline |
| README doc links use absolute GitHub URLs (PyPI-safe) | #62 / #63 | Small docs fix in the same release window |

**Do not add** #88 (Cursor Cloud `AGENTS.md` blurb) — agent/dev doc, not a user-facing
release note unless you explicitly want it.

**Optional tidy while editing:** align issue refs where HISTORY already mentions work
(e.g. pre-commit is #84 issue / #85 PR — keep `#84` or note both; merge is #86 issue /
#87 PR — current `#86` is fine).

Leave a fresh empty:

```markdown
## [Unreleased]

```

above `[0.1.4]` (added in step 2).

### 2. `[0.1.4]` section (this release)

Under `[Unreleased]`, add **one** consolidated bullet for #90 (paraphrase from
[`zensical-docs.md`](../04-designs-and-guides/zensical-docs.md)):

- Migrate documentation to **Zensical** with **Read the Docs** hosting
  (`.readthedocs.yaml`, `zensical.toml`, `docs` group in `pyproject.toml`).
- Restructure docs tree (`getting-started`, `user-guide/`, `specifications/`,
  `examples/`, `development/`); `changelog.md` and `development/roadmap.md` snippet-include
  root `HISTORY.md` / `ROADMAP.md`.
- Add executable example notebooks (committed markdown + plot outputs under
  `docs/examples/`). (#90)

Then **promote** for release (during `/iflow-close` with bump):

```markdown
## [0.1.4] - <release-date>
```

(empty `[Unreleased]` above it again).

### 3. Version bump + release (cellpy-core)

On branch `91-release-v0-1-4`:

1. Preflight: `uv run ruff check`, `uv run pytest` (matches `release.yml`).
2. Commit HISTORY backfill + `[0.1.4]` unreleased bullet (can be one commit or two —
   prefer **one PR** with clear commit message).
3. `/iflow-close bump patch` → `0.1.4`, promote `[Unreleased]` → `[0.1.4]`, open PR.
4. After merge to `main`: user runs `release` (or `release patch` if version not yet
   committed — follow alias guards) → verify `release.yml` green → confirm
   `cellpycore 0.1.4` on PyPI.

Current state: `pyproject.toml` is `0.1.3`; `v0.1.3` tag exists; one commit since tag
(`b5f088a` #90 docs only) — aligns with 0.1.4 scope.

### 4. cellpy re-pin (follow-up in sibling repo)

On a `cellpy` branch (e.g. `core91-pin-cellpycore-0-1-4`):

- `[project.dependencies]`: `cellpycore==0.1.2` → `cellpycore==0.1.4` (or `>=0.1.4` if
  you prefer minimum pin — match #400 style: exact `==` before cellpy release).
- `uv lock` / `uv sync` in `cellpy`.
- `uv run pytest tests/test_slim.py` (and optionally parity tests).
- Open PR on `jepegit/cellpy`; reference cellpy-core #91.

Can land same day as core release but is a **separate PR** (different repo).

## Files to touch

| Path | Change |
|------|--------|
| [`HISTORY.md`](../../HISTORY.md) | Promote `[Unreleased]` → `[0.1.3]`; add missing #89/#63 bullets; add #90 under unreleased then promote to `[0.1.4]` at close |
| [`pyproject.toml`](../../pyproject.toml) | `0.1.3` → `0.1.4` at `/iflow-close bump patch` |
| [`uv.lock`](../../uv.lock) | Refresh if bump touches lock (usually unchanged for patch) |
| `.issueflows/01-current-issues/issue91_status.md` | Progress + done checkbox at close |
| `cellpy/pyproject.toml` + `cellpy/uv.lock` | Re-pin (separate repo, separate PR) |

**No code changes** under `src/cellpycore/` for this issue.

## Test strategy

**cellpy-core (before PR):**

```bash
uv run ruff check src/ tests/
uv run ruff format --check
uv run pytest
```

Release CI repeats the same. No new tests — changelog/release only.

**cellpy (re-pin PR):**

```bash
cd ../cellpy && uv lock && uv run pytest tests/test_slim.py
```

## Open questions

1. **cellpy pin style:** exact `cellpycore==0.1.4` vs `>=0.1.4`? Recommend `==0.1.4`
   to mirror #400 until the next cellpy release.
2. **Include #88 in 0.1.3 HISTORY?** Plan default: **no** (skip).
3. **Split PRs?** Recommend single cellpy-core PR (HISTORY backfill + 0.1.4 notes +
   bump); cellpy re-pin as sibling PR after PyPI publish.

---

**Ready for `/iflow-start` after you Accept.** Revise/Abort if you want different pin
style or to include #88.
