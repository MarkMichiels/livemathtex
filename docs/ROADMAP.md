# Livemathtex - Development Roadmap

> ⚠️ **Built with AI** — This project is developed using AI tools. Feedback welcome.

## Overview

This roadmap outlines the phased development of Livemathtex from MVP to full-featured release.

```
Phase 1: Foundation     ████████░░░░░░░░░░░░  40%  [Current]
Phase 2: Core Features  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3: Advanced       ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4: Ecosystem      ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## Phase 1: Foundation (MVP)

**Goal:** Minimal viable product that demonstrates core concept.

**Timeline:** 2-3 weeks

### Deliverables

- [ ] **1.1 Project Setup**
  - [x] Repository structure
  - [x] Documentation (ARCHITECTURE, USAGE, ROADMAP)
  - [ ] pyproject.toml with dependencies
  - [ ] Basic test infrastructure

- [ ] **1.2 Parser (Basic)**
  - [ ] Recognize `:=` definitions
  - [ ] Recognize `==` evaluations
  - [ ] Recognize `=>` symbolic operations
  - [ ] Error on bare `=` (safety feature)
  - [ ] Parse simple arithmetic expressions
  - [ ] Handle variable names (including Greek letters)
  - [ ] Skip non-calculation Markdown content

- [ ] **1.3 Engine (Basic)**
  - [ ] Symbol table for variables
  - [ ] Numeric evaluation of expressions
  - [ ] Basic error handling (undefined variable, division by zero)
  - [ ] Evaluation order (top-down)

- [ ] **1.4 Error Handling (from day one)**
  - [ ] Undefined variable: clear message at evaluation point
  - [ ] Division by zero, math errors
  - [ ] Syntax errors with line numbers
  - [ ] Console summary with all errors
  - [ ] Errors never crash - always produce output

- [ ] **1.5 Renderer (Basic)**
  - [ ] Output Markdown with results injected
  - [ ] Format numbers (configurable precision)
  - [ ] Display errors inline (red/warning style)

- [ ] **1.6 CLI (Basic)**
  - [ ] `livemathtex input.md -o output.md`
  - [ ] Basic file I/O

### Success Criteria

```markdown
# Input
$x := 5$
$y := 3$
$z == x + y$

# Output
$x := 5$
$y := 3$
$z == x + y = 8$
```

---

## Phase 2: Core Features

**Goal:** Full numeric calculation with units.

**Timeline:** 3-4 weeks

### Deliverables

- [ ] **2.1 Unit Support**
  - [ ] Integrate Pint library
  - [ ] Parse units in expressions
  - [ ] Automatic dimension checking
  - [ ] Unit conversion on output
  - [ ] Error messages for unit mismatch

- [ ] **2.2 LaTeX Parsing**
  - [ ] Integrate latex2sympy2
  - [ ] Parse fractions (`\frac{}{}`)
  - [ ] Parse subscripts/superscripts
  - [ ] Parse Greek letters
  - [ ] Parse common functions (sin, cos, sqrt)

- [ ] **2.3 Functions**
  - [ ] Built-in math functions
  - [ ] User-defined functions `f(x) := ...`
  - [ ] Multiple parameters

- [ ] **2.4 CLI Enhanced**
  - [ ] Watch mode (`--watch`)
  - [ ] Verbose/quiet modes
  - [ ] Precision flag (`--digits`)
  - [ ] Documentation: explain how to use Pandoc for PDF

- [ ] **2.5 Error Handling**
  - [ ] Comprehensive error types
  - [ ] Line number in errors
  - [ ] Visual error markers in output
  - [ ] Console error summary

### Success Criteria

```markdown
# Input
$m := 5\ \text{kg}$
$a := 9.81\ \text{m/s}^2$
$F == m \cdot a$

# Output
$F == m \cdot a = 49.05\ \text{N}$
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
$\det(A) =$
$f(x) := x^2 - 4x + 3$
$f'(x) =>$

# Output
$\det(A) = -2$
$f'(x) = 2x - 4$
```

---

## Phase 4: Ecosystem (Optional)

**Goal:** Editor integration for better UX.

**Timeline:** If needed

### Deliverables

- [ ] **4.1 VS Code Extension**
  - [ ] Syntax highlighting for `:=`, `=`, `=>`
  - [ ] Live preview pane
  - [ ] Error diagnostics
  - [ ] Hover for computed values

- [ ] **4.2 Web Playground** (optional, for demo)
  - [ ] Browser-based demo via Pyodide
  - [ ] Share calculations via URL

- [ ] **4.3 Import/Include** (future)
  - [ ] Include other documents
  - [ ] Shared constants libraries

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

| Version | Phase | Key Features |
|---------|-------|--------------|
| 0.1.0 | 1 | Basic arithmetic, variables, error handling |
| 0.2.0 | 2 | Units, LaTeX parsing, watch mode |
| 0.3.0 | 3 | Symbolic math, matrices |
| 1.0.0 | - | Stable release |

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

### Must Have (MVP)
- `:=`, `==` and `=>` syntax
- Variable definitions
- Basic arithmetic
- Error handling (from day one!)
- CLI with file I/O

### Should Have (v0.2)
- Unit support
- LaTeX parsing
- Watch mode

### Nice to Have (v0.3+)
- Symbolic math
- Matrices
- VS Code extension

### Future (maybe)
- Tables with calculations
- Conditional logic
- Import/include
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
