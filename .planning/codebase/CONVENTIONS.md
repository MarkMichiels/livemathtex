# Coding Conventions

**Analysis Date:** 2026-01-11

## Naming Patterns

**Files:**
- snake_case.py for all Python modules
- UPPERCASE.md for important docs (README, ARCHITECTURE, ROADMAP)
- lowercase.md for other documentation

**Functions:**
- snake_case for all functions
- Prefix with `_` for private/internal functions (`_populate_ir_symbols`, `_compute`)
- No special prefix for async functions

**Variables:**
- snake_case for variables
- UPPER_SNAKE_CASE for constants (if any)
- No underscore prefix for class attributes

**Classes:**
- PascalCase for class names
- Dataclasses for schema types (SymbolEntry, LivemathIR)

**Types:**
- PascalCase for type aliases
- No I prefix for interfaces

## Code Style

**Formatting:**
- Black with line-length=100 (configured in `pyproject.toml`)
- Target Python versions: 3.10, 3.11, 3.12

**Linting:**
- Ruff with line-length=100
- Rules: E, F, W, I, UP, B, C4

**Type Hints:**
- Type hints used for function signatures
- Optional for internal variables
- mypy for type checking

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports (sympy, pint, click, etc.)
3. Local imports (from .parser, from .engine)
4. Type imports

**Patterns:**
- Relative imports within package (`from .core import process_file`)
- Explicit imports preferred over star imports

## Error Handling

**Patterns:**
- Try/catch at calculation level, continue processing
- Errors collected in IR for inspection
- Error messages displayed inline with `\color{red}`
- CLI exits with code 1 on fatal errors

**Error Types:**
- Standard Python exceptions
- Custom error classes in `src/livemathtex/utils/errors.py`

## Logging

**Framework:**
- click.echo for CLI output
- Rich for styled terminal output (colors, progress)

**Patterns:**
- Status messages via click.echo
- Styled output for success/error states
- No logging to files (stdout/stderr only)

## Comments

**When to Comment:**
- Docstrings for all public functions and classes
- Inline comments for complex logic
- Version notes in module docstrings

**Docstrings:**
- Triple-quoted strings
- Google-style format (Args, Returns, Raises)
- Used for functions, classes, modules

**Example:**
```python
def process_file(
    input_path: str,
    output_path: str = None,
) -> LivemathIR:
    """
    Main pipeline: Read -> Parse -> Build IR -> Evaluate -> Render -> Write

    Args:
        input_path: Path to input markdown file
        output_path: Path to output markdown file

    Returns:
        The processed LivemathIR containing all symbol values
    """
```

## Function Design

**Size:**
- Large functions in evaluator.py and pint_backend.py (due to complex logic)
- Helper functions extracted for repeated patterns

**Parameters:**
- Type hints for all parameters
- Optional parameters with defaults
- Config objects for complex options

**Return Values:**
- Explicit return types
- Tuple returns for multi-value (rendered_output, ir)

## Module Design

**Exports:**
- `__init__.py` for package exports
- Named exports preferred

**Package Structure:**
- One concept per directory (parser, engine, render, ir)
- `__init__.py` re-exports public API

---

*Convention analysis: 2026-01-11*
*Update when patterns change*
