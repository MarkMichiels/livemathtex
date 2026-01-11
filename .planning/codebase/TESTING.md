# Testing Patterns

**Analysis Date:** 2026-01-11

## Test Framework

**Runner:**
- pytest >=7.0
- Config: `pyproject.toml` [tool.pytest.ini_options]

**Assertion Library:**
- pytest built-in assertions
- Standard Python `assert` statements

**Run Commands:**
```bash
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest tests/test_examples.py    # Single file
pytest --cov=livemathtex         # Coverage report
pytest -k "test_name"            # Run specific test
```

## Test File Organization

**Location:**
- `tests/` directory (separate from source)

**Naming:**
- `test_*.py` for test files
- `test_*` for test functions

**Structure:**
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_examples.py         # Snapshot tests (14,748 bytes)
├── test_pint_backend.py     # Unit backend tests (10,211 bytes)
└── test_unit_recognition.py # Unit recognition tests (9,500 bytes)
```

## Test Structure

**Suite Organization:**
```python
"""Docstring explaining test module purpose."""

import pytest
from pathlib import Path

from livemathtex.core import process_text, process_text_v3

@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    """
    Test docstring explaining what this test verifies.
    """
    # arrange
    example_dir = examples_dir / example_name
    input_file = example_dir / "input.md"

    # act
    output, ir = process_text(input_content)

    # assert
    assert normalize_output(output) == normalize_output(expected)
```

**Patterns:**
- Descriptive test function names
- Module docstrings explaining test purpose
- Arrange/Act/Assert structure (implicit)
- Parametrized tests for multiple examples

## Fixtures

**Shared Fixtures:**
- `conftest.py` for pytest fixtures
- `examples_dir` fixture for example paths

**Example:**
```python
# conftest.py
@pytest.fixture
def examples_dir() -> Path:
    return Path(__file__).parent.parent / "examples"
```

## Test Types

**Snapshot Tests (`test_examples.py`):**
- Process input.md, compare against output.md
- Each example directory is a test case
- Normalization handles timestamps and whitespace
- Critical regression safety net

**Unit Tests (`test_pint_backend.py`, `test_unit_recognition.py`):**
- Test individual functions in isolation
- Test unit parsing, conversion, recognition
- Test edge cases and error handling

**Pattern:**
```python
@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    """Snapshot test for example directory."""
    # Reset unit registry to ensure clean state
    reset_unit_registry()

    # Load and process
    input_content = (example_dir / "input.md").read_text()
    output, ir = process_text(input_content)

    # Compare with expected
    expected = (example_dir / "output.md").read_text()
    assert normalize_output(output) == normalize_output(expected)
```

## Coverage

**Requirements:**
- Coverage tracked via pytest-cov
- No enforced coverage target
- Focus on critical paths (evaluator, pint_backend)

**Configuration:**
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=livemathtex"
```

**View Coverage:**
```bash
pytest --cov=livemathtex --cov-report=html
open htmlcov/index.html
```

## Common Patterns

**Unit Registry Reset:**
```python
from livemathtex.engine import reset_unit_registry

def test_something():
    reset_unit_registry()  # Clean state between tests
    # test code
```

**Output Normalization:**
```python
def normalize_output(text: str) -> str:
    """Normalize output for comparison."""
    lines = []
    for line in text.split('\n'):
        if '<!-- livemathtex-meta -->' in line:
            continue  # Skip timestamps
        lines.append(line.rstrip())
    return '\n'.join(lines)
```

**Diff Generation:**
```python
def diff_strings(expected: str, actual: str) -> str:
    """Generate unified diff for debugging."""
    return '\n'.join(difflib.unified_diff(
        expected.split('\n'),
        actual.split('\n'),
        fromfile='expected',
        tofile='actual'
    ))
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("unit,expected", [
    ("kg", True),
    ("m/s", True),
    ("invalid", False),
])
def test_is_pint_unit(unit: str, expected: bool) -> None:
    assert is_pint_unit(unit) == expected
```

---

*Testing analysis: 2026-01-11*
*Update when test patterns change*
