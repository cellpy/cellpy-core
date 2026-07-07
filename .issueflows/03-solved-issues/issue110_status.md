# Issue #110 — status

- [x] Done

## What's done

- Added `mkdocstrings-python` to the `docs` dependency group (`uv.lock` updated).
- Configured mkdocstrings Python handler in `zensical.toml` (`paths = ["src"]`,
  Google docstring style, nav entry **API reference**).
- Added `docs/api/index.md` and `docs/api/public.md` (`::: cellpycore` with
  explicit `members` matching `cellpycore.__all__`).
- Updated `.readthedocs.yaml` to install `zensical` + `mkdocstrings-python`.
- Updated `zensical-docs.md`, `docs/development/guide.md`, `README.md`,
  `HISTORY.md` `[Unreleased]` bullet.
- Verified: `uv run --group docs zensical build --clean` green (Griffe warnings
  on pre-existing missing annotations only).
- Unit-conversion convenience helpers in `cellpycore.units`:
  `calculate_nom_cap_abs_from_specific`, `calculate_current_conversion_factor`,
  `calculate_specific_conversion_factors` (+ docs in `standalone-use.md`).
- Renamed `specific_converters` → `specific_conversion_factors` on
  `add_scaled_summary_columns` and the units helper; deprecated aliases with
  `DeprecationWarning` (shared `summarizers._resolve_specific_conversion_factors`).
  Internal resolver renamed to `_resolve_specific_conversion_factor`.

## Remaining work

- None. Released as **0.1.5**. Post-merge: run `/iflow-cleanup`.

## Housekeeping

- Issue #99 files moved to `.issueflows/03-solved-issues/` (was marked done,
  PR #107 merged).
