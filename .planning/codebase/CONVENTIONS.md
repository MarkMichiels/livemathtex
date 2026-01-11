# Coding Conventions

**Analysis Date:** 2026-01-10

## Naming Patterns

**Files:**
- `snake_case.py` for all Python modules
- `test_*.py` for test files (alongside source or in tests/)
- `__init__.py` for package initialization
- `conftest.py` for pytest configuration

**Functions:**
- `snake_case` for all functions
- No special prefix for async functions (none used currently)
- Descriptive names: `process_file()`, `evaluate()`, `parse()`

**Variables:**
- `snake_case` for variables
- `UPPER_SNAKE_CASE` for constants (e.g., `GREEK_LETTERS`)
- No underscore prefix for private (Python convention: use `_` prefix if truly private)

**Types:**
- `PascalCase` for classes (e.g., `Evaluator`, `Lexer`, `LivemathConfig`)
- `PascalCase` for dataclasses (e.g., `SymbolEntry`, `LivemathIR`, `ValueWithUnit`)
- `PascalCase` for type aliases (e.g., `FormatType`, `UnitSystem`)

## Code Style

**Formatting:**
- Black 23.0+ with 100 character line length
- Target Python versions: py310, py311, py312
- Config: `[tool.black]` in `pyproject.toml`

**Linting:**
- Ruff 0.1.0+ with select rules: E, F, W, I, UP, B, C4
- Line length: 100 characters
- Config: `[tool.ruff]` in `pyproject.toml`
- Run: `ruff check .`

**Type Checking:**
- mypy 1.0+ for static type checking
- Python version: 3.10
- Warn on return any, unused configs
- Config: `[tool.mypy]` in `pyproject.toml`

## Import Organization

**Order:**
1. Standard library imports (pathlib, time, datetime, typing)
2. Third-party packages (click, sympy, pint, numpy)
3. Local imports (from .parser, from .engine, etc.)

**Grouping:**
- Blank line between standard library and third-party
- Blank line between third-party and local imports
- Alphabetical within each group (enforced by isort)

**Path Aliases:**
- No path aliases (relative imports only)
- Use `from .module import ...` for same package
- Use `from ..parent import ...` for parent package

## Error Handling

**Patterns:**
- Try/catch at calculation level (isolate failures)
- Errors collected in IR.errors list (don't crash)
- Custom error types: `EvaluationError`, `UndefinedVariableError` in `utils/errors.py`
- Error messages rendered in output as red LaTeX: `\color{red}`

**Error Types:**
- Throw on invalid input, undefined variables, unit mismatches
- Log error context before adding to IR (line number, expression)
- Continue processing even if some calculations fail

## Logging

**Framework:**
- Click.echo for normal output
- Click.style for colored output (errors in red)
- No structured logging framework

**Patterns:**
- Console output for CLI feedback
- Stats displayed after processing (symbols, definitions, evaluations, errors)
- No file logging (CLI tool, not a service)

## Comments

**When to Comment:**
- Explain why, not what: "Symbol normalization ensures 100% latex2sympy compatibility"
- Document business logic: "Pint as single source of truth for unit recognition"
- Explain non-obvious algorithms: "Clean IDs (v_{n}) prevent parsing failures"
- Avoid obvious comments: "# Increment counter"

**Docstrings:**
- Required for public functions and classes
- Use Google-style docstrings (or NumPy style)
- Include Args, Returns, Raises sections
- Example: See `core.py:process_file()` docstring

**TODO Comments:**
- Format: `# TODO: description`
- Link to issue if exists: `# TODO: Add import system (issue #123)`
- Examples in code: "TODO: Optimize unit conversion caching"

## Function Design

**Size:**
- Keep functions focused (typically 20-50 lines)
- Extract helpers for complex logic
- One level of abstraction per function

**Parameters:**
- Use dataclasses for complex config (LivemathConfig)
- Max 3-4 parameters, use options object for more
- Type hints required for all parameters

**Return Values:**
- Explicit return statements
- Return tuples for multiple values: `(rendered_output, ir)`
- Type hints required for return types

## Module Design

**Exports:**
- Named exports preferred (no default exports in Python)
- Public API in `__init__.py` (re-export key classes/functions)
- Internal helpers stay private (not exported from `__init__.py`)

**Barrel Files:**
- `__init__.py` re-exports public API
- Keep internal helpers private
- Avoid circular dependencies (use relative imports carefully)

**Module Organization:**
- One class per file typically (e.g., `evaluator.py` has `Evaluator` class)
- Related functions grouped in same module
- Clear separation of concerns (parser/, engine/, render/)

## Type Hints

**Usage:**
- Type hints required for all function parameters and returns
- Use `typing` module for complex types (Optional, List, Dict, Tuple)
- Use `from __future__ import annotations` for forward references (if needed)

**Examples:**
```python
def process_file(
    input_path: str,
    output_path: str = None,
    verbose: bool = False,
) -> LivemathIR:
    ...
```

---

*Convention analysis: 2026-01-10*
*Update when patterns change*

