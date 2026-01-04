# Livemathtex Examples

## Quick Start

```bash
# Process the playground file (feel free to edit it!)
python3 -m livemathtex.cli process examples/playground.md
```

## Example Structure

| Directory | Purpose |
|-----------|---------|
| `simple/` | Basic example showing `:=` and `==` operators |
| `playground.md` | **Editable** - experiment here! |

## Static Examples (input → output)

The `simple/` directory contains a before/after demonstration:

- **`input.md`** - Source file (don't process this)
- **`output.md`** - Result after processing

To regenerate the output:
```bash
python3 -m livemathtex.cli process examples/simple/input.md -o examples/simple/output.md
```

## Operators Reference

| Operator | Name | Example |
|----------|------|---------|
| `:=` | Definition | `$x := 10$` |
| `==` | Evaluation | `$x + 5 ==$` → `$x + 5 == 15$` |
| `=>` | Symbolic | `$x + x =>$` → `$x + x => 2x$` |

## Unit Conversion

Use HTML comments to request specific units:

```markdown
$F ==$ <!-- [N] -->
```

The comment stays in the source but is invisible when rendered.
