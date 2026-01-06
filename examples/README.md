# LiveMathTeX Examples

## Quick Start

```bash
# Install livemathtex
pip install -e .

# Process the playground file (feel free to edit it!)
livemathtex process examples/playground.md
```

## Example Structure

| Directory | Purpose |
|-----------|---------|
| `simple/` | Basic arithmetic with multi-letter variables |
| `simple-units/` | Simple calculations with SI units |
| `engineering/` | Shell-and-tube heat exchanger design |
| `engineering-units/` | Pump sizing with unit conversions |
| `settings/` | **Configuration settings demo** (digits, format) |
| `units/` | **Custom unit definitions** (`===` syntax) |
| `playground.md` | **Editable** - experiment here! |

## Static Examples (input → output)

Each directory contains a before/after demonstration:

- **`input.md`** - Source file (don't process this directly)
- **`output.md`** - Result after processing

To regenerate outputs (each example has a `.livemathtex.toml` that sets `output = "output.md"`):
```bash
livemathtex process examples/simple/input.md
livemathtex process examples/simple-units/input.md
livemathtex process examples/engineering/input.md
livemathtex process examples/engineering-units/input.md
livemathtex process examples/settings/input.md
livemathtex process examples/units/input.md
```

## Operators Reference

| Operator | Name | Example |
|----------|------|---------|
| `:=` | Definition | `$x := 10$` |
| `==` | Evaluation | `$x + 5 ==$` → `$x + 5 == 15$` |
| `=>` | Symbolic | `$x + x =>$` → `$x + x => 2x$` |
| `===` | Unit definition | `$€ === €$` (new unit) |

## SI Units Support

LiveMathTeX recognizes SI units: `kg`, `m`, `s`, `N`, `J`, `W`, `Pa`, `Hz`, `V`, `A`, `K`, `mol`

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

## Configuration Settings

LiveMathTeX supports flexible configuration via expression-level overrides.

### Expression-Level Overrides

Override settings for individual calculations:

```markdown
$result ==$ <!-- digits:6 format:scientific -->
```

### Available Settings

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| `digits` | 1-15 | 4 | Significant figures |
| `format` | `general`, `decimal`, `scientific` (`sci`), `engineering` (`eng`) | `general` | Number format |

### Examples

```markdown
$x := 123456.789 ==$                        <!-- default: 1.235e+05 -->
$x ==$ <!-- digits:6 -->                    <!-- 123457 -->
$x ==$ <!-- format:scientific -->           <!-- 1.235e+05 -->
$x ==$ <!-- format:engineering -->          <!-- 123.5e3 -->
$x ==$ <!-- digits:2 format:decimal -->     <!-- 123456.79 -->
```

See `examples/settings/` for a complete demonstration of all configuration options.
