# Livemathtex Examples

## Quick Start

```bash
# Process the playground file (feel free to edit it!)
python3 -m livemathtex.cli process examples/playground.md
```

## Example Structure

| Directory | Purpose |
|-----------|---------|
| `simple/` | Basic arithmetic with multi-letter variables |
| `physics/` | Force calculation with SI units (kg, m, s) |
| `playground.md` | **Editable** - experiment here! |

## Static Examples (input → output)

Each directory contains a before/after demonstration:

- **`input.md`** - Source file (don't process this directly)
- **`output.md`** - Result after processing

To regenerate outputs:
```bash
python3 -m livemathtex.cli process examples/simple/input.md -o examples/simple/output.md
python3 -m livemathtex.cli process examples/physics/input.md -o examples/physics/output.md
```

## Operators Reference

| Operator | Name | Example |
|----------|------|---------|
| `:=` | Definition | `$x := 10$` |
| `==` | Evaluation | `$x + 5 ==$` → `$x + 5 == 15$` |
| `=>` | Symbolic | `$x + x =>$` → `$x + x => 2x$` |

## SI Units Support

Livemathtex recognizes SI units: `kg`, `m`, `s`, `N`, `J`, `W`, `Pa`, `Hz`, `V`, `A`, `K`, `mol`

```markdown
$mass := 10 \cdot kg$
$accel := 9.81 \cdot \frac{m}{s^2}$
$F := mass \cdot accel ==$
```

Result: `$F := ... == 98.1 \frac{kg \cdot m}{s^2}$`

### ⚠️ Reserved Names

**Do NOT use SI unit symbols as variable names!** These will produce an error:

```markdown
$m := 10$      ❌ Error: 'm' conflicts with meter
$s := 5$       ❌ Error: 's' conflicts with second
$mass := 10$   ✓ OK
$time := 5$    ✓ OK
```

## Unit Conversion (experimental)

Use HTML comments to request specific units:

```markdown
$F ==$ <!-- [N] -->
```

The comment stays in the source but is invisible when rendered.
