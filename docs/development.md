# Development Guide

This document outlines the development practices, standards, and workflows for the cellpy-core library.

## Table of Contents

1. [Code Documentation](#code-documentation)
2. [Branching and Merging Strategy](#branching-and-merging-strategy)
3. [Code Structure and Principles](#code-structure-and-principles)
4. [Development Workflow](#development-workflow)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Quality Standards](#code-quality-standards)

## Code Documentation

### Docstring Format

We use the **Google docstring format** for all Python code documentation. This format provides clear, readable documentation that works well with most documentation generators.

#### Basic Structure

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """Brief description of the function.

    More detailed description if needed. This can span multiple lines
    and should explain the purpose and behavior of the function.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter. Defaults to 10.

    Returns:
        Description of what the function returns.

    Raises:
        ValueError: Description of when this exception is raised.
        TypeError: Description of when this exception is raised.

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
    pass
```

#### Class Documentation

```python
class ExampleClass:
    """Brief description of the class.

    More detailed description of the class purpose and behavior.
    This can include information about the class design, usage patterns,
    and any important implementation details.

    Attributes:
        attribute1: Description of the first attribute.
        attribute2: Description of the second attribute.

    Example:
        >>> obj = ExampleClass("value1", "value2")
        >>> obj.method()
    """

    def __init__(self, param1: str, param2: str):
        """Initialize the ExampleClass.

        Args:
            param1: Description of the first parameter.
            param2: Description of the second parameter.
        """
        self.attribute1 = param1
        self.attribute2 = param2
```

#### Module Documentation

```python
"""Module-level docstring.

This module provides functionality for [description of module purpose].
It contains classes and functions for [specific functionality].

Example:
    Basic usage example here.
"""
```

### Documentation Standards

- **All public functions, classes, and methods must have docstrings**
- **Use type hints for all function parameters and return values**
- **Include examples in docstrings when the functionality is complex**
- **Document all exceptions that functions may raise**
- **Keep docstrings up-to-date with code changes**

## Branching and Merging Strategy

### Branch Structure

We follow the **GitHub Flow** methodology loosely with the following branch structure:

- **`main`**: The primary branch containing production-ready code
- **`nn-add-something*`**: Branch that addresses a particular issue 

Optionally, we can label branches using the following allowed labels
- **`feature/*`**: Feature development branches
- **`bugfix/*`**: Bug fix branches
- **`hotfix/*`**: Critical production fixes
- **`release/*`**: Release preparation branches

### Branch Naming Convention

- **Features**: `feature/description-of-feature`
  - Example: `feature/add-polars-support`
- **Bug fixes**: `bugfix/description-of-bug`
  - Example: `bugfix/fix-memory-leak-in-summarizers`
- **Hotfixes**: `hotfix/description-of-issue`
  - Example: `hotfix/fix-critical-data-corruption`
- **Releases**: `release/version-number`
  - Example: `release/v0.2.0`

### Workflow Process

1. **Create a new branch** from `main` for your work
2. **Make your changes** with clear, atomic commits
3. **Push your branch** to the remote repository
4. **Create a Pull Request** (PR) targeting the `main` branch
5. **Request code review** from team members
6. **Address feedback** and make necessary changes
7. **Merge the PR** once approved and all checks pass

### Commit Message Standards
Use clear, descriptive commit messages.

If you want to impress your fellow developers, you can opt for the
fancy commit message standard:

#### Fancy Commmit Messages

Use clear, descriptive commit messages following this format:

```
type(scope): brief description

Longer description if needed, explaining what and why.
Can span multiple lines.

Fixes #issue-number
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(selectors): add support for custom step type filtering
fix(summarizers): resolve memory leak in large dataset processing
docs(api): update function documentation with examples
```

## Code Structure and Principles

This should be considered as Work-In-Progress and design decissions will be updated as the project matures. For now, use them as a first guide, but feel free to suggest changes.

### Project Architecture

The cellpy-core library follows a modular architecture with clear separation of concerns:

```
src/cellpycore/
├── __init__.py          # Package initialization and public API
├── cell_core.py         # Main CellpyCellCore class
├── selectors.py         # Data selection and filtering functions
├── summarizers.py       # Data summarization and analysis functions
├── units.py            # Unit conversion and handling
└── config.py           # Configuration and constants
```

### Design Principles

#### 1. **Immutability by Design**
- **Selectors and summarizers should NOT modify input data objects**
- Functions should return new data or computed results
- This ensures data integrity and enables safe parallel processing

```python
# ✅ Good: Non-modifying selector
def filter_by_step_type(data: DataFrame, step_type: str) -> DataFrame:
    """Filter data by step type without modifying original data."""
    return data.filter(pl.col("step_type") == step_type)

# ❌ Bad: Modifying selector
def filter_by_step_type(data: DataFrame, step_type: str) -> None:
    """This modifies the input data - avoid this pattern."""
    data.drop_in_place(pl.col("step_type") != step_type)
```

#### 2. **Functional Programming Approach**
- Prefer pure functions that don't have side effects
- Use composition over inheritance where possible
- Make functions stateless and predictable

#### 3. **Type Safety**
- Use type hints for all function signatures
- Leverage TypeVar for generic types
- Use Union types for multiple possible return types

```python
from typing import TypeVar, Union, Optional

DataFrame = TypeVar("DataFrame")  # Generic DataFrame type

def process_data(data: DataFrame) -> Union[DataFrame, None]:
    """Process data with proper type hints."""
    pass
```

#### 4. **Modular Design**
- Each module has a single, well-defined responsibility
- Modules should be loosely coupled
- Clear interfaces between modules

#### 5. **Configuration Management**
- Centralize configuration in `config.py`
- Use constants for magic numbers and strings
- Make configuration easily discoverable and modifiable

### Module Responsibilities

#### `cell_core.py`
- **Main CellpyCellCore class** - the primary interface
- **Data object management** - handles the core data structure
- **Orchestration** - coordinates between selectors and summarizers

#### `selectors.py`
- **Data filtering and selection** functions
- **Step type identification** and classification
- **Data validation** and quality checks
- **Non-modifying operations** only

#### `summarizers.py`
- **Statistical analysis** and summarization
- **Step table generation** and processing
- **Core summary calculations**
- **Non-modifying operations** only

#### `config.py`
- **Constants and configuration** values
- **Header definitions** for data structures
- **Default settings** and parameters

#### `units.py`

Might not be included in `core`, but as an additonal package.

- **Unit conversion** utilities
- **Unit validation** and standardization
- **Measurement system** handling


### Code Organization Patterns

#### 1. **Function Organization**
```python
# Group related functions together
# Use clear, descriptive names
# Keep functions focused on single responsibility (within reason)

```

#### 2. **Error Handling**
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: DataFrame) -> DataFrame:
    """Process data with proper error handling."""
    try:
        # Processing logic
        return result
    except ValueError as e:
        logger.error(f"Value error in data processing: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in data processing: {e}")
        raise
```

#### 3. **Constants and Configuration**
```python
# Define constants at module level
MY_MAGIC_NUMBER = 42

# Use configuration objects for complex settings (could be enums)
class Config:
    """Configuration settings for the module."""
    DEFAULT_METHOD = "explode"
    CAPACITY_MODIFIERS = ["reset"]

# Use the core configuration solution for main configurations.

from .config import Headers

```

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**
2. **Install dependencies**: `uv sync --group dev`
3. **Install pre-commit hooks** (if available)
4. **Run tests** to ensure everything works

It is recommended to use the `uv` project management solution for
adding new dependencies: `uv add something`

More details can be found at [Astral's uv documentation](https://docs.astral.sh/uv/).

### Development Process

1. **Create a feature (issue) branch** from `main`
2. **Write tests "first"** (TDD approach recommended, but use common sense)
3. **Implement the feature** following coding standards
4. **Update documentation** as needed
5. **Run all tests** and ensure they pass
6. **Run linting** and fix any issues
7. **Create a Pull Request**

### Code Review Process

- **All code must be reviewed** before merging
- **At least one approval** required for merging
- **Address all review comments** before merging
- **Keep PRs focused** and reasonably sized

## Testing Guidelines

We are currently using `pytest` as test runner. We have not decided
if we would like implement sandboxed local testing (e.g. with `nox`),
and it might never happen since for example `github actions` also
can check sandboxed tests.

### Test Structure

- **Unit tests** for individual functions
- **Integration tests** for module interactions
- **End-to-end tests** for complete workflows

### Test Naming

```python
def test_function_name_with_valid_input_returns_expected_result():
    """Test that function_name returns expected result with valid input."""
    pass

def test_function_name_with_invalid_input_raises_exception():
    """Test that function_name raises appropriate exception with invalid input."""
    pass
```

### Test Coverage

- **Aim for >90% code coverage**
- **Test edge cases** and error conditions
- **Test with different data types** (Pandas, Polars)

## Code Quality Standards

### Linting and Formatting

- **Use Ruff** for linting and formatting
- **Follow PEP 8** style guidelines
- **Use type hints** throughout the codebase
- **Keep line length** under 88 characters

### Performance Considerations

- **Profile code** for performance bottlenecks
- **Use appropriate data structures** for the task
- **Consider memory usage** for large datasets
- **Optimize critical paths** in the code

### Documentation Requirements

Initial documentation should use markdown format and should live in the docs folder.
Keep in mind that we intend to implement `sphinx` in a not-too-far future.

- **All public APIs** must be documented
- **Examples** should be provided for complex functions
- **Keep documentation** up-to-date with code changes
- **Use clear, concise language**

### Additional tooling

- **AI**: a `.cursor` folder exists where general rules and project specific rules can be put
- **Aliases**: a `.aliases` file exists where general linux aliases can be put and sourced (`source .aliases`)

---

This development guide should be followed by all contributors to ensure consistency and quality across the cellpy-core library. For questions or suggestions about these guidelines, please open an issue or discuss in a Pull Request.
