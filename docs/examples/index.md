# Examples

Runnable Jupyter notebooks demonstrating the cellpy-core pipeline end-to-end.
Each example is available both as a rendered page and as a downloadable
notebook you can run yourself.

| Example | Rendered page | Notebook |
|---------|---------------|----------|
| Quickstart on mock data | [Quickstart](quickstart.md) | [`quickstart.ipynb`](quickstart.ipynb) |
| Real cycling data walkthrough | [Walkthrough](real_data_walkthrough.md) | [`real_data_walkthrough.ipynb`](real_data_walkthrough.ipynb) |

## Running the notebooks

From a checkout of the repository:

```bash
uv sync --group docs
uv run jupyter lab docs/examples/
```

The quickstart is fully self-contained (it generates mock data with
`cellpycore.testing.mock_data`). The real-data walkthrough reads the small
vendored parquet fixture `tests/data/cycler_cc_harmonized_raw.parquet`, so it
needs to run from inside the repository.

## Regenerating the rendered pages

The rendered Markdown pages are generated from the notebooks with
[nbconvert](https://nbconvert.readthedocs.io/) and committed alongside them.
After editing a notebook, re-run:

```bash
uv run --group docs jupyter nbconvert --to markdown --execute docs/examples/*.ipynb
```

and commit the updated `.md` files and image directories together with the
notebook.
