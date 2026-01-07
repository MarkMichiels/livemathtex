# LiveMathTeX - Development Roadmap

> 💡 **Note:** This project is developed with the help of AI coding assistants. Feedback and contributions welcome!

## Overview

This roadmap outlines the phased development of LiveMathTeX from MVP to full-featured release.

```
Phase 1: Foundation     ████████████████████ 100%  [COMPLETE]
Phase 2: Core Features  ██████████████████░░  90%  [Current]
Phase 3: Advanced       ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4: Ecosystem      ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## Phase 1: Foundation (MVP) - COMPLETE

**Goal:** Minimal viable product that demonstrates core concept.

**Status:** COMPLETE

### Deliverables

- [x] **1.1 Project Setup**
  - [x] Repository structure
  - [x] Documentation (ARCHITECTURE, USAGE, ROADMAP)
  - [x] pyproject.toml with dependencies
  - [x] Basic test infrastructure

- [x] **1.2 Parser (Basic)**
  - [x] Recognize `:=` definitions
  - [x] Recognize `==` evaluations
  - [x] Recognize `=>` symbolic operations
  - [x] Error on bare `=` (safety feature)
  - [x] Parse simple arithmetic expressions
  - [x] Handle variable names (including Greek letters)
  - [x] Skip non-calculation Markdown content
  - [x] **NEW:** Display-only formulas pass through unchanged

- [x] **1.3 Engine (Basic)**
  - [x] Symbol table for variables
  - [x] Numeric evaluation of expressions
  - [x] Basic error handling (undefined variable, division by zero)
  - [x] Evaluation order (top-down)

- [x] **1.4 Error Handling (from day one)**
  - [x] Undefined variable: clear message at evaluation point
  - [x] Division by zero, math errors
  - [x] Syntax errors with line numbers
  - [x] Console summary with all errors
  - [x] Errors never crash - always produce output

- [x] **1.5 Renderer (Basic)**
  - [x] Output Markdown with results injected
  - [x] Format numbers (configurable precision)
  - [x] Display errors inline (red/warning style)

- [x] **1.6 CLI (Basic)**
  - [x] `livemathtex process input.md -o output.md`
  - [x] Basic file I/O
  - [x] **NEW:** `--verbose` flag for IR JSON output
  - [x] **NEW:** `livemathtex inspect` command

### Success Criteria

```markdown
# Input
$x := 5$
$y := 3$
$z := x + y ==$

# Output
$x := 5$
$y := 3$
$z := x + y == 8$
```

---

## Phase 2: Core Features - IN PROGRESS

**Goal:** Full numeric calculation with units, IR layer.

**Status:** 90% complete

### Deliverables

- [x] **2.1 Unit Support** (TASK-007 - COMPLETE)
  - [x] Integrate SymPy physics.units (not Pint - simpler)
  - [x] Parse units in expressions (basic)
  - [x] Automatic dimension checking
  - [x] Unit conversion on output (via HTML comments)
  - [x] Error messages for unit/variable name conflicts
  - [x] **Custom unit definitions** (`===` syntax)
  - [x] Unit abbreviation mappings (L→liter, h→hour, dag→day)
  - [x] Currency units (euro, dollar)
  - [x] **Strip units from values** (`strip_unit_from_value()`)
  - [x] **Unit propagation through calculations** (`propagate_units=True`)
  - [x] **Unit display in output** (`_format_unit_part()`)

- [x] **2.2 LaTeX Parsing**
  - [x] Integrate latex2sympy2
  - [x] Parse fractions (`\frac{}{}`)
  - [x] Parse subscripts/superscripts (including complex like `T_{h,in}`)
  - [x] Parse Greek letters (Δ, α, θ, etc.)
  - [x] Parse common functions (sin, cos, sqrt, log)

- [x] **2.3 Intermediate Representation (IR)**
  - [x] Symbol normalization (`v_{n}`/`f_{n}` architecture)
  - [x] IR JSON output for debugging (`--verbose`)
  - [x] `inspect` command for IR files
  - [ ] **Import system** (load symbols from other Markdown via IR)

- [x] **2.4 Functions**
  - [x] Built-in math functions
  - [x] User-defined functions `f(x) := ...`
  - [ ] Multiple parameters

- [ ] **2.5 CLI Enhanced**
  - [ ] Watch mode (`--watch`)
  - [x] Verbose mode (`--verbose`)
  - [ ] Precision flag (`--digits`)
  - [x] Documentation: explain how to use Pandoc for PDF
  - [ ] `--import` flag for loading library IR

- [x] **2.6 Configuration System** (TASK-006 - COMPLETE)
  - [x] Document directives (`<!-- livemathtex: digits=4 -->`)
  - [x] Expression-level overrides (`<!-- digits:2 -->`)
  - [x] Local config (`.livemathtex.toml`)
  - [x] Project config (`pyproject.toml [tool.livemathtex]`)
  - [x] User config (`~/.config/livemathtex/config.toml`)
  - [x] Config precedence hierarchy
  - [x] Safe output defaults (timestamped, not inplace)

- [x] **2.7 Error Handling**
  - [x] Comprehensive error types
  - [x] Line number in errors
  - [x] Visual error markers in output (inline LaTeX)
  - [x] Console error summary

### Success Criteria

```markdown
# Input
$m := 5\ \text{kg}$
$a := 9.81\ \text{m/s}^2$
$F := m \cdot a ==$

# Output
$F := m \cdot a == 49.05\ \text{N}$
```

---

## Phase 3: Advanced Features

**Goal:** Symbolic math, matrices.

**Timeline:** 4-6 weeks

### Deliverables

- [ ] **3.1 Matrices & Vectors**
  - [ ] Matrix definition syntax
  - [ ] Basic operations (add, multiply)
  - [ ] Inverse, determinant, transpose
  - [ ] Linear system solving

- [ ] **3.2 Symbolic Math (Basic)**
  - [ ] SymPy integration
  - [ ] Simplification
  - [ ] Solving equations
  - [ ] Differentiation
  - [ ] Integration

- [ ] **3.3 Symbolic Operations (`=>`)**
  - [ ] Differentiation: `$f'(x) =>$`
  - [ ] Integration: `$\int f(x) dx =>$`
  - [ ] Equation solving: `$\text{solve}(f(x)=0) =>$`

- [ ] **3.4 Performance**
  - [ ] Caching of parsed AST
  - [ ] Incremental recalculation
  - [ ] Timeout per expression
  - [ ] Memory limits

### Success Criteria

```markdown
# Input
$A := [[1, 2]; [3, 4]]$
$\det(A) ==$
$f(x) := x^2 - 4x + 3$
$f'(x) =>$

# Output
$\det(A) == -2$
$f'(x) => 2x - 4$
```

---

## Phase 4: Ecosystem (Optional)

**Goal:** Editor integration for better UX.

**Timeline:** If needed

### Deliverables

- [ ] **4.1 VS Code Extension**
  - [ ] Syntax highlighting for `:=`, `==`, `=>`
  - [ ] Live preview pane
  - [ ] Error diagnostics
  - [ ] Hover for computed values

- [ ] **4.2 Web Playground** (optional, for demo)
  - [ ] Browser-based demo via Pyodide
  - [ ] Share calculations via URL

- [ ] **4.3 Import/Include** (moved to Phase 2)
  - [x] IR JSON output enables import workflow
  - [ ] CLI `--import` flag to load library IR
  - [ ] Document directive `<!-- livemathtex: import lib.lmt.json -->`

  **Import Workflow:**
  ```bash
  # 1. Create library Markdown (constants.md)
  # 2. Process: livemathtex process constants.md --verbose
  # 3. Import: livemathtex process calc.md --import constants.lmt.json
  ```

---

## Technical Debt & Quality

### Throughout All Phases

- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Documentation updates
- [ ] Type hints (mypy clean)
- [ ] Linting (ruff clean)
- [ ] Performance benchmarks
- [ ] Security review (sandboxing)

---

## Version Milestones

| Version | Phase | Key Features | Status |
|---------|-------|--------------|--------|
| 0.1.0 | 1 | Basic arithmetic, variables, error handling, IR layer | DONE |
| 0.2.0 | 2 | Units, LaTeX parsing, import system | In progress |
| 0.3.0 | 3 | Symbolic math, matrices | Planned |
| 1.0.0 | - | Stable release | Future |

---

## Out of Scope (intentionally)

| Feature | Reason | Use Instead |
|---------|--------|-------------|
| PDF/HTML export | Existing tools excel | Pandoc, WeasyPrint |
| Plotting/graphs | Many excellent libs | Matplotlib, charts CLI |
| GUI editor | We're a preprocessor | VS Code + MPE |
| Jupyter kernel | Jupyter has SymPy | Use Jupyter directly |

---

## Priorities

### Done (v0.1)
- [x] `:=`, `==` and `=>` syntax
- [x] Variable definitions
- [x] Basic arithmetic
- [x] Error handling (from day one!)
- [x] CLI with file I/O
- [x] Unit support (SI)
- [x] LaTeX parsing
- [x] IR layer for debugging

### In Progress (v0.2)
- [ ] Import system (load Markdown IR)
- [ ] Watch mode
- [ ] Symbolic math (`=>`)

### Nice to Have (v0.3+)
- Matrices
- VS Code extension
- Tables with calculations

### Future (maybe)
- Conditional logic
- Web playground (for demo only)

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to help with development.

**Good First Issues:**
- Add new unit definitions
- Add math functions
- Improve error messages
- Write documentation
- Add example documents

---

## References

- [Background](./BACKGROUND.md)
- [Architecture](./ARCHITECTURE.md)
- [Usage Reference](./USAGE.md)
- [Dependencies](./DEPENDENCIES.md)
- [Pint Migration Analysis](./PINT_MIGRATION_ANALYSIS.md)
