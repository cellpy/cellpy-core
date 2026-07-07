# Documentation stack: Zensical on Read the Docs

**Context.** The repo's loose markdown docs were restructured into a proper
site. `development.md` once said "we intend to implement sphinx"; that
intention is superseded by this decision.

**Decision.** Docs are built with [Zensical](https://zensical.org) (the
Material-for-MkDocs successor) and hosted on Read the Docs.

- Config: `zensical.toml` at the repo root (nav, theme, markdown extensions).
- Hosting: `.readthedocs.yaml` uses `build.jobs` (`pip install zensical` →
  `zensical build --clean` → copy `site/` to `$READTHEDOCS_OUTPUT/html/`).
  The RTD build needs **only** zensical — no project deps.
- Local preview: `uv run --group docs zensical serve`.
- **API reference:** autodoc from Google-style docstrings via the
  [mkdocstrings](https://mkdocstrings.github.io) plugin (`docs/api/`, configured
  in `zensical.toml`). RTD installs `zensical` + `mkdocstrings-python`; source is
  parsed from `src/` via Griffe (no runtime project deps required on RTD).
- Structure: `docs/{index,getting-started,changelog}.md`, `user-guide/`,
  `examples/`, `specifications/` (was `data_format_specifications/`),
  `development/`. `changelog.md` and `development/roadmap.md` are thin
  `--8<--` snippet includes of root `HISTORY.md` / `ROADMAP.md` (single
  source of truth stays at the root; `pymdownx.snippets` has
  `base_path = ["."]`).

**Notebooks.** Zensical does not render `.ipynb` (it copies them verbatim).
Example notebooks under `docs/examples/` are therefore executed and converted
to committed markdown pages (plus `*_files/` plot PNGs) with nbconvert:

```bash
uv run --group docs jupyter nbconvert --to notebook --execute --inplace docs/examples/*.ipynb
uv run --group docs jupyter nbconvert --to markdown docs/examples/*.ipynb
```

Re-run and commit the outputs whenever a notebook changes. The `.ipynb` files
stay in the nav-adjacent docs tree as downloadable sources. Ruff lints and
formats notebooks too (`ruff format docs/examples/*.ipynb`).

**Alternatives considered.** Sphinx (heavier, reST-leaning, docs were already
markdown); MkDocs + mkdocs-jupyter (Zensical does not support MkDocs plugins,
and the team wanted Zensical); converting notebooks at RTD build time (adds
jupyter+project deps to the RTD build for little gain — committed rendered
pages keep the RTD build trivially `pip install zensical`).
