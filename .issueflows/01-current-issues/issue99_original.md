# Issue #99: Clarify standalone-use docs: nom_cap vs nom_cap_abs naming

Source: https://github.com/cellpy/cellpy-core/issues/99

## Original issue text

## Context

The standalone-use quickstart example is confusing because parameter names differ between step-table and summary helpers:

- `make_core_step_table(..., nom_cap=...)` 
- `add_scaled_summary_columns(..., nom_cap_abs=...)`

Similarly, summary scaling uses `current_conversion_factor` in one place and `specific_converters` in another — the relationship is not obvious from the docs alone.

Source: `SCRATCHPAD.md` (Unclear example section).

## Example from docs (current)

```python
data = core.make_core_step_table(
    core.data,
    nom_cap=my_nom_cap_abs,              # absolute (e.g. Ah), for the per-step C-rate
    ...
)
data = core.add_scaled_summary_columns(
    data,
    nom_cap_abs=my_nom_cap_abs,
    specific_converters={"gravimetric": f_g, "areal": f_a, "absolute": f_abs},
)
```

## Proposal

Pick one approach (docs-only or API alignment):

1. **Docs-only:** Add a short glossary / callout explaining that both args expect absolute capacity in Ah (or document units), and how `current_conversion_factor` vs `specific_converters` relate.
2. **API alignment (breaking):** Rename parameters for consistency across step and summary entry points (needs migration note).

## Selected option

2. **API alignment (breaking):** 

deprecation path + tests updated

## Comments (curated summary)

- **Clarifications / constraints**: `make_core_step_table` is slated to be split into `make_core...` and `add_scaled...` parts (issue #98); the `nom_cap` parameter (whatever its final name) will belong to the `add_scaled...` entry point, so the rename here should target that seam.

_Note: this section is an interpretive summary of the comment thread, not a verbatim dump. Source comments: 1, last comment by @jepegit on 2026-07-05._
