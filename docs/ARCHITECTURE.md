# Livemathtex - Architecture

## Overview

Livemathtex follows a modular pipeline architecture:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parser    │───▶│   Engine    │───▶│  Renderer   │───▶│   Output    │
│  (Frontend) │    │(Interpreter)│    │ (Compiler)  │    │    (MD)     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Components

### 1. Parser / Frontend

**Responsibility:** Analyze Markdown files and recognize formulas, variables, units.

#### Detection Strategy

- Scan for `:=`, `==`, `=>` patterns
- Error on bare `=` (safety: prevents accidental overwrites)
- Recognize `livemathtex` code fences
- Distinguish static LaTeX (`$...$`) from calculable expressions

#### Grammar Elements

| Element | Example | Description |
|---------|---------|-------------|
| Variables | `m_{rock}`, `α`, `x_1` | LaTeX subscript/superscript, Greek |
| Assignment | `x := 5` | Definition, stored in symbol table |
| Evaluation | `x == expr` | Compute and display numeric result |
| Symbolic | `f'(x) =>` | Symbolic evaluation (differentiation, etc.) |
| Units | `9.81 m/s^2` | Recognized after numbers/variables |
| Functions | `sin`, `cos`, `log`, `sqrt` | Built-in mathematical functions |
| Matrices | `[[1,2];[3,4]]` | Row-separated by `;` |

#### Markdown Preservation

The parser preserves non-calculation content (headings, paragraphs, lists) unchanged. Only calculation nodes are transformed.

---

### 2. Engine / Interpreter

**Responsibility:** Execute calculations, manage symbols, handle units.

#### Symbol Table

```python
symbols = {
    "m": Value(5, unit="kg"),
    "g": Value(9.81, unit="m/s^2"),
    "F": Expression("m * g"),  # lazy evaluation
}
```

#### Evaluation Order

1. Build dependency graph from definitions
2. Topological sort for evaluation order
3. Detect circular references → error
4. Evaluate in order, cache results

#### Unit Calculation

Each quantity stored as: `(base_value_SI, dimensions)`

| Operation | Rule |
|-----------|------|
| Add/Subtract | Dimensions must match |
| Multiply | Dimensions combine |
| Divide | Dimensions subtract |
| Output | Convert to requested unit |

**Example:**
```
F = m * a
  = 5 kg * 2 m/s²
  = 10 kg·m/s²
  = 10 N
```

#### Error Handling

Errors never crash the system. Each evaluation returns `Result<Value, Error>`:

| Error Type | Example |
|------------|---------|
| `UndefinedVariable` | Variable not defined |
| `UnitMismatch` | Adding kg + m |
| `DivisionByZero` | 1/0 |
| `Timeout` | Computation > 5s |
| `CircularDependency` | a := b, b := a |

#### Sandboxing

- No filesystem access from expressions
- No network access
- Whitelisted math functions only
- Timeout per expression (configurable, default 5s)
- Memory limits for matrix operations

---

### 3. Renderer / Output Generator

**Responsibility:** Transform calculated AST to output format.

#### Markdown Output Mode

Input:
```markdown
$d == v \cdot t$
```

Output:
```markdown
$d == v \cdot t = 200\ \text{km}$
```

**Note:** PDF/HTML export is out of scope. Use `pandoc output.md -o output.pdf` on the result.

#### Error Display

```markdown
$F == m \cdot a$ → ⚠️ Error: Undefined variable 'm'
$x = 5$ → ⚠️ Error: Invalid operator '='. Use ':=' or '=='
```

#### Symbolic Results (`=>`)

The `=>` operator triggers symbolic evaluation:

```markdown
$f(x) := x^2 + 2x + 1$
$f'(x) =>$
```

Output: `$f'(x) = 2x + 2$`

---

### 4. CLI Interface

**Responsibility:** Orchestrate pipeline, handle file I/O, watch mode.

#### Commands

```bash
livemathtex <input> [options]

Options:
  -o, --output FILE    Output Markdown file
  -w, --watch          Watch mode, rebuild on change
  --config FILE        Path to config file
  --digits N           Significant figures (default: 4)
  --scientific         Force scientific notation
  --no-symbolic        Disable CAS features
  --timeout N          Max seconds per expression
  -v, --verbose        Verbose output
  -q, --quiet          Only show errors

# For PDF: use external tools on the output
pandoc output.md -o output.pdf
```

#### Configuration

**Precedence (highest to lowest):**
1. Command-line arguments
2. Document directives (`<!-- livemathtex: digits=4 -->`)
3. Local config (`.livemathtex.toml` in document directory)
4. Project config (`pyproject.toml` `[tool.livemathtex]` section)
5. User config (`~/.config/livemathtex/config.toml`)
6. Defaults

**Config file format (TOML):**

```toml
# .livemathtex.toml or pyproject.toml [tool.livemathtex]
digits = 4
scientific = false
timeout = 5
symbolic = true

[units]
system = "SI"  # or "imperial"
```

**Why TOML:**
- Standard for Python tools (pyproject.toml, ruff, black, pytest)
- Human-readable, easy to edit
- Supports comments
- Type-safe (numbers vs strings)

#### Watch Mode

1. Monitor input file for changes (inotify/fswatch)
2. On change: parse → evaluate → render
3. Report timing and errors to console
4. Support incremental recalculation (future optimization)

---

## Technology Choices

### Recommended: Python

| Component | Library |
|-----------|---------|
| Operators | `regex` (`:=`, `==`, `=>` detection) |
| Units | `pint` |
| Numeric | `numpy`, `scipy` |
| Symbolic | `sympy` |
| LaTeX parsing | `latex2sympy2` |
| Math detection | `regex` (built-in) |

**Pros:** Rich ecosystem, rapid development, SymPy for CAS
**Cons:** Distribution (requires Python), slightly slower

**Why Python:** Rich math ecosystem (SymPy, Pint), rapid development, easy distribution via pip.

---

## Module Structure

```
livemathtex/
├── src/
│   └── livemathtex/
│       ├── __init__.py
│       ├── cli.py           # CLI entry point
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── lexer.py     # Tokenization
│       │   ├── grammar.py   # Expression grammar
│       │   └── ast.py       # AST node types
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── evaluator.py # Main evaluation logic
│       │   ├── symbols.py   # Symbol table
│       │   ├── units.py     # Unit handling (pint wrapper)
│       │   └── functions.py # Built-in functions
│       ├── symbolic/
│       │   ├── __init__.py
│       │   └── cas.py       # SymPy integration
│       ├── render/
│       │   ├── __init__.py
│       │   └── markdown.py  # MD output (only output format)
│       └── utils/
│           ├── __init__.py
│           └── errors.py    # Error types
├── tests/
│   ├── test_parser.py
│   ├── test_engine.py
│   ├── test_units.py
│   └── test_integration.py
├── docs/
│   ├── BACKGROUND.md
│   ├── ARCHITECTURE.md
│   ├── USAGE.md
│   ├── ROADMAP.md
│   └── DEPENDENCIES.md
└── examples/
    ├── basic.md
    ├── physics.md
    └── engineering.md
```

---

## Security Considerations

### Sandboxing Strategy

1. **No `eval()` on user input** - Parse to AST, evaluate AST
2. **Whitelist approach** - Only allow known functions
3. **Resource limits** - Timeout, memory caps
4. **No side effects** - Calculations are pure functions

### Safe Functions Whitelist

```python
SAFE_FUNCTIONS = {
    # Basic math
    "sin", "cos", "tan", "asin", "acos", "atan",
    "sinh", "cosh", "tanh",
    "log", "log10", "log2", "exp",
    "sqrt", "abs", "floor", "ceil", "round",
    "min", "max", "sum", "prod",

    # Linear algebra
    "inv", "det", "transpose", "dot", "cross",

    # Symbolic (optional)
    "diff", "integrate", "solve", "simplify",

    # Statistics
    "mean", "std", "var",
}
```

---

## Performance Considerations

### Caching Strategy

- Cache parsed AST per file
- Cache evaluation results per expression
- Invalidate on dependency change
- Full recalculation is acceptable for typical document sizes

### Benchmarks (Target)

| Operation | Target Time |
|-----------|-------------|
| Parse 100-line doc | < 50ms |
| Evaluate 50 expressions | < 200ms |
| Full rebuild with plots | < 2s |
| Watch mode latency | < 500ms |

---

## Future Extensions

**In scope (this repo):**
1. **Import/Include** - Reference other documents
2. **Tables with Calculations** - Spreadsheet-like tables
3. **Conditional Logic** - If/else in expressions
4. **Iteration** - Loops and summations

**Separate projects (build on top of Livemathtex):**
- VS Code Extension (`livemathtex-vscode`)
- Web Playground (`livemathtex-web`)
- GUI with PDF export (`livemathtex-desktop`)

---

## References

- [Pint Documentation](https://pint.readthedocs.io/)
- [SymPy Documentation](https://docs.sympy.org/)
- [latex2sympy2](https://github.com/augustt198/latex2sympy)
