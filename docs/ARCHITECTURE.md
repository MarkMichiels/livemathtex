# LiveMathTeX - Architecture

## Overview

LiveMathTeX follows a modular pipeline architecture with an **Intermediate Representation (IR)** layer for clean symbol management and debugging:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parser    │───▶│ IR Builder  │───▶│   Engine    │───▶│  Renderer   │───▶│   Output    │
│  (Lexer)    │    │ (Normalize) │    │ (Evaluator) │    │ (Markdown)  │    │    (MD)     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                         │
                         ▼
                   ┌─────────────┐
                   │  IR JSON    │  (--verbose)
                   │  (Debug)    │
                   └─────────────┘
```

### Intermediate Representation (IR)

The IR layer (inspired by [Cortex-JS MathJSON](https://cortexjs.io/math-json/)) provides:

1. **Symbol Normalization** - Clean mapping between LaTeX (`\Delta T_h`) and internal names (`Delta_T_h`)
2. **Debugging** - Write IR to JSON with `--verbose` flag
3. **Traceability** - Track all calculations and their results
4. **Import System** - Load symbols from other Markdown files via their IR JSON

```json
{
  "symbols": {
    "Delta_T_h": {
      "mapping": {
        "latex_original": "\\Delta T_h",
        "latex_display": "\\Delta_{T_h}",
        "internal_name": "Delta_T_h"
      },
      "value": 17.92,
      "unit": "K"
    }
  }
}
```

### Import System (Future)

The IR JSON enables importing symbols from other Markdown files without modifying them:

```mermaid
graph LR
    subgraph library [Library Files]
        L1[constants.md] --> L1J[constants.lmt.json]
        L2[formulas.md] --> L2J[formulas.lmt.json]
    end

    subgraph calc [Calculation File]
        C[calculation.md]
    end

    L1J --> C
    L2J --> C
    C --> OUT[output.md]

    style L1 fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style L2 fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style L1J fill:#f39c12,stroke:#c87f0a,color:#fff
    style L2J fill:#f39c12,stroke:#c87f0a,color:#fff
    style C fill:#7cb342,stroke:#558b2f,color:#fff
    style OUT fill:#7cb342,stroke:#558b2f,color:#fff
```

**Workflow:**

1. **Create library Markdown** - Define reusable constants/functions:
   ```markdown
   <!-- constants.md -->
   $g := 9.81$
   $c := 299792458$
   $\pi := 3.14159265359$
   ```

2. **Process library** - Generate IR JSON:
   ```bash
   livemathtex process constants.md --verbose
   # Creates: constants.lmt.json with all symbol values
   ```

3. **Import in calculation** - Use directive to load symbols:
   ```markdown
   <!-- calculation.md -->
   <!-- livemathtex: import constants.lmt.json -->

   $h := 100$
   $t := \sqrt{\frac{2h}{g}} ==$   <!-- g comes from constants -->
   ```

4. **Process calculation** - Symbols are pre-loaded:
   ```bash
   livemathtex process calculation.md -o output.md
   # g, c, π are available from imported JSON
   ```

**Key Benefits:**

| Benefit | Description |
|---------|-------------|
| **Source = Markdown** | Library files are readable, editable Markdown |
| **No modification needed** | Import uses IR output, original stays unchanged |
| **Composable** | Chain multiple imports, build complex calculations |
| **Cacheable** | Re-process library only when source changes |
| **Intermediate files** | Create helper Markdown files just for their IR |

**Example: Engineering Library**

```
libs/
├── physical_constants.md    → physical_constants.lmt.json
├── material_properties.md   → material_properties.lmt.json
└── common_formulas.md       → common_formulas.lmt.json

projects/
└── heat_exchanger.md        # Imports all three libraries
```

```markdown
<!-- heat_exchanger.md -->
<!-- livemathtex: import ../libs/physical_constants.lmt.json -->
<!-- livemathtex: import ../libs/material_properties.lmt.json -->

## Heat Exchanger Design
$Q := m \cdot c_p \cdot \Delta T ==$   <!-- c_p from material_properties -->
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
| Evaluation | `x ==` | Show value of defined variable |
| Combined | `y := x + 1 ==` | Define AND show result |
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
$d := v \cdot t ==$
```

Output:
```markdown
$d := v \cdot t == 200\ \text{km}$
```

**Note:** PDF/HTML export is out of scope. Use `pandoc output.md -o output.pdf` on the result.

#### Error Display

```markdown
$F ==$                    → ⚠️ Error: Undefined variable 'F'
$x = 5$                   → ⚠️ Error: Invalid operator '='. Use ':=' or '=='
$wrong := m + L ==$       → ⚠️ Error: Cannot add kg + m (if units mismatch)
```

#### Symbolic Results (`=>`)

The `=>` operator triggers symbolic evaluation:

```markdown
$f(x) := x^2 + 2x + 1$
$f'(x) =>$
```

Output: `$f'(x) => 2x + 2$`

---

### 4. CLI Interface

**Responsibility:** Orchestrate pipeline, handle file I/O, debugging output.

#### Commands

```bash
# Process a file
livemathtex process <input> [options]

Options:
  -o, --output FILE    Output Markdown file
  -v, --verbose        Write IR to JSON file for debugging
  --ir-output FILE     Custom path for IR JSON (default: input.lmt.json)

# Inspect an IR JSON file
livemathtex inspect <ir_file>

# Examples
livemathtex process input.md                      # In-place processing
livemathtex process input.md -o output.md         # Separate output
livemathtex process input.md --verbose            # Write debug IR
livemathtex inspect input.lmt.json                # View symbols and results

# For PDF: use external tools on the output
pandoc output.md -o output.pdf
```

#### IR Debug Output (`--verbose`)

When using `--verbose`, livemathtex writes a JSON file containing:

- **symbols**: All defined variables with their values and LaTeX mappings
- **blocks**: Each calculation block with input/output LaTeX
- **errors**: List of any errors encountered
- **stats**: Timing and operation counts

```bash
$ livemathtex process engineering.md --verbose
✓ Processed engineering.md
  Definitions (:=): 26
  Evaluations (==): 16
  Symbolic (=>):    0
  Errors: 0
  Duration: 0.50s
  IR written to: engineering.lmt.json
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
| Units | `sympy.physics.units` |
| Numeric | `numpy` |
| Symbolic | `sympy` |
| LaTeX parsing | `latex2sympy2` (our fork) |
| Math detection | `regex` (built-in) |

**Pros:** Rich ecosystem, rapid development, SymPy for CAS
**Cons:** Distribution (requires Python), slightly slower

**Why Python:** Rich math ecosystem (SymPy), rapid development, easy distribution via pip.

**Why SymPy units:** Simpler integration than Pint - units are SymPy expressions, already using SymPy for symbolic math.

---

## Module Structure

```
livemathtex/
├── src/
│   └── livemathtex/
│       ├── __init__.py
│       ├── cli.py           # CLI entry point
│       ├── core.py          # Main pipeline orchestration
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── lexer.py     # Markdown/LaTeX tokenization
│       │   └── models.py    # AST node types (Document, MathBlock, etc.)
│       ├── ir/              # NEW: Intermediate Representation
│       │   ├── __init__.py
│       │   ├── schema.py    # IR dataclasses (LivemathIR, SymbolEntry, etc.)
│       │   ├── normalize.py # Symbol normalization (LaTeX <-> internal)
│       │   └── builder.py   # Build IR from parsed AST
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── evaluator.py # Main evaluation logic + IR integration
│       │   └── symbols.py   # Symbol table
│       ├── render/
│       │   ├── __init__.py
│       │   └── markdown.py  # MD output (only output format)
│       └── utils/
│           ├── __init__.py
│           └── errors.py    # Error types
├── tests/
│   ├── test_parser.py
│   ├── test_engine.py
│   └── test_integration.py
├── docs/
│   ├── BACKGROUND.md
│   ├── ARCHITECTURE.md
│   ├── USAGE.md
│   ├── ROADMAP.md
│   └── DEPENDENCIES.md
└── examples/
    ├── simple/
    │   ├── input.md
    │   └── output.md
    ├── physics/
    │   ├── input.md
    │   └── output.md
    └── engineering/
        ├── input.md
        ├── output.md
        └── images/
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

| Feature | Status | Description |
|---------|--------|-------------|
| **Import System** | Planned | Import symbols from other Markdown via IR JSON (see above) |
| **CLI `--import` flag** | Planned | `livemathtex process calc.md --import lib.lmt.json` |
| **Watch Mode** | Planned | Auto-rebuild on file changes |
| **Tables with Calculations** | Future | Spreadsheet-like tables in Markdown |
| **Conditional Logic** | Future | If/else in expressions |

**Import System Implementation (next priority):**
```bash
# Option 1: CLI flag
livemathtex process calculation.md --import constants.lmt.json

# Option 2: Document directive
<!-- livemathtex: import constants.lmt.json -->

# Option 3: Both (directive overrides CLI)
```

**Separate projects (build on top of LiveMathTeX):**
- VS Code Extension (`livemathtex-vscode`)
- Web Playground (`livemathtex-web`)
- GUI with PDF export (`livemathtex-desktop`)

---

## References

- [SymPy Documentation](https://docs.sympy.org/)
- [SymPy Units](https://docs.sympy.org/latest/modules/physics/units/)
- [latex2sympy2](https://github.com/augustt198/latex2sympy) (we use [our fork](https://github.com/MarkMichiels/latex2sympy))
- [Cortex-JS MathJSON](https://cortexjs.io/math-json/) (inspiration for IR layer)
