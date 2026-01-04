# Livemathtex - Architecture

## Overview

Livemathtex follows a modular pipeline architecture:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parser    │───▶│   Engine    │───▶│  Renderer   │───▶│   Output    │
│  (Frontend) │    │(Interpreter)│    │ (Compiler)  │    │  (MD/PDF)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    Plot     │
                   │   Module    │
                   └─────────────┘
```

---

## Components

### 1. Parser / Frontend

**Responsibility:** Analyze Markdown files and recognize formulas, variables, units.

#### Detection Strategy

- Scan for `:=`, `=`, `=?` patterns
- Recognize `livemathtex` code fences
- Distinguish static LaTeX (`$...$`) from calculable expressions
- `=?` is unambiguous signal for evaluation

#### Grammar Elements

| Element | Example | Description |
|---------|---------|-------------|
| Variables | `m_{rock}`, `α`, `x_1` | LaTeX subscript/superscript, Greek |
| Assignment | `x := 5` | Definition, stored in symbol table |
| Evaluation | `x =` | Compute and display numeric result |
| Symbolic | `x =>` | Symbolic evaluation or highlight |
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
$d = v \cdot t$
```

Output:
```markdown
$d = v \cdot t = 200\ \text{km}$
```

#### LaTeX/PDF Output Mode

- Wrap expressions in `align*` environments
- Use `\coloneqq` for `:=` definitions
- Include generated plots as `\includegraphics`
- Professional typography

#### Error Display

```markdown
$F = m \cdot a = \textcolor{red}{\text{Error: Undefined variable } m}$
```

#### Result Highlighting

Using `=>` syntax to mark important results:

```markdown
$\text{Final Answer} = 42 =>$
```

Renders with visual emphasis (boxed, bold, or icon).

---

### 4. Plot Module

**Responsibility:** Generate graphs from function definitions.

#### Input Syntax

```markdown
```plot
title: "Parabola"
y = x^2 - 4x + 5
x = -2..6
grid: true
```
```

#### Implementation

- Use matplotlib/plotly for rendering
- Sample function at N points
- Respect units for axis labels
- Output PNG/SVG embedded in document

#### Features

- 2D line plots
- Multiple series
- Automatic scaling
- Legend support
- Future: 3D plots, bar charts

---

### 5. CLI Interface

**Responsibility:** Orchestrate pipeline, handle file I/O, watch mode.

#### Commands

```bash
livemathtex <input> [options]

Options:
  -o, --output FILE    Output file (md, pdf, html, tex)
  -w, --watch          Watch mode, rebuild on change
  --digits N           Significant figures (default: 4)
  --scientific         Force scientific notation
  --no-symbolic        Disable CAS features
  --timeout N          Max seconds per expression
  -v, --verbose        Verbose output
  -q, --quiet          Only show errors
```

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
| Parser | `lark` or `pyparsing` |
| Units | `pint` |
| Numeric | `numpy`, `scipy` |
| Symbolic | `sympy` |
| Plotting | `matplotlib` |
| LaTeX parsing | `latex2sympy2` |
| Markdown | `markdown-it-py` or `mistune` |
| PDF | `pandoc` (external) or `weasyprint` |

**Pros:** Rich ecosystem, rapid development, SymPy for CAS
**Cons:** Distribution (requires Python), slightly slower

### Alternative: Rust

| Component | Library |
|-----------|---------|
| Parser | `pest` or `nom` |
| Units | `uom` or custom |
| Numeric | `nalgebra` |
| Symbolic | Limited (SymEngine FFI) |
| Plotting | `plotters` |
| WASM | Native support |

**Pros:** Fast, single binary, WASM for web demo
**Cons:** Harder CAS integration, longer development

### Recommendation

**Start with Python** for rapid prototyping and rich math ecosystem. Consider Rust rewrite for performance-critical parts or web deployment later.

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
│       │   ├── markdown.py  # MD output
│       │   ├── latex.py     # LaTeX output
│       │   └── html.py      # HTML output
│       ├── plot/
│       │   ├── __init__.py
│       │   └── plotter.py   # Graph generation
│       └── utils/
│           ├── __init__.py
│           └── errors.py    # Error types
├── tests/
│   ├── test_parser.py
│   ├── test_engine.py
│   ├── test_units.py
│   └── test_integration.py
├── docs/
│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   ├── UX.md
│   └── SYNTAX.md
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

1. **VS Code Extension** - Live preview pane
2. **Web Playground** - WASM-compiled demo
3. **Jupyter Kernel** - Use in notebooks
4. **Import/Include** - Reference other documents
5. **Tables with Calculations** - Spreadsheet-like tables
6. **Conditional Logic** - If/else in expressions
7. **Iteration** - Loops and summations
8. **Custom Themes** - Output styling options

---

## References

- [Pint Documentation](https://pint.readthedocs.io/)
- [SymPy Documentation](https://docs.sympy.org/)
- [Lark Parser](https://lark-parser.readthedocs.io/)
- [latex2sympy2](https://github.com/augustt198/latex2sympy)
