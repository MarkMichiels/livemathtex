# LiveMathTeX - Usage Reference

> Complete reference for syntax, workflow, and examples.

---

## Quick Reference

| Operator | Meaning | Input | Output |
|----------|---------|-------|--------|
| `:=` | Define | `$x := 42$` | `$x := 42$` (unchanged) |
| `==` | Evaluate | `$x ==$` | `$x == 42$` (result filled in) |
| `:= ==` | Define + evaluate | `$y := x^2 ==$` | `$y := x^2 == 1764$` |
| `=>` | Symbolic | `$f'(x) =>$` | `$f'(x) => 2x$` |

**Unit conversion** (using HTML comment, invisible in rendered output):
```
Input:   $v ==$ <!-- [m/s] -->
Output:  $v == 27.78\ \text{m/s}$ <!-- [m/s] -->
```

**Notes:**
- Results are **overwritten** on re-run (old values replaced with new)
- Default output: SI units
- Pure display formulas (no operators) pass through unchanged: `$E = mc^2$`
- Bare `=` only errors in blocks that contain `:=`, `==`, or `=>`

---

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Editor    │───▶│   Save      │───▶│  LiveMathTeX│───▶│   Preview   │
│  (VS Code)  │    │  (.md file) │    │  (CLI)      │    │  (Pandoc)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

1. **Edit:** Write Markdown with embedded calculations
2. **Save:** File triggers watch mode rebuild
3. **View:** See rendered output with computed results
4. **Iterate:** Adjust values, fix errors, repeat

Target latency: < 500ms for instant feedback.

---

## Operators

### Definition (`:=`)

Assigns a value to a variable. No output is generated.

```latex
$m := 5\ \text{kg}$
$g := 9.81\ \text{m/s}^2$
$f(x) := x^2 + 2x + 1$
```

### Evaluation (`==`)

Shows the computed value of a defined variable.

```latex
$m := 5\ \text{kg}$
$g := 9.81\ \text{m/s}^2$
$F := m \cdot g$
$F ==$
```

**Output:** `$F == 49.05\ \text{N}$`

**Or combined (define + evaluate in one line):**

```latex
$F := m \cdot g ==$
```

**Output:** `$F := m \cdot g == 49.05\ \text{N}$`

> **Note:** Using `=` instead of `:=` or `==` in a block with operators will produce an error, preventing accidental overwrites. Pure display formulas like `$E = mc^2$` (no operators) pass through unchanged.

### Symbolic (`=>`)

Performs symbolic operations (differentiation, integration, solving).

```latex
$f'(x) =>$
$\int x^2\, dx =>$
$\text{solve}(x^2 - 4 = 0) =>$
```

**Output:** Shows symbolic result, not numeric.

---

## Variables

### Simple Names

```
x, y, z, mass, force, velocity
```

### Greek Letters

```latex
$\alpha$, $\beta$, $\gamma$, $\delta$, $\theta$, $\pi$, $\omega$
```

### Subscripts

```latex
$x_1$, $x_{max}$, $T_{ambient}$, $v_{initial}$
```

### Functions

```latex
$f(x) := x^2 + 2x + 1$
$g(x, y) := x^2 + y^2$
$\text{area}(r) := \pi \cdot r^2$
```

---

## Numbers

### Formats

```
5, 42, 1000              # integers
3.14, 0.001              # decimals
1.5e-3, 6.022e23         # scientific
```

### LaTeX Scientific Notation

```latex
$1.5 \times 10^{-3}$
$6.022 \times 10^{23}$
```

### Fractions

```latex
$\frac{1}{2}$
$\frac{x + 1}{x - 1}$
```

---

## Units

### Basic Units

```latex
$5\ \text{kg}$
$10\ \text{m}$
$100\ \text{N}$
```

### Compound Units

```latex
$9.81\ \text{m/s}^2$
$50\ \text{km/h}$
$1.2\ \text{kg/m}^3$
```

### Supported Units

| Category | Units |
|----------|-------|
| Length | m, km, cm, mm, µm, nm, in, ft, mi |
| Mass | kg, g, mg, lb, oz |
| Time | s, ms, µs, min, h, day |
| Force | N, kN, lbf |
| Energy | J, kJ, MJ, kWh, cal, eV |
| Power | W, kW, MW, hp |
| Pressure | Pa, kPa, MPa, bar, psi, atm |
| Temperature | K, °C, °F |

### Unit Display (IMPORTANT)

**Default behavior:** All results are displayed in **SI base units** (m, kg, s, A, K, mol, cd).

**To display in different units:** Add `<!-- [unit] -->` comment after the evaluation:

```markdown
# Input (define in any unit you want)
$Q := 50\ \text{L/h}$

# Display in default SI (m³/s)
$Q ==$

# Display in specific unit
$Q ==$ <!-- [L/h] -->
$Q ==$ <!-- [m³/h] -->
```

```markdown
# Output
$Q := 50\ \text{L/h}$
$Q == 1.389e-05\ \text{m}^3/\text{s}$           ← SI default
$Q == 50\ \text{L/h}$ <!-- [L/h] -->             ← same as input
$Q == 0.05\ \text{m}^3/\text{h}$ <!-- [m³/h] --> ← converted
```

**🚨 Common mistake - Don't manually convert:**

```markdown
# ❌ WRONG - unnecessary manual conversion
$Q_{vol} := 50\ \text{L/h}$
$Q_s := 0.0000139\ Q_{vol}$  ← Don't do this!

# ✅ CORRECT - let LiveMathTeX handle conversion
$Q := 50\ \text{L/h}$
$Q ==$ <!-- [m³/s] -->       ← Just request the display unit
```

**Why HTML comments?**
- The instruction stays in the source for re-runs
- Invisible when rendered (preview/PDF)
- Doesn't affect calculations, only display

### Value Display in Tables

When creating summary tables, you often want to display just the **numeric value** of a variable, not the full formula. Use the `<!-- value:VAR [unit] :precision -->` syntax:

```markdown
| Parameter | Value | Unit |
|-----------|-------|------|
| Flow rate | $ $ <!-- value:Q [m³/h] --> | m³/h |
| Velocity  | $ $ <!-- value:vel [m/s] :2 --> | m/s |
| Power     | $ $ <!-- value:P [kW] :2 --> | kW |
```

**Output:**

| Parameter | Value | Unit |
|-----------|-------|------|
| Flow rate | $50.00$ | m³/h |
| Velocity  | $1.77$ | m/s |
| Power     | $2.86$ | kW |

**Syntax components:**

| Part | Required | Description | Example |
|------|----------|-------------|---------|
| `$ $` | Yes | Empty math block (placeholder) | `$ $` |
| `value:VAR` | Yes | Variable name (LaTeX notation) | `value:P_{hyd}` |
| `[unit]` | Optional | Target unit for conversion | `[kW]` |
| `:precision` | Optional | Decimal places | `:2` |

**Important:**
- The math block must be empty (`$ $`) for value-only display
- Variable names use the same LaTeX notation as in your formulas
- Units use simple Unicode notation (`m³/h`, `kW`, `m/s`)
- The dollar signs are preserved in the output for proper KaTeX rendering

**Examples:**

```markdown
<!-- Just the value, default precision -->
$ $ <!-- value:Q -->

<!-- Value with unit conversion -->
$ $ <!-- value:Q [L/s] -->

<!-- Value with precision -->
$ $ <!-- value:vel :3 -->

<!-- Value with unit AND precision -->
$ $ <!-- value:P_{hyd} [kW] :2 -->

<!-- Greek letter variables -->
$ $ <!-- value:\rho [kg/m³] -->
```

### Custom Units

```latex
$1\ \text{lightyear} := 9.461 \times 10^{15}\ \text{m}$
```

---

## Functions

### Trigonometric

```latex
$\sin(x)$, $\cos(x)$, $\tan(x)$
$\arcsin(x)$, $\arccos(x)$, $\arctan(x)$
```

### Exponential & Logarithmic

```latex
$\exp(x)$, $e^x$
$\ln(x)$, $\log(x)$, $\log_{10}(x)$
```

### Roots

```latex
$\sqrt{x}$
$\sqrt[3]{x}$
$|x|$
```

### Aggregation

```latex
$\min(a, b, c)$
$\max(a, b, c)$
$\sum_{i=1}^{n} x_i$
```

---

## Matrices & Vectors

### Definition

```latex
$\vec{v} := [1, 2, 3]$
$A := [[1, 2]; [3, 4]]$
```

### Operations

```latex
$A^T$            <!-- transpose -->
$A^{-1}$         <!-- inverse -->
$\det(A)$        <!-- determinant -->
$A \cdot B$      <!-- multiplication -->
```

---

## Symbolic Operations

Use `=>` for symbolic math:

### Differentiation

```latex
$\frac{d}{dx}(x^2) =>$
$\text{diff}(x^3, x) =>$
```

### Integration

```latex
$\int x^2\, dx =>$
```

### Equation Solving

```latex
$\text{solve}(x^2 - 5x + 6 = 0, x) =>$
```

### Simplification

```latex
$\text{simplify}(\sin^2(x) + \cos^2(x)) =>$
```

---

## Comments

### Line Comments

```latex
# This entire line is a comment
$x := 5$  # Inline comment
```

### Block Comments

```markdown
<!--
Multi-line comment
-->
```

---

## Document Directives

Control behavior within documents:

```markdown
<!-- livemathtex: digits=4 -->
<!-- livemathtex: scientific=true -->
<!-- livemathtex: units=SI -->
```

Or with code fence:

````markdown
```livemathtex-config
digits: 4
scientific: false
```
````

---

## CLI Usage

### Basic

```bash
livemathtex process input.md -o output.md
```

### With Debug Output

The `--verbose` flag writes an IR (Intermediate Representation) JSON file for debugging:

```bash
livemathtex process input.md --verbose
# Creates: input.lmt.json with all symbol mappings and results

livemathtex process input.md -v --ir-output debug.json
# Custom IR output path
```

### Inspect IR

View the contents of an IR JSON file:

```bash
livemathtex inspect input.lmt.json
```

Output:
```
Source: engineering/input.md
Version: 1.0

Symbols:
  \Delta_{T_h}: = 17.92 [K]
  T_{h,out}: = 72.08
  LMTD: = 55.01 [K]
  A: = 5.45 [m²]

Stats:
  definitions: 26
  evaluations: 16
  errors: 0
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Output Markdown file (default: in-place) |
| `-v, --verbose` | Write IR to JSON file for debugging |
| `--ir-output FILE` | Custom path for IR JSON |

### PDF Output

Use Pandoc on the processed Markdown:

```bash
livemathtex process calculation.md -o calculation_out.md
pandoc calculation_out.md -o calculation.pdf
```

---

## Error Handling

### Error Types

| Error | Cause |
|-------|-------|
| `Undefined variable` | Variable not defined before use |
| `Unit mismatch` | Incompatible units in operation |
| `Division by zero` | Divide by zero |
| `Invalid syntax` | Parse error |
| `Circular dependency` | Self-reference |
| `Computation timeout` | Expression too complex |

### Error Display

Errors appear inline:

```latex
$y == x + 1$ → Error: Undefined variable 'x'
```

**Note about bare `=`:**
- Pure display: `$E = mc^2$` → passes through unchanged (no operators in block)
- In calculation block: `$$ x := 5 \n y = x + 3 $$` → Error on the `y = ...` line

Console also reports errors with line numbers.

---

## Debugging

### IR JSON Output

Use `--verbose` to generate a JSON file containing the full intermediate representation:

```bash
livemathtex process input.md --verbose
```

This creates `input.lmt.json` with:

```json
{
  "version": "1.0",
  "source": "input.md",
  "symbols": {
    "Delta_T_h": {
      "mapping": {
        "latex_original": "\\Delta T_h",
        "latex_display": "\\Delta_{T_h}",
        "internal_name": "Delta_T_h"
      },
      "value": 17.92,
      "unit": "K",
      "line": 52
    }
  },
  "blocks": [...],
  "errors": [],
  "stats": {
    "definitions": 26,
    "evaluations": 16,
    "errors": 0
  }
}
```

### Symbol Mapping

The IR tracks three forms of each symbol:

| Form | Example | Purpose |
|------|---------|---------|
| `latex_original` | `\Delta T_h` | Exactly as written in input |
| `latex_display` | `\Delta_{T_h}` | KaTeX-safe display form |
| `internal_name` | `Delta_T_h` | Python/SymPy identifier |

This mapping solves:
- **KaTeX rendering issues** (no `\text{Delta_T_h}` errors)
- **Symbol lookup consistency** (Greek letters work correctly)
- **Debugging clarity** (see exactly what's happening)

### Inspecting Results

```bash
livemathtex inspect input.lmt.json
```

Shows all symbols, their values, and any errors in a human-readable format.

---

## Examples

### Example 1: Basic Physics

**Input:**
```markdown
$g := 9.81\ \text{m/s}^2$
$h := 100\ \text{m}$

Time to fall:
$t := \sqrt{\frac{2h}{g}} ==$

Final velocity:
$v := g \cdot t ==$
```

**Output:**
```markdown
$t := \sqrt{\frac{2h}{g}} == 4.515\ \text{s}$
$v := g \cdot t == 44.29\ \text{m/s}$
```

---

### Example 2: Beam Design

**Input:**
```markdown
## Material
$E := 200\ \text{GPa}$

## Geometry
$L := 6\ \text{m}$
$b := 0.2\ \text{m}$
$h := 0.4\ \text{m}$

## Section Properties
$I := \frac{b \cdot h^3}{12} ==$

## Loading
$w := 20\ \text{kN/m}$

## Maximum Bending Moment
$M_{max} := \frac{w \cdot L^2}{8} ==$

## Maximum Deflection
$\delta_{max} := \frac{5 \cdot w \cdot L^4}{384 \cdot E \cdot I}\ [\text{mm}] ==$
```

---

### Example 3: RC Circuit

**Input:**
```markdown
$R := 10\ \text{k}\Omega$
$C := 100\ \text{µF}$
$V_s := 12\ \text{V}$

Time constant:
$\tau := R \cdot C ==$

Charging voltage at $t := 0.5\ \text{s}$:
$V_C := V_s \cdot (1 - e^{-t/\tau}) ==$

Energy stored:
$E := \frac{1}{2} C V_s^2 ==$
```

---

### Example 4: Linear System

**Input:**
```markdown
Solve: $3x + 2y = 7$ and $x - y = 1$

$A := [[3, 2]; [1, -1]]$
$b := [7, 1]$

$x := A^{-1} \cdot b ==$

Verification: $check := A \cdot x ==$
Determinant: $det := \det(A) ==$
```

---

### Example 5: Calculus

**Input:**
```markdown
$f(x) := x^3 - 3x^2 + 2x$

$f'(x) =>$
$f''(x) =>$

Critical points:
$\text{solve}(f'(x) = 0, x) =>$

Indefinite integral:
$\int f(x)\, dx =>$
```

---

### Example 6: Error Handling

**Pure display passes through (no operators in block):**
```markdown
$E = mc^2$               <!-- Pure display - no error -->
```

**Errors in calculation blocks:**
```markdown
$$
x := 5
y = x + 3                <!-- ERROR: bare = in block with operators -->
$$

$result := z + 5 ==$     <!-- ERROR: undefined variable -->

$a := 5$
$b := 3$
$c := a + b ==$          <!-- works: 8 -->
```

**Output:**
```markdown
$E = mc^2$               <!-- unchanged -->
$$x := 5
y = x + 3
Error: Invalid operator '='. Use ':=' or '=='$$
$result := z + 5 == Error: Undefined variable 'z'$
$c := a + b == 8$
```

---

## Best Practices

### Do

- ✅ Document calculations with text
- ✅ Use meaningful variable names (`F_gravity` not `F1`)
- ✅ Include units in definitions
- ✅ Use `=>` for symbolic operations
- ✅ Use comments for clarification

### Don't

- ❌ Create circular dependencies
- ❌ Use extremely long variable names
- ❌ Forget to define variables before use
- ❌ Mix incompatible units

---

## Reserved Keywords

Cannot be used as variable names:

```
sin, cos, tan, asin, acos, atan
sinh, cosh, tanh
log, ln, exp, sqrt
abs, floor, ceil, round
min, max, sum, prod
diff, integrate, solve, simplify
det, inv, transpose
pi, e, i
true, false
```

---

## Plain Text Benefits

- Source files readable without tools
- Version control friendly (Git diffs work)
- Searchable text
- Works offline
- No proprietary formats

---

## Editor Integration (Planned)

### VS Code
- Syntax highlighting for `:=`, `==`, `=>`
- Live preview pane
- Error squiggles
- Hover for computed values

### Any Editor
- Edit in preferred editor
- Run `livemathtex --watch` in terminal
- View output with any Markdown viewer

---

## Summary

LiveMathTeX transforms Markdown into live technical documents:

1. **Immediate feedback** — See results as you type
2. **Familiar syntax** — Markdown + LaTeX, no new language
3. **Clear errors** — Know exactly what went wrong
4. **Plain text** — Enhanced Markdown, use Pandoc for PDF/HTML
5. **Safe** — Documents can't execute harmful code
