---
description: Process Markdown files with LiveMathTeX calculations
---

# LiveMathTeX - Process Calculations

Process a Markdown file and compute all LaTeX calculations.

## Quick Usage

```bash
# Process file (updates in place)
livemathtex process input.md

# Output to separate file
livemathtex process input.md -o output.md

# Debug mode (creates .lmt.json)
livemathtex process input.md --verbose
```

## Syntax Reference

| Operator | Meaning | Example |
|----------|---------|---------|
| `:=` | Define | `$x := 42$` |
| `==` | Evaluate | `$x ==$` → `$x == 42$` |
| `:= ==` | Define + evaluate | `$y := x^2 ==$` → `$y := x^2 == 1764$` |
| `=>` | Symbolic | `$f'(x) =>$` (future) |

## Example Workflow

**1. Create calculation file:**
```markdown
# Force Calculation

$m := 5$
$a := 9.81$
$F := m \cdot a ==$
```

**2. Process:**
```bash
livemathtex process force.md
```

**3. Result:**
```markdown
# Force Calculation

$m := 5$
$a := 9.81$
$F := m \cdot a == 49.05$
```

## With Units

```markdown
$mass := 75 \text{ kg}$
$gravity := 9.81 \text{ m/s}^2$
$Force := mass \cdot gravity ==$
```

Result: `$Force := mass \cdot gravity == 735.8 \text{ N}$`

## Unit Display (Important!)

**Default:** Results in SI base units. **Use `<!-- [unit] -->` for specific display:**

```markdown
# Define in any unit
$Q := 50\ \text{L/h}$

# Display in SI (default)
$Q ==$                    → 1.389e-05 m³/s

# Display in specific unit
$Q ==$ <!-- [L/h] -->     → 50 L/h
$Q ==$ <!-- [m³/h] -->    → 0.05 m³/h
```

**🚨 Don't manually convert** - just request the display unit!

## Value Display in Tables

Display just the numeric value of a variable (useful for summary tables):

```markdown
| Parameter | Value | Unit |
|-----------|-------|------|
| Flow rate | $ $ <!-- value:Q [m³/h] --> | m³/h |
| Power     | $ $ <!-- value:P_{hyd} [kW] :2 --> | kW |
```

**Output:**

| Parameter | Value | Unit |
|-----------|-------|------|
| Flow rate | $50.00$ | m³/h |
| Power     | $2.86$ | kW |

**Syntax:** `$ $ <!-- value:VAR [unit] :precision -->`
- `$ $` - Empty math block (required)
- `value:VAR` - Variable name in LaTeX notation
- `[unit]` - Optional unit conversion
- `:precision` - Optional decimal places

## Error Handling

LiveMathTeX shows errors inline:
- Undefined variable → `$x ==$ \color{red}{\textbf{Error:} \text{Undefined: x}}`
- Invalid syntax → `$y = 5$ \color{red}{\textbf{Error:} \text{Use := or ==}}`

## More Information

- **[USAGE.md](../../docs/USAGE.md)** - Complete syntax reference
- **[Examples](../../examples/)** - Working examples
- **`/livemathtex-setup`** - Installation guide
