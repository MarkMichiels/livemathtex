# Testing Patterns

**Analysis Date:** 2026-05-21

## Test Framework

**Runner:**
- Framework: pytest 7.0+
- Config: `pyproject.toml` under `[tool.pytest.ini_options]`
- Config details:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  addopts = "-v --cov=livemathtex"
  ```

**Assertion Library:**
- pytest built-in assertions
- `pytest.approx()` for floating-point comparison

**Run Commands:**
```bash
# Run all tests with coverage
python3 -m pytest tests/ -v --cov=livemathtex

# Run specific test file
python3 -m pytest tests/test_expression_evaluator.py -v

# Run specific test class
python3 -m pytest tests/test_expression_evaluator.py::TestNumberEvaluation -v

# Run specific test
python3 -m pytest tests/test_expression_evaluator.py::TestNumberEvaluation::test_integer

# Watch mode (requires pytest-watch or manual re-run)
python3 -m pytest tests/ -v --cov=livemathtex --tb=short

# Coverage report
python3 -m pytest tests/ --cov=livemathtex --cov-report=html
```

## Test File Organization

**Location:**
- Co-located in separate `tests/` directory (not inline with source)
- Path: `/home/mark/Repositories/livemathtex/tests/`

**Naming:**
- Test files: `test_<module>.py` pattern
- Test classes: `Test<Feature>` pattern
- Test methods: `test_<behavior>()` pattern

**Structure:**
```
tests/
├── __init__.py
├── conftest.py                          # Shared fixtures
├── test_expression_evaluator.py          # Unit tests for evaluator
├── test_expression_parser.py             # Unit tests for parser
├── test_markdown_parser.py               # Unit tests for markdown parsing
├── test_examples.py                      # Snapshot/integration tests
├── test_calculation_parser.py
├── test_pint_backend.py
├── test_pint_evaluator.py
├── test_expression_tokenizer.py
├── test_clear_v2.py
└── [25+ more test files]
```

Total: 25 test files, ~6,761 lines of test code.

## Test Structure

**Suite Organization:**

Example from `tests/test_expression_evaluator.py`:
```python
"""Tests for the expression evaluator.

This module tests evaluate_expression_tree() which evaluates ExprNode trees
using Pint for unit-aware calculations.

TDD: RED phase - all tests should fail until evaluator is implemented.
"""

import pytest
import pint

from livemathtex.parser.expression_tokenizer import ExpressionTokenizer
from livemathtex.parser.expression_parser import ExpressionParser
from livemathtex.engine.expression_evaluator import (
    evaluate_expression_tree,
    EvaluationError,
)
from livemathtex.engine.pint_backend import get_unit_registry


@pytest.fixture
def ureg():
    """Get unit registry for tests."""
    return get_unit_registry()


def evaluate(latex: str, symbols: dict = None, ureg: pint.UnitRegistry = None):
    """Helper to tokenize, parse, and evaluate a LaTeX expression."""
    if ureg is None:
        ureg = get_unit_registry()
    if symbols is None:
        symbols = {}
    tokens = ExpressionTokenizer(latex).tokenize()
    tree = ExpressionParser(tokens).parse()
    return evaluate_expression_tree(tree, symbols, ureg)


# =============================================================================
# Number Evaluation
# =============================================================================


class TestNumberEvaluation:
    """Test evaluation of numeric literals."""

    def test_integer(self, ureg):
        """Evaluate integer literal."""
        result = evaluate("5", ureg=ureg)
        assert isinstance(result, pint.Quantity)
        assert result.magnitude == 5.0
        assert result.dimensionless

    def test_decimal(self, ureg):
        """Evaluate decimal literal."""
        result = evaluate("3.14", ureg=ureg)
        assert result.magnitude == pytest.approx(3.14)
        assert result.dimensionless
```

**Patterns:**
- Test classes group related tests: `TestNumberEvaluation`, `TestVariableLookup`, `TestBinaryOperations`
- Section headers with equal signs: `# =============================================================================`
- Docstring on every test method explaining what is being tested
- Helper functions (like `evaluate()`) provided at module level for test utilities

**Fixtures:**

From `tests/conftest.py`:
```python
import pytest
from pathlib import Path


# Project paths
@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def examples_dir(project_root: Path) -> Path:
    """Return the examples directory."""
    return project_root / "examples"


@pytest.fixture
def example_dirs(examples_dir: Path) -> list[Path]:
    """Return all example directories that contain input.md files."""
    dirs = []
    for subdir in sorted(examples_dir.iterdir()):
        if subdir.is_dir() and (subdir / "input.md").exists():
            dirs.append(subdir)
    return dirs


# Example data
def get_example_ids() -> list[str]:
    """Get list of example directory names for parametrization."""
    examples_path = Path(__file__).parent.parent / "examples"
    return [
        d.name
        for d in sorted(examples_path.iterdir())
        if d.is_dir() and (d / "input.md").exists()
    ]


EXAMPLE_IDS = get_example_ids()
```

- Function-scoped fixtures (default)
- Fixtures injected as parameters: `def test_integer(self, ureg)`
- Parametrization helpers: `EXAMPLE_IDS` list for parametrized tests

## Mocking

**Framework:** None detected. Tests use real objects or helper functions.

**Patterns:**
- No mock framework (unittest.mock) imported
- Real unit registry: Tests use `get_unit_registry()` to get actual Pint UnitRegistry
- Helper functions create test data: `evaluate()` helper wraps tokenization and parsing
- Fixture factories for complex data

**What to Mock:**
- File I/O: Not mocked in test suite; uses real `examples/` directory
- External APIs: Not tested (no external integrations)
- Unit registry: Created fresh per test via fixture

**What NOT to Mock:**
- Pint UnitRegistry: Always real
- Parser/Tokenizer: Always real (unit testing the full pipeline)
- Math operations: Always real

## Fixtures and Factories

**Test Data:**

From `tests/test_expression_evaluator.py`:
```python
def evaluate(latex: str, symbols: dict = None, ureg: pint.UnitRegistry = None):
    """Helper to tokenize, parse, and evaluate a LaTeX expression."""
    if ureg is None:
        ureg = get_unit_registry()
    if symbols is None:
        symbols = {}
    tokens = ExpressionTokenizer(latex).tokenize()
    tree = ExpressionParser(tokens).parse()
    return evaluate_expression_tree(tree, symbols, ureg)
```

Usage pattern:
```python
def test_simple_variable(self, ureg):
    """Look up simple variable."""
    symbols = {"x": 5.0 * ureg.dimensionless}
    result = evaluate("x", symbols, ureg)
    assert result.magnitude == 5.0
```

**Location:**
- Fixtures in `tests/conftest.py` (global fixtures)
- Test-specific helpers in test file itself (e.g., `evaluate()` helper in test_expression_evaluator.py)
- No external fixture factory files

## Coverage

**Requirements:** Not enforced by CI. Coverage data generated but no minimum threshold.

**View Coverage:**
```bash
# Generate HTML coverage report
python3 -m pytest tests/ --cov=livemathtex --cov-report=html

# View report
open htmlcov/index.html

# Terminal coverage report
python3 -m pytest tests/ --cov=livemathtex --cov-report=term-missing
```

**Current State:** `.coverage` file present, pytest-cov plugin installed in dev dependencies.

## Test Types

**Unit Tests (Primary):**
- Scope: Individual functions and classes in isolation
- Approach: Fast, focused assertions on single behaviors
- Example: `test_integer()` tests only integer literal evaluation
- 95% of test suite
- Path: `tests/test_<module>.py` files
- Examples:
  - `tests/test_expression_evaluator.py`: Tests `evaluate_expression_tree()` with various inputs
  - `tests/test_expression_parser.py`: Tests parsing of LaTeX expressions to AST
  - `tests/test_expression_tokenizer.py`: Tests tokenization of LaTeX math

**Integration Tests:**
- Scope: Multi-module workflows
- Approach: Exercise full pipelines (tokenize → parse → evaluate)
- Example: `evaluate()` helper in test_expression_evaluator.py chains multiple modules
- In: Specific test files or marked with classes
- Examples:
  - `tests/test_markdown_parser.py`: Tests markdown detection + LaTeX parsing
  - `tests/test_calculation_parser.py`: Tests full calculation parsing

**Snapshot Tests:**
- Framework: Manual (no pytest-snapshot plugin)
- Approach: Compare full output against expected file
- Test: `test_example_snapshot()` in `tests/test_examples.py`
- Triggers: Parametrized over example directories
- Mechanism:
  ```python
  @pytest.mark.parametrize("example_name", EXAMPLE_IDS)
  def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
      """
      Test that processing input.md produces the expected output.md.

      This is a snapshot test: the output must match exactly (after normalization).
      If the behavior should change, update output.md to reflect the new expected output.
      """
      example_dir = examples_dir / example_name
      input_file = example_dir / "input.md"
      expected_output_file = example_dir / "output.md"

      if not expected_output_file.exists():
          pytest.skip(f"No output.md found for {example_name}")

      reset_unit_registry()
      # ... process and compare
  ```
- Normalization applied to handle timestamps:
  ```python
  def normalize_output(text: str) -> str:
      """
      Normalize output for comparison.

      Handles:
      - Trailing whitespace
      - Timestamp lines (they change on each run)
      - Line ending normalization
      """
      lines = []
      for line in text.split('\n'):
          # Skip timestamp meta line (changes on each run)
          if '<!-- livemathtex-meta -->' in line:
              continue
          # Strip trailing whitespace
          lines.append(line.rstrip())

      # Remove trailing empty lines
      while lines and not lines[-1]:
          lines.pop()

      return '\n'.join(lines)
  ```

**E2E Tests:**
- Not explicitly present
- Closest: `test_example_snapshot()` tests full document processing pipeline
- Parametrized over 40+ example directories in `examples/`

## Common Patterns

**Async Testing:**
- Not used (no async code in project)

**Error Testing:**

Pattern with `pytest.raises()`:
```python
def test_undefined_variable(self, ureg):
    """Look up undefined variable raises EvaluationError."""
    with pytest.raises(EvaluationError):
        evaluate("undefined_var", ureg=ureg)
```

From `tests/test_expression_parser.py`:
```python
def test_missing_closing_paren(self):
    """Missing closing paren raises ParseError."""
    with pytest.raises(ParseError):
        parse("(1 + 2")
```

**Floating-Point Testing:**
```python
def test_decimal(self, ureg):
    """Evaluate decimal literal."""
    result = evaluate("3.14", ureg=ureg)
    assert result.magnitude == pytest.approx(3.14)  # Fuzzy comparison
    assert result.dimensionless
```

**Parametrized Tests:**

From `tests/test_examples.py`:
```python
EXAMPLE_IDS = get_example_ids()  # List of example directory names

@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    """Test each example directory."""
    # One test per example
```

**Cleanup/Setup:**

From `tests/test_examples.py`:
```python
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    # ... setup
    reset_unit_registry()  # Clean state before test
    # ... test
```

**Class-Based vs Function-Based:**
- Preferred: Class-based for logical grouping
- Used for: Feature grouping (TestNumberEvaluation, TestBinaryOperations)
- Benefits: Organize related tests, share fixtures via method parameters

## Test Coverage Gaps

Based on exploration, areas with substantial test coverage:
- Expression parsing and evaluation: 95% of tests focus here
- Markdown/LaTeX parsing: Well covered
- Pint backend integration: Well covered

Areas with less emphasis:
- CLI functionality: Tests via integration tests, less isolated CLI testing
- Error paths: Basic coverage, edge cases may lack tests
- Configuration system: Likely tested but not examined in detail

---

*Testing analysis: 2026-05-21*
