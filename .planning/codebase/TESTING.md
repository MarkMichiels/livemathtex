# Testing Patterns

**Analysis Date:** 2026-01-10

## Test Framework

**Runner:**
- pytest 7.0+
- Config: `[tool.pytest.ini_options]` in `pyproject.toml`
- Test paths: `tests/` directory
- Options: `-v --cov=livemathtex` (verbose, coverage)

**Assertion Library:**
- pytest built-in assertions (no separate library)
- Standard Python assert statements
- pytest.raises for exception testing

**Run Commands:**
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_examples.py  # Single file
pytest --cov=livemathtex  # Coverage report
pytest -k test_name       # Run tests matching pattern
```

## Test File Organization

**Location:**
- `tests/` directory at project root
- Test files alongside source (not co-located)
- Fixtures in `tests/conftest.py`

**Naming:**
- `test_*.py` for all test files
- `test_examples.py` - Snapshot tests for examples
- `test_pint_backend.py` - Pint unit tests
- `test_unit_recognition.py` - Unit recognition tests

**Structure:**
```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_examples.py         # Example snapshot tests
├── test_pint_backend.py     # Pint backend tests
└── test_unit_recognition.py  # Unit recognition tests
```

## Test Structure

**Suite Organization:**
```python
import pytest
from livemathtex.core import process_text

@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    """Test that processing input.md produces expected output.md."""
    example_dir = examples_dir / example_name
    input_file = example_dir / "input.md"
    expected_output_file = example_dir / "output.md"

    # Read and process
    input_content = input_file.read_text(encoding='utf-8')
    actual_output, ir = process_text(input_content, source=str(input_file))

    # Compare
    expected_output = expected_output_file.read_text(encoding='utf-8')
    normalized_expected = normalize_output(expected_output)
    normalized_actual = normalize_output(actual_output)

    assert normalized_expected == normalized_actual
```

**Patterns:**
- Use `@pytest.mark.parametrize` for testing multiple examples
- Fixtures in `conftest.py` for shared setup (project_root, examples_dir)
- Normalize output before comparison (strip timestamps, whitespace)
- Reset unit registry between tests (`reset_unit_registry()`)

## Mocking

**Framework:**
- pytest built-in mocking (no separate library)
- Use `unittest.mock` if needed (rarely used)

**Patterns:**
- Minimal mocking (most tests use real implementations)
- Reset unit registry between tests to avoid state leakage
- Use fixtures for test data setup

**What to Mock:**
- External file I/O (if testing in isolation)
- Time-dependent operations (if needed)
- Rarely needed: most tests use real file system

**What NOT to Mock:**
- Core calculation logic (test real SymPy/Pint)
- Parser logic (test real regex/parsing)
- Unit conversion (test real Pint registry)

## Fixtures and Factories

**Test Data:**
```python
# In conftest.py
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
```

**Location:**
- Fixtures: `tests/conftest.py`
- Test data: Example files in `examples/` directory
- Factory functions: Inline in test files if simple

## Coverage

**Requirements:**
- No enforced coverage target
- Coverage tracked for awareness
- Focus on critical paths (parser, evaluator, IR)

**Configuration:**
- pytest-cov 4.0+ for coverage reporting
- Coverage for `livemathtex` package
- Config: `--cov=livemathtex` in pytest options

**View Coverage:**
```bash
pytest --cov=livemathtex --cov-report=html
open htmlcov/index.html
```

## Test Types

**Unit Tests:**
- Test single function/class in isolation
- Examples: `test_pint_backend.py`, `test_unit_recognition.py`
- Fast: each test <100ms
- Minimal dependencies

**Integration Tests:**
- Test full pipeline (parse → evaluate → render)
- Examples: `test_examples.py` (snapshot tests)
- Use real file system, real SymPy/Pint
- Reset state between tests

**Snapshot Tests:**
- Compare output against expected files
- Examples: `test_examples.py` (compares `output.md`)
- Normalize output before comparison (timestamps, whitespace)
- Update expected files when behavior changes intentionally

## Common Patterns

**Async Testing:**
- Not applicable (no async code)

**Error Testing:**
```python
def test_undefined_variable():
    """Test that undefined variable raises error."""
    content = "$x ==$"  # x not defined
    output, ir = process_text(content)

    assert len(ir.errors) > 0
    assert any("undefined" in e.message.lower() for e in ir.errors)
```

**Example Testing:**
```python
@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    """Test that example produces expected output."""
    # Uses fixtures from conftest.py
    # Normalizes output for comparison
    # Fails with diff if mismatch
```

**Unit Registry Reset:**
```python
from livemathtex.engine import reset_unit_registry

def test_with_clean_registry():
    """Test with clean unit registry."""
    reset_unit_registry()  # Clear custom units
    # ... test code ...
```

**IR Structure Testing:**
```python
def test_ir_v3_structure(example_name: str, examples_dir: Path) -> None:
    """Verify IR v3.0 has expected structure."""
    _, ir = process_text_v3(input_content, source=str(input_file))

    assert ir.version == "3.0"
    assert 'name' in ir.unit_backend
    assert ir.unit_backend['name'] == 'pint'
    assert isinstance(ir.symbols, dict)
```

**Snapshot Testing:**
- Not used (prefer explicit assertions)
- Output comparison via file diff
- Normalize before comparison (timestamps, whitespace)

---

*Testing analysis: 2026-01-10*
*Update when test patterns change*

