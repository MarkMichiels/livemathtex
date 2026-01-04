# Livemathtex - User Experience

## Workflow Overview

Livemathtex integrates seamlessly into a Markdown-based workflow:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Editor    │───▶│   Save      │───▶│  Livemathtex│───▶│   Preview   │
│  (VS Code)  │    │  (.md file) │    │  (CLI)      │    │  (PDF/HTML) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ▲                                                        │
       └────────────────────────────────────────────────────────┘
                         Iterate & Refine
```

### The Edit-Evaluate-View Cycle

1. **Edit:** Write Markdown with embedded calculations
2. **Save:** File triggers watch mode rebuild
3. **View:** See rendered output with computed results
4. **Iterate:** Adjust values, fix errors, repeat

This cycle should feel **instant** (< 500ms latency).

---

## Syntax Guide

### Definitions (`:=`)

Use `:=` to define variables without showing output:

```markdown
$m := 5\ \text{kg}$
$g := 9.81\ \text{m/s}^2$
$F_{friction} := 0.3$
```

**Output:** Shows the definition as-is (no computed value).

### Evaluations (`=`)

Use `=` to compute and display results:

```markdown
$F = m \cdot g$
```

**Output:** `$F = m \cdot g = 49.05\ \text{N}$`

The `?` is optional but makes intent explicit.

### Implicit Evaluation

When the right-hand side is just a variable:

```markdown
$F =$
```

**Output:** `$F = 49.05\ \text{N}$`

### Combined Definition and Evaluation

```markdown
$E := m \cdot c^2$
$E =$
```

Defines `E` AND shows the computed value.

---

## Control Over Output

### What Gets Evaluated

| Pattern | Behavior |
|---------|----------|
| `x := 5` | Define only, no output value |
| `x =` | Evaluate and show result |
| `x =` | Evaluate and show result |
| `$E = mc^2$` | Static LaTeX, no evaluation |

### Pure Documentation Formulas

If you just want to show a formula without evaluation, use standard LaTeX:

```markdown
Einstein's famous equation: $E = mc^2$
```

No `:=` or `=` at the end means Livemathtex leaves it untouched.

---

## Inline vs Block Calculations

### Inline

Small calculations within text:

```markdown
The time constant is $\tau = R \cdot C$ for the given values.
```

### Block

Multi-step calculations as separate paragraphs:

```markdown
## Calculation

1. $v_0 := 20\ \text{m/s}$
2. $t := 5\ \text{s}$
3. $d = v_0 \cdot t$

The total distance traveled is shown in step 3.
```

---

## Error Display

### Error Types and Messages

| Error | Display |
|-------|---------|
| Undefined variable | `⚠️ Error: Undefined variable 'm'` |
| Unit mismatch | `⚠️ Error: Cannot add kg + m` |
| Division by zero | `⚠️ Error: Division by zero` |
| Syntax error | `⚠️ Error: Invalid expression` |
| Timeout | `⚠️ Error: Computation timed out` |

### Visual Feedback

Errors appear **inline** at the evaluation point, styled in red:

```markdown
$F = m \cdot a = \textcolor{red}{\text{⚠️ Undefined variable } m}$
```

The console also reports errors with line numbers:

```
Error on line 12: Undefined variable 'm'
Error on line 15: Unit mismatch in addition
```

---

## Symbolic Operations (`=>`)

Use `=>` for symbolic math (differentiation, integration, solving):

```markdown
$f(x) := x^2 + 2x + 1$
$f'(x) =>$
```

Output: `$f'(x) = 2x + 2$`

---

## Comments and Annotations

### Hash Comments

Within calculation blocks, `#` marks comments:

```markdown
```livemathtex
# Material properties
rho := 7850 kg/m^3    # steel density
E := 200 GPa          # Young's modulus
```
```

Comments appear in output but are not evaluated.

### Document Text

Regular Markdown text between calculations serves as documentation:

```markdown
## Stress Analysis

We first calculate the cross-sectional area:

$A = \pi \cdot r^2$

With this area, we can determine the stress:

$\sigma = F / A$
```

---

## Units Handling

### Supported Units

All SI base and derived units plus common alternatives:

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
| Velocity | m/s, km/h, mph |
| ... | And many more |

### Unit Conversion

Request specific output units:

```markdown
$v := 100\ \text{km/h}$
$v_{\text{si}} = v\ [\text{m/s}]$
```

**Output:** `$v = 27.78\ \text{m/s}$`

### Custom Units

Define your own:

```markdown
$1\ \text{lightyear} := 9.461 \times 10^{15}\ \text{m}$
```

---

## CLI Usage Examples

### Basic Conversion

```bash
# Markdown to Markdown with results
livemathtex calculation.md -o calculation_out.md

# For PDF: use Pandoc on the output
pandoc calculation_out.md -o calculation.pdf
```

### Watch Mode

```bash
# Auto-rebuild on save
livemathtex calculation.md --watch
```

Terminal output:
```
Watching calculation.md...
[14:23:01] Rebuilt in 0.3s - 0 errors
[14:23:15] Rebuilt in 0.2s - 1 warning (line 23: large matrix)
[14:23:22] Rebuilt in 0.2s - 0 errors
```

### Formatting Options

```bash
# 6 significant figures
livemathtex input.md --digits 6

# Scientific notation
livemathtex input.md --scientific

# Combine
livemathtex input.md --digits 3 --scientific -o output.md
```

---

## Document Directives

Control behavior within documents:

```markdown
<!-- livemathtex: digits=4 -->
<!-- livemathtex: scientific=true -->
<!-- livemathtex: units=SI -->
```

Or using code fence syntax:

```markdown
```livemathtex-config
digits: 4
scientific: false
```
```

---

## Editor Integration

### VS Code (Planned)

- Live preview pane
- Syntax highlighting for `:=`, `=` and `=>`
- Error squiggles
- Go-to-definition for variables
- Hover for computed values

### Obsidian (Planned)

- Plugin for live evaluation
- Preview mode integration
- Graph rendering

### Any Editor

Works with any text editor + terminal:
- Edit in your preferred editor
- Run `livemathtex --watch` in terminal
- View output in PDF viewer or browser

---

## Example Use Case

### Engineering Design Document

**File: `beam_design.md`**

```markdown
# Beam Design Calculation

## Given Parameters

$L := 5\ \text{m}$          <!-- Beam length -->
$w := 10\ \text{kN/m}$      <!-- Distributed load -->
$E := 200\ \text{GPa}$      <!-- Young's modulus (steel) -->
$I := 8.33 \times 10^{-5}\ \text{m}^4$  <!-- Moment of inertia -->

## Maximum Bending Moment

For a simply supported beam with uniform load:

$M_{max} = \frac{w \cdot L^2}{8}$

## Maximum Deflection

$\delta_{max} = \frac{5 \cdot w \cdot L^4}{384 \cdot E \cdot I}\ [\text{mm}]$

## Safety Check

Allowable deflection is L/360:

$\delta_{allow} = L / 360\ [\text{mm}]$
$\text{Safe} = \delta_{max} < \delta_{allow} =>$
```

### Workflow

1. Engineer writes `beam_design.md`
2. Runs `livemathtex beam_design.md --watch`
3. Opens output in Markdown Preview (VS Code)
4. Adjusts parameters, sees results immediately
5. For sharing: `pandoc beam_design.md -o beam_design.pdf`
6. Git-commits the .md source

---

## Best Practices

### Do

✅ Document your calculations with text
✅ Use meaningful variable names (`F_gravity` not `F1`)
✅ Include units in definitions
✅ Use `=>` for symbolic operations (derivatives, integrals)
✅ Use comments for clarification

### Don't

❌ Create circular dependencies
❌ Use extremely long variable names
❌ Forget to define variables before use
❌ Mix incompatible units

---

## Accessibility

### Plain Text Foundation

- Source files are readable without tools
- Version control friendly (Git diffs work)
- Searchable text
- Works offline

### Output Format

Livemathtex outputs **Markdown only**. For other formats, use external tools:

- **PDF:** `pandoc output.md -o output.pdf`
- **HTML:** `pandoc output.md -o output.html`
- **Markdown:** Direct output, ready for any Markdown renderer

### Collaboration

- Share `.md` source via Git
- Generated outputs are standalone
- No proprietary formats

---

## Summary

Livemathtex provides the experience of **"live technical documents"**: writing in a LaTeX-style document that simultaneously functions as a calculation sheet. Without switching between code, calculator, and report, users can focus on the content of their calculations.

The key UX principles:

1. **Immediate feedback** - See results as you type
2. **Familiar syntax** - Markdown + LaTeX, no new language
3. **Clear errors** - Know exactly what went wrong
4. **Plain text output** - Enhanced Markdown, use Pandoc for PDF/HTML
5. **Safe sharing** - Documents can't execute harmful code
