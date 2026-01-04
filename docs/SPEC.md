# Livemathtex - Specification

**Live math calculations in LaTeX notation**

---

## Introduction

Livemathtex is a Markdown-driven tool for calculations – similar to PTC Mathcad – where calculations are performed in live mathematical notation within plain-text documents. The goal is to make documenting technical calculations as easy as writing Markdown, while automatically computing results.

### Existing Tools Landscape

| Tool | Approach | Pros | Cons |
|------|----------|------|------|
| **[CalcuLaTeX](https://github.com/mkhan45/CalcuLaTeX)** | Rust interpreter, LaTeX output | Units, variables, `= ?` syntax | No graphs, no symbolic, requires pandoc+LaTeX |
| **[Calca](https://calca.io)** | Markdown editor + calculator | Real-time updates, `=>` syntax | Closed source, platform limited |
| **[Soulver](https://soulver.app)** | Notepad calculator | Variables, units, live | Less focus on LaTeX notation |
| **[Obsidian Numerals](https://github.com/gtg922r/obsidian-numerals)** | Obsidian plugin, MathJS | Units, variables, `=>` highlight | Only in Obsidian, not saved to file |
| **[Typst](https://typst.app)** | Modern typesetting | Built-in scripting, fast | Different ecosystem, not Markdown |

Livemathtex fills the gap by combining: **LaTeX notation + live calculations + plain Markdown + CLI tool**.

---

## Core Objectives

### 1. Markdown + LaTeX Notation

Users write formulas in natural mathematical notation (with LaTeX syntax for symbols) directly in Markdown files. Formulas and results are beautifully rendered via MathJax/KaTeX or LaTeX.

### 2. Definition vs Evaluation Syntax

Inspired by Mathcad's clear distinction:

| Syntax | Meaning | Output |
|--------|---------|--------|
| `x := 5` | Definition (assignment) | Shows definition only |
| `x = ?` | Evaluation (compute) | Shows computed result |
| `x =` | Implicit evaluation | Shows computed result |

**Example:**

```markdown
$v := 50\ \text{km/h}$           <!-- definition, no output -->
$t := 4\ \text{h}$               <!-- definition, no output -->
$d = v \cdot t = ?$              <!-- evaluation, shows: d = 200 km -->
```

### 3. Automatic Recalculation

The system recalculates all dependent values automatically when a variable or formula changes. In watch mode, the output updates immediately upon file save.

### 4. Unit Support

Full support for physical units in calculations:

- Variables can have units: `m := 5 kg`
- Operations check dimensions and convert automatically
- `F = m * a = ?` outputs result in Newton (N)
- Unit mismatch produces clear error messages
- User-defined units: `1 mph := 1 mile/hour`

### 5. Matrix & Vector Calculations

Support for linear algebra operations:

- Matrix input: `A := [[1, 2]; [3, 4]]`
- Operations: inverse, transpose, determinant, multiplication
- System solving: `solve(A, b)`

### 6. Graph Generation

Built-in capability to generate graphs:

```markdown
```plot
y = x^2 - 4x + 5
x = -2..6
```
```

- 2D plots (future: 3D)
- Automatic axis labeling
- Unit-aware axes
- Embedded as images in output

### 7. Inline Error Messages

When errors occur, results show clear messages at the evaluation point:

```markdown
$F = m \cdot a = ?$
<!-- Output: F = ⚠️ Error: Undefined variable 'm' -->
```

Errors are visually marked (red text, warning icon) similar to Mathcad's red error boxes.

### 8. Symbolic Manipulation (CAS)

Optional symbolic computation support:

- Expression simplification
- Equation solving: `solve(x^2 - 5x + 6 = 0)` → `x = 2, x = 3`
- Differentiation: `diff(x^2, x)` → `2x`
- Integration: `integrate(x^2, x)` → `x^3/3`

*Note: Symbolic functionality is secondary to numeric+units.*

### 9. Extensibility & Open Source

- Modular architecture
- Plugin system for new functions/units
- Sandboxed evaluation (no arbitrary code execution)
- Safe to run untrusted documents

---

## Key Features Summary

| Feature | Description |
|---------|-------------|
| **Live calculations** | Combine documentation and calculation in one file |
| **`:=` vs `=`** | Clear separation between definition and evaluation |
| **Auto-recalculation** | Automatic updates on changes |
| **Units** | SI units, conversions, dimension analysis |
| **Matrices** | Linear algebra operations |
| **Graphs** | Embedded plots without external tools |
| **Inline errors** | Clear feedback at error location |
| **Symbolic** | Optional CAS for algebra |
| **CLI tooling** | `livemathtex input.md -o output.pdf` |
| **Safe** | Sandboxed execution, no security risks |

---

## CLI Interface

```bash
# Basic conversion
livemathtex input.md -o output.md

# PDF output
livemathtex input.md -o output.pdf

# Watch mode (auto-rebuild on save)
livemathtex input.md -o output.md --watch

# Specify precision
livemathtex input.md --digits 4

# Scientific notation
livemathtex input.md --scientific
```

---

## Output Formats

| Format | Description |
|--------|-------------|
| **Markdown** | Input with results injected, MathJax-ready |
| **PDF** | Via LaTeX compilation |
| **HTML** | Standalone with KaTeX/MathJax |
| **LaTeX** | Pure .tex file |

---

## References

- [CalcuLaTeX by Mikail Khan](https://github.com/mkhan45/CalcuLaTeX)
- [Calca](https://calca.io)
- [Obsidian Numerals](https://github.com/gtg922r/obsidian-numerals)
- [GitHub Math Expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)
