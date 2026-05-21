# Coding Conventions

**Analysis Date:** 2026-05-21

## Naming Patterns

**Files:**
- Snake case: `expression_parser.py`, `pint_backend.py`, `calculation_parser.py`
- Test files: `test_<module>.py` pattern (e.g., `test_expression_evaluator.py`)
- Module grouping: Organized by functional domain (parser, engine, ir, render, utils)

**Functions:**
- Snake case: `evaluate_expression_tree()`, `get_unit_registry()`, `clear_text()`
- Private functions: Leading underscore `_eval_node()`, `_lookup_variable()`, `_clear_text_regex()`
- Helper functions: Lower-level utilities prefixed with underscore `_normalize_variable_name()`, `_format_unit_for_prose()`

**Variables:**
- Snake case: `symbols`, `ureg`, `token_stream`, `expression_tree`
- Single letters acceptable in math contexts: `x`, `y`, `m`, `a` (but discouraged outside math)
- Descriptive names preferred: `current_unit` not `cu`, `target_unit` not `tu`

**Types:**
- Pascal case for classes: `ExpressionTokenizer`, `BinaryOpNode`, `VariableNode`
- Dataclass nodes: `ExprNode`, `NumberNode`, `FracNode`, `UnitAttachNode`, `IndexNode`
- Exception classes: Pascal case with Error/Exception suffix: `ParserError`, `EvaluationError`, `UndefinedVariableError`, `UnitConversionWarning`

**Constants:**
- All caps with underscores: `MATH_CONSTANTS`, `MATH_BLOCK_RE`, `OPERATOR_RE`, `CODE_BLOCK_RE`, `EXAMPLE_IDS`

## Code Style

**Formatting:**
- Tool: Black (line length 100)
- Target versions: Python 3.10, 3.11, 3.12 (from `pyproject.toml`)
- From `pyproject.toml`:
  ```toml
  [tool.black]
  line-length = 100
  target-version = ["py310", "py311", "py312"]
  ```

**Linting:**
- Tool: Ruff
- Line length: 100
- Selected rules: E, F, W, I, UP, B, C4
- From `pyproject.toml`:
  ```toml
  [tool.ruff]
  line-length = 100
  select = ["E", "F", "W", "I", "UP", "B", "C4"]
  ```

**Editor Configuration:**
- Unix line endings (LF, not CRLF)
- 4-space indentation for Python
- UTF-8 charset
- No final newline (from `.editorconfig`):
  ```
  [*]
  end_of_line = lf
  insert_final_newline = false
  trim_trailing_whitespace = true

  [*.py]
  indent_style = space
  indent_size = 4
  ```

## Import Organization

**Order:**
1. Standard library: `import re`, `import math`, `from pathlib import Path`
2. Third-party: `import pint`, `import pytest`, `from click import ...`
3. Local relative: `from ..parser.expression_parser import ...`, `from .pint_backend import ...`

**Path Aliases:**
- No import aliases configured. Full relative imports used: `from livemathtex.parser.expression_parser import ExpressionParser`
- Local imports: `from ..config import LivemathConfig`

**Pattern Examples:**
From `src/livemathtex/core.py`:
```python
import re
import time
from datetime import datetime
from pathlib import Path

from .config import LivemathConfig
from .engine.evaluator import Evaluator
from .ir import IRBuilder, LivemathIR, SymbolEntry, ValueWithUnit
from .ir.schema import FormulaInfo, LivemathIRV3, SymbolEntryV3
from .parser.lexer import Lexer
from .parser.models import MathBlock
from .parser.reference_parser import extract_references, restore_references
from .render.markdown import MarkdownRenderer
```

## Error Handling

**Patterns:**
- Custom exception hierarchy in `src/livemathtex/utils/errors.py`:
  ```python
  class LiveMathTexError(Exception):
      """Base exception for livemathtex."""
      pass

  class ParserError(LiveMathTexError):
      """Error during parsing."""
      pass

  class EvaluationError(LiveMathTexError):
      """Error during evaluation."""
      pass

  class UndefinedVariableError(EvaluationError):
      """Reference to an undefined variable."""
      pass

  class UnitConversionWarning(Exception):
      """Warning for unit conversion failures (not calculation errors)."""
      def __init__(self, message: str, current_unit: str, target_unit: str, si_value: str):
          super().__init__(message)
          self.current_unit = current_unit
          self.target_unit = target_unit
          self.si_value = si_value
  ```

- Raise exceptions for errors: `raise EvaluationError(f"Undefined variable: {name}")`
- Use try/except for specific recovery: See `src/livemathtex/cli.py` for file I/O error handling
- Dimension checking with Pint: `pint.DimensionalityError` for unit incompatibility

## Logging

**Framework:** No structured logging framework detected. Uses `click.echo()` for CLI output.

**Patterns:**
- CLI feedback: `click.echo(f"✓ Processed {input_file}")`
- Verbose mode: `-v`/`--verbose` flags (passed to config system)
- Statistics output: `click.echo(f"  Symbols: {stats.get('symbols', 0)}")`
- No debug logging framework; relies on inline prints or pytest verbose mode

## Comments

**When to Comment:**
- Module-level docstrings: Always present, explain purpose
- Function-level docstrings: Always present with Args, Returns, Raises sections
- Inline comments: Explain WHY, not WHAT. Examples from codebase:

From `src/livemathtex/parser/lexer.py`:
```python
# Regex for finding math blocks: $...$ or $$...$$
# AND optionally an HTML comment immediately following it on the same line.
#
# Supported comment formats:
# - <!-- [\frac{m}{s}] -->                    → unit conversion (LaTeX notation)
# - <!-- value:vel -->                        → value lookup
```

From `src/livemathtex/engine/expression_evaluator.py`:
```python
# Mathematical constants - mapped to their values
# The tokenizer produces '\pi' for Greek pi, and 'e' for Euler's number
# Note: 'e' alone is treated as Euler's number; use subscript (e_1) for variables
MATH_CONSTANTS = {
    r"\pi": math.pi,
    "\\pi": math.pi,
    "e": math.e,  # Euler's number (standalone 'e')
}
```

**Docstring Style:**
- Google/NumPy hybrid style with sections: Summary, Args, Returns, Raises, Examples
- Single line summary, blank line, then detailed description
- Include type hints in docstring or rely on Python type annotations

Example from `src/livemathtex/engine/expression_evaluator.py`:
```python
def evaluate_expression_tree(
    node: ExprNode,
    symbols: dict[str, pint.Quantity],
    ureg: pint.UnitRegistry = None,
) -> pint.Quantity:
    """
    Evaluate an expression tree using Pint for unit-aware calculations.

    Walks the ExprNode tree from the parser and evaluates it directly
    with Pint.

    Args:
        node: Root node of expression tree (from ExpressionParser)
        symbols: Dict mapping variable names to Pint Quantities
        ureg: Pint UnitRegistry (uses global if not provided)

    Returns:
        Pint Quantity with evaluated result

    Raises:
        EvaluationError: If variable not found or evaluation fails
        pint.DimensionalityError: If units are incompatible

    Examples:
        >>> ureg = get_unit_registry()
        >>> symbols = {'m': 10 * ureg.kg, 'a': 2 * ureg('m/s^2')}
        >>> tokens = ExpressionTokenizer(r"m \\cdot a").tokenize()
        >>> tree = ExpressionParser(tokens).parse()
        >>> result = evaluate_expression_tree(tree, symbols, ureg)
        >>> # result is 20 kg⋅m/s² (20 N)
    """
```

## Function Design

**Size:** Functions average 10-50 lines. Longer functions (200+ lines) are for complex pipelines like `process_text_v3()` with multiple phases.

**Parameters:**
- Positional for required args: `def evaluate(latex: str, symbols: dict = None, ureg: pint.UnitRegistry = None)`
- Type hints always present: `def evaluate_expression_tree(node: ExprNode, symbols: dict[str, pint.Quantity], ureg: pint.UnitRegistry = None) -> pint.Quantity`
- Default arguments for optional values: `ureg: pint.UnitRegistry = None`

**Return Values:**
- Explicit return statements: `return _eval_node(node, symbols, ureg)`
- Tuples for multiple returns: `def _clear_text_regex(content: str) -> tuple[str, int]` returns (cleared_content, count)
- Type hints on return: Always specified

## Module Design

**Exports:**
- `__init__.py` files export main classes: `src/livemathtex/ir/__init__.py` exports `IRBuilder`, `LivemathIR`
- Submodule re-exports: `from .schema import CustomUnitEntry, LivemathIRV3, SymbolEntryV3`

**Barrel Files:**
- Used selectively: `src/livemathtex/ir/__init__.py` re-exports public API
- Direct imports preferred over barrel imports in tests

**File Organization:**
- Classes in own files or grouped by responsibility: `expression_parser.py` contains multiple node types (NumberNode, VariableNode, BinaryOpNode, etc.)
- Utilities grouped: `utils/errors.py` contains exception hierarchy
- No single "utils.py" dumping ground

---

*Convention analysis: 2026-05-21*
