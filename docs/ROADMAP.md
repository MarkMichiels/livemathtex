# Livemathtex - Development Roadmap

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
  - [x] Documentation (SPEC, ARCHITECTURE, UX)
  - [ ] pyproject.toml with dependencies
  - [ ] Basic test infrastructure

- [ ] **1.2 Parser (Basic)**
  - [ ] Recognize `:=` definitions
  - [ ] Recognize `=` evaluations
  - [ ] Recognize `=>` symbolic/highlight
  - [ ] Parse simple arithmetic expressions
  - [ ] Handle variable names (including Greek letters)
  - [ ] Skip non-calculation Markdown content

- [ ] **1.3 Engine (Basic)**
  - [ ] Symbol table for variables
  - [ ] Numeric evaluation of expressions
  - [ ] Basic error handling (undefined variable, division by zero)
  - [ ] Evaluation order (top-down)

- [ ] **1.4 Renderer (Basic)**
  - [ ] Output Markdown with results injected
  - [ ] Format numbers (configurable precision)
  - [ ] Display errors inline

- [ ] **1.5 CLI (Basic)**
  - [ ] `livemathtex input.md -o output.md`
  - [ ] Basic file I/O

### Success Criteria

```markdown
# Input
$x := 5$
$y := 3$
$z = x + y$

# Output
$x := 5$
$y := 3$
$z = x + y = 8$
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
  - [ ] PDF output (via Pandoc)
  - [ ] Verbose/quiet modes
  - [ ] Precision flag (`--digits`)

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
$F = m \cdot a$

# Output
$F = m \cdot a = 49.05\ \text{N}$
```

---

## Phase 3: Advanced Features

**Goal:** Symbolic math, matrices, graphs.

**Timeline:** 4-6 weeks

### Deliverables

- [ ] **3.1 Matrices & Vectors**
  - [ ] Matrix definition syntax
  - [ ] Basic operations (add, multiply)
  - [ ] Inverse, determinant, transpose
  - [ ] Linear system solving

- [ ] **3.2 Graphs**
  - [ ] Plot code block syntax
  - [ ] 2D line plots
  - [ ] Multiple series
  - [ ] Axis labels with units
  - [ ] PNG/SVG output
  - [ ] Embedded in Markdown/PDF

- [ ] **3.3 Symbolic Math (Basic)**
  - [ ] SymPy integration
  - [ ] Simplification
  - [ ] Solving equations
  - [ ] Differentiation
  - [ ] Integration

- [ ] **3.4 Result Highlighting**
  - [ ] `=>` syntax for important results
  - [ ] Visual emphasis in output
  - [ ] Summary generation (optional)

- [ ] **3.5 Performance**
  - [ ] Caching of parsed AST
  - [ ] Incremental recalculation
  - [ ] Timeout per expression
  - [ ] Memory limits

### Success Criteria

```markdown
# Input
$A := [[1, 2]; [3, 4]]$
$\det(A) =$

```plot
y = x^2 - 4x + 3
x = -1..5
```

# Output
$\det(A) = -2$
[Generated plot image]
```

---

## Phase 4: Ecosystem

**Goal:** Editor integration, community tools.

**Timeline:** Ongoing

### Deliverables

- [ ] **4.1 VS Code Extension**
  - [ ] Syntax highlighting
  - [ ] Live preview pane
  - [ ] Error diagnostics
  - [ ] Hover for computed values
  - [ ] Go-to-definition for variables

- [ ] **4.2 Web Playground**
  - [ ] Browser-based demo
  - [ ] Pyodide or WASM
  - [ ] Share calculations via URL

- [ ] **4.3 Additional Output Formats**
  - [ ] HTML with KaTeX
  - [ ] Pure LaTeX (.tex)
  - [ ] Jupyter notebook export

- [ ] **4.4 Import/Include**
  - [ ] Include other documents
  - [ ] Shared variable libraries
  - [ ] Constants databases

- [ ] **4.5 Tables with Calculations**
  - [ ] Spreadsheet-like tables
  - [ ] Cell references
  - [ ] Column calculations

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
| 0.1.0 | 1 | Basic arithmetic, variables |
| 0.2.0 | 2 | Units, LaTeX parsing, watch mode |
| 0.3.0 | 3 | Matrices, graphs |
| 0.4.0 | 3 | Symbolic math |
| 0.5.0 | 4 | VS Code extension |
| 1.0.0 | 4 | Stable release |

---

## Priorities

### Must Have (MVP)
- `:=`, `=` and `=>` syntax
- Variable definitions
- Basic arithmetic
- CLI with file I/O

### Should Have (v0.2)
- Unit support
- LaTeX parsing
- Watch mode
- PDF output

### Nice to Have (v0.3+)
- Graphs
- Symbolic math
- Matrices
- Editor extensions

### Future
- Tables with calculations
- Conditional logic
- Import/include
- Web playground

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

- [Project SPEC](./SPEC.md)
- [Architecture](./ARCHITECTURE.md)
- [UX Design](./UX.md)
- [Syntax Reference](./SYNTAX.md)
- [Dependencies](./DEPENDENCIES.md)
