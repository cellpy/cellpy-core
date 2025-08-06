# cellpy-core

## Installing

only available on <https://github.com/cellpy/cellpy-core>

## Developing

This project uses `uv` as the package manager and build tool. `uv` is a fast Python package installer and resolver, written in Rust.

### Prerequisites

1. Install `uv`:

```bash
pip install uv
```

### Development Workflow

1. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate     # On Windows
```

2. Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

3. Adding new dependencies:

```bash
# Add a new package
uv add <package-name>

# Add a new development package
uv add --dev <package-name>
```

4. Updating dependencies:

```bash
# Update all packages
uv sync
```

5. Running tests:

```bash
pytest
```

### Common Commands

- List installed packages: `uv pip list`
- Remove a package: `uv remove <package-name>`
- Show package info: `uv pip show <package-name>`
- Export requirements: `uv pip freeze > requirements.txt`

For more information about `uv`, visit the [official documentation](https://github.com/astral-sh/uv).
