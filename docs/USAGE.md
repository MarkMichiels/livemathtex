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
| `===` | Unit definition | `$€ === €$` | (defines custom unit) |

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

## Library Usage (Python API)

LiveMathTeX can be used as a Python library for programmatic document processing.

### Installation

```bash
pip install -e .  # or pip install livemathtex when published
```

### Quick Start

```python
from livemathtex import process_text

content = """
$m := 5\\ \\text{kg}$
$a := 9.81\\ \\text{m/s}^2$
$F := m \\cdot a ==$
"""

output, ir = process_text(content)
print(output)
# $m := 5\ \text{kg}$
# $a := 9.81\ \text{m/s}^2$
# $F := m \cdot a == 49.05\ \text{kg} \cdot \text{m} / \text{s}^{2}$
```

### Public API

#### Processing Functions

**`process_text(content: str, source: str = "<string>") -> tuple[str, LivemathIR]`**

Process markdown content from a string.

- `content`: Markdown with LiveMathTeX calculations
- `source`: Source identifier for debugging (optional)
- Returns: `(rendered_output, ir)` tuple

```python
from livemathtex import process_text

output, ir = process_text("$x := 5$\n$y := x^2 ==$")
print(output)  # Markdown with results
print(ir.stats)  # Processing statistics
```

**`process_text_v3(content: str, source: str = "<string>", config: LivemathConfig = None) -> tuple[str, LivemathIRV3]`**

Process with v3.0 IR schema (Pint-based units, detailed custom unit metadata).

```python
from livemathtex import process_text_v3, LivemathConfig

config = LivemathConfig(digits=6)
output, ir = process_text_v3("$x := 123.456789 ==$", config=config)
```

**`process_file(input_path: str, output_path: str = None, verbose: bool = False, ir_output_path: str = None) -> LivemathIR`**

Process a markdown file directly.

- `input_path`: Path to input markdown file
- `output_path`: Path for output file (default: uses config or timestamped)
- `verbose`: If True, write IR JSON file
- `ir_output_path`: Custom path for IR JSON
- Returns: `LivemathIR` with all symbol values

```python
from livemathtex import process_file

ir = process_file("calculation.md", output_path="result.md", verbose=True)
print(f"Processed {ir.stats['symbols']} symbols")
```

#### Configuration

**`LivemathConfig`**

Configuration options for processing.

```python
from livemathtex import LivemathConfig

config = LivemathConfig(
    digits=4,           # Significant figures (default: 4)
    format="general",   # general/decimal/scientific/engineering
    output="inplace",   # Output mode: inplace/timestamped/path
    json=False,         # Generate IR JSON file
)
```

Configuration hierarchy (highest priority first):
1. Expression-level: `$x ==$ <!-- digits:6 -->`
2. Document directives: `<!-- livemathtex: digits=6 -->`
3. Config file: `.livemathtex.toml`
4. Passed `LivemathConfig` object
5. Defaults

#### Result Types

**`LivemathIR`** (v2.0)

Intermediate Representation with symbol values and errors.

```python
from livemathtex import process_text

output, ir = process_text(content)

# Access symbols
for name, entry in ir.symbols.items():
    print(f"{name}: {entry.original.value} {entry.original.unit}")
    print(f"  SI: {entry.si.value} {entry.si.unit}")
    print(f"  Valid: {entry.valid}")

# Access errors
for error in ir.errors:
    print(f"Line {error.line}: {error.message}")

# Processing stats
print(ir.stats)
# {'symbols': 3, 'definitions': 2, 'evaluations': 1, 'errors': 0, ...}
```

**`LivemathIRV3`** (v3.0)

Enhanced IR with Pint-based unit conversion and custom unit metadata.

```python
from livemathtex import process_text_v3

output, ir = process_text_v3(content)

# Custom units with full metadata
for name, unit in ir.custom_units.items():
    print(f"{name}: {unit.type} - {unit.pint_definition}")

# Symbols with Pint conversion info
for id, entry in ir.symbols.items():
    print(f"{entry.latex_name}:")
    print(f"  Original: {entry.original.value} {entry.original.unit}")
    print(f"  Base: {entry.base.value} {entry.base.unit}")
    print(f"  Conversion OK: {entry.conversion_ok}")
```

### Examples

#### Basic Text Processing

```python
from livemathtex import process_text

content = """
# Physics Calculation

$m := 10\\ \\text{kg}$
$v := 5\\ \\text{m/s}$
$E_k := \\frac{1}{2} m v^2 ==$
"""

output, ir = process_text(content)
print(output)
```

#### Processing with Custom Config

```python
from livemathtex import process_text_v3, LivemathConfig

# High precision engineering format
config = LivemathConfig(digits=6, format="engineering")

content = "$P := 1234567.89 ==$"
output, ir = process_text_v3(content, config=config)
```

#### Accessing Symbol Values

```python
from livemathtex import process_text

content = """
$Q := 50\\ \\text{m}^3/\\text{h}$
$\\rho := 1000\\ \\text{kg/m}^3$
$\\dot{m} := Q \\cdot \\rho ==$
"""

output, ir = process_text(content)

# Get mass flow rate value
for name, entry in ir.symbols.items():
    if "dot{m}" in name:
        print(f"Mass flow: {entry.si.value} {entry.si.unit}")
```

#### Error Handling

```python
from livemathtex import process_text

content = """
$x := undefined_var + 5 ==$
"""

output, ir = process_text(content)

if ir.errors:
    for error in ir.errors:
        print(f"Error on line {error.line}: {error.message}")
else:
    print("Processing successful")
```

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

### Unit Definition (`===`)

Defines custom units that can be used in calculations.

**Base unit (new unit):**
```latex
$$ € === € $$
$$ dollar === dollar $$
```

**Derived unit (from existing):**
```latex
$$ mbar === bar / 1000 $$
$$ kPa === Pa * 1000 $$
```

**Compound unit:**
```latex
$$ kWh === kW \cdot h $$
$$ mg_per_L === mg / L $$
```

**Alias (rename existing):**
```latex
$$ dag === day $$
$$ uur === hour $$
```

**Pattern recognition:**

| Pattern | Meaning | Example |
|---------|---------|---------|
| `X === X` | New base unit | `€ === €` |
| `X === Y / n` | Derived (scaled) | `mbar === bar/1000` |
| `X === Y * Z` | Compound | `kWh === kW * h` |
| `X === Y` | Alias | `dag === day` |

**Built-in units:** SymPy provides most SI and common units. Use `===` for:
- Currency (euro, dollar)
- Non-standard abbreviations (dag → day)
- Domain-specific units

### Using Units in Calculations

Units can be attached to values and will propagate through calculations automatically:

```latex
$$ € === € $$                           <!-- Define euro as a unit -->
$$ kWh === kW \cdot h $$                <!-- Define kWh as compound unit -->

$$ prijs := 0.139\ €/kWh $$             <!-- Unit attached with backslash-space -->
$$ energie := 1500\ kWh $$

$$ kosten := prijs \cdot energie == $$  <!-- Units propagate automatically! -->
```

**Output:**
```latex
$$ kosten := prijs \cdot energie == 208.5\ \text{€} $$
```

**Unit attachment patterns:**

| Pattern | Example | Note |
|---------|---------|------|
| `number\ unit` | `0.139\ €/kWh` | Backslash-space (recommended) |
| `number \text{unit}` | `100\ \text{kg}` | Explicit text wrapper |
| `number unit` | `5 kg` | Direct (works for simple units) |

**Unit propagation rules:**

- **Multiplication:** `€/kWh * kWh = €` (kWh cancels)
- **Division:** `m / s = m/s` (creates compound unit)
- **SI conversion:** Results are simplified to SI base units when possible

**Example with area calculation:**

```latex
$$ hoogte := 2\ m $$
$$ breedte := 3\ m $$
$$ oppervlakte := hoogte \cdot breedte == $$  <!-- 6.0 m² -->
```

**See also:** `examples/custom-units/` and `examples/unit-library/` for complete examples.

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

## Configuration

LiveMathTeX uses a hierarchical configuration system. The key principle is that **documents are self-contained**: the same input produces the same output regardless of who processes it.

### Configuration Hierarchy

From highest to lowest priority:

```
1. CLI -o flag               (output path only)
2. Expression-level          <!-- digits:6 -->
3. Document directives       <!-- livemathtex: ... -->
4. Local config              .livemathtex.toml
5. Project config            pyproject.toml
6. User config               ~/.config/livemathtex/
7. Defaults
```

### Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `digits` | int | 4 | Significant figures (1-15) |
| `format` | enum | "general" | general/decimal/scientific/engineering |
| `exponential_threshold` | int | 9 | Exponent threshold for scientific notation (10^9 = billion) |
| `trailing_zeros` | bool | false | Show zeros to fill precision |
| `unit_system` | enum | "SI" | SI/imperial/CGS |
| `timeout` | int | 5 | Seconds per expression |
| `output` | string | "timestamped" | Output mode |
| `json` | bool | false | Generate `.lmt.json` IR file for debugging |

### Output Modes

| Value | Behavior | Use Case |
|-------|----------|----------|
| `"timestamped"` | `input_20260106_2045.md` | **Default** - safe |
| `"inplace"` | Overwrite input | Explicit opt-in |
| `"output.md"` | Specific file | Examples, CI |

### Expression-Level Overrides

Override formatting for individual calculations:

```markdown
$P := 123456.789 ==$ <!-- digits:6 -->
$E := 0.00001234 ==$ <!-- format:sci -->
$Q := 50.123 ==$ <!-- digits:6 [m³/h] -->
```

### Document Directives

Set document-wide defaults at the top:

```markdown
<!-- livemathtex: digits=6, format=engineering -->
<!-- livemathtex: output=inplace -->

# My Calculations
$x := 5 ==$
```

### ⭐ Preferred Method: Settings in Document

**The recommended approach is to put ALL settings directly in the document using document directives.**

This follows the principle that **documents should be self-contained**:

```markdown
<!-- livemathtex: output=output.md, json=true -->

# My Engineering Calculation

This document contains everything needed to reproduce the calculation:
- The input values
- The formulas
- The configuration settings
```

**Why document directives are preferred:**

| Approach | Portable | Visible | Version Controlled |
|----------|----------|---------|-------------------|
| Document directive | ✅ | ✅ | ✅ |
| `.livemathtex.toml` | ⚠️ Separate file | ❌ Hidden | ⚠️ Easy to forget |
| `pyproject.toml` | ⚠️ Project-wide | ❌ Hidden | ⚠️ Affects all docs |
| User config | ❌ Machine-specific | ❌ Hidden | ❌ Not tracked |

**Common document directive patterns:**

```markdown
<!-- livemathtex: output=output.md, json=true -->
<!-- livemathtex: digits=6, format=engineering -->
<!-- livemathtex: output=inplace -->
```

**Note:** External config files (`.livemathtex.toml`, `pyproject.toml`) are still supported for project-wide defaults, but document directives take precedence and make documents portable.

### Config Files (Alternative)

**.livemathtex.toml** (in document directory):

```toml
digits = 6
format = "engineering"
output = "output.md"

[units]
system = "SI"
```

**pyproject.toml**:

```toml
[tool.livemathtex]
digits = 4
timeout = 10
```

**User config** (~/.config/livemathtex/config.toml):

```toml
digits = 4
output = "inplace"
```

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
Source: engineering-units/input.md
Version: 3.0
Unit backend: pint 0.25.2

Symbols:
  v_{0} (Q):
    original: 50.0 m³/h
    base: 0.0138889 [meter ** 3 / second]
    conversion_ok: ✓

Stats:
  definitions: 19
  evaluations: 11
  value_refs: 7
  errors: 0
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Output Markdown file (overrides config; if omitted uses document/config `output`, default: `"timestamped"`) |
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

Use `--verbose` to generate a JSON file containing the Intermediate Representation:

```bash
livemathtex process input.md --verbose
```

Or use the `json=true` document directive:

```markdown
<!-- livemathtex: output=output.md, json=true -->
```

This creates `input.lmt.json`.

### IR Schema v3.0 (Current)

Version 3.0 uses Pint for unit handling and includes full custom unit metadata:

```json
{
  "version": "3.0",
  "source": "input.md",
  "unit_backend": {
    "name": "pint",
    "version": "0.25.2"
  },

  "custom_units": {
    "€": {
      "latex": "€",
      "type": "base",
      "pint_definition": "€ = [€]",
      "line": 5
    },
    "kWh": {
      "latex": "kWh",
      "type": "alias",
      "pint_definition": "kWh = kW * hour",
      "line": 6
    }
  },

  "symbols": {
    "v_{0}": {
      "latex_name": "Q",
      "original": { "value": 50.0, "unit": "m³/h" },
      "base": { "value": 0.01389, "unit": "meter ** 3 / second" },
      "conversion_ok": true,
      "line": 31
    },
    "v_{1}": {
      "latex_name": "\\rho",
      "original": { "value": 1000.0, "unit": "kg/m³" },
      "base": { "value": 1000.0, "unit": "kilogram / meter ** 3" },
      "conversion_ok": true,
      "line": 32
    }
  },

  "errors": [],
  "stats": {
    "last_run": "2026-01-07 14:30:00",
    "symbols": 2,
    "custom_units": 2
  }
}
```

### IR v3.0 Schema Structure

| Field | Description |
|-------|-------------|
| `version` | Schema version ("3.0") |
| `source` | Input file path |
| `unit_backend` | Unit library info (`{name, version}`) |
| `custom_units` | User-defined units with full metadata |
| `symbols` | All defined variables (keyed by internal ID) |
| `errors` | List of errors with line numbers |
| `stats` | Processing statistics |

### Symbol Entry Fields (v3.0)

Each symbol in `symbols` contains:

| Field | Description |
|-------|-------------|
| `latex_name` | Original LaTeX name (e.g., `P_{LED,out}`) |
| `original.value` | Numeric value as entered |
| `original.unit` | Unit as entered (e.g., "m³/h") |
| `base.value` | SI-converted numeric value (Pint) |
| `base.unit` | Pint base unit expression |
| `conversion_ok` | Whether unit conversion succeeded |
| `line` | Source line number |
| `formula` | (optional) Formula info for computed values |

### Custom Unit Entry Fields (v3.0)

Each custom unit in `custom_units` contains:

| Field | Description |
|-------|-------------|
| `latex` | LaTeX representation |
| `type` | Unit type: "base", "derived", "compound", or "alias" |
| `pint_definition` | Pint-compatible definition string |
| `line` | Source line number |

### Symbol Mapping

LiveMathTeX uses a simple `v_{n}` / `f_{n}` naming scheme for reliable parsing:

| Type | Pattern | Example LaTeX | Internal |
|------|---------|---------------|----------|
| **Variables** | `v_{n}` | `P_{LED,out}` | `v_{0}` |
| **Functions** | `f_{n}` | `\eta_{PSU}(x)` | `f_{0}` |

The key in `symbols` is the **internal ID**, and `latex_name` is the display name:

```json
{
  "symbols": {
    "v_{0}": {
      "latex_name": "P_{LED,out}",
      "original": { "value": 123.45, "unit": "W" },
      "base": { "value": 123.45, "unit": "watt" },
      "conversion_ok": true,
      "line": 15
    }
  }
}
```

This approach ensures:
- **100% parsing success** - `v_{0}` always parses correctly
- **Any LaTeX supported** - Greek, subscripts, commas, slashes all work
- **Debugging clarity** - IR shows full mapping with original and base units
- **Pint integration** - Unit conversion validated by Pint

### Inspecting Results

```bash
livemathtex inspect input.lmt.json
```

Shows all symbols, their values, and any errors in a human-readable format.

### IR Schema v2.0 (Legacy)

Version 2.0 is still supported for backward compatibility. See [ARCHITECTURE.md](../.planning/codebase/ARCHITECTURE.md) for details.

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

### Mathematical Functions

```
sin, cos, tan, asin, acos, atan
sinh, cosh, tanh
log, ln, exp, sqrt
abs, floor, ceil, round
min, max, sum, prod
diff, integrate, solve, simplify
det, inv, transpose
```

### Constants

```
pi, e, i
true, false
```

### Unit Names (Pint Registry)

**Important:** All unit names recognized by Pint are reserved. This includes:

- **SI base units:** `m`, `kg`, `s`, `A`, `K`, `mol`, `cd`
- **SI derived units:** `N`, `J`, `W`, `Pa`, `V`, `F`, `ohm`, etc.
- **Prefixed units:** `km`, `mm`, `MHz`, `kW`, `mg`, etc.
- **Common abbreviations:** `L` (liter), `h` (hour), `min`, `bar`, etc.
- **Legacy units:** `a` (year/annum), `b` (barn), etc.

To check if a name conflicts with a unit:

```bash
livemathtex process input.md
# Error: Variable name 'a' conflicts with unit 'year' (annum)
```

**Best practice:** Use descriptive names with subscripts:

```latex
$m_{rock} := 5\ kg$        <!-- OK: not 'm' but 'm_rock' -->
$a_1 := 10$                <!-- OK: not 'a' but 'a_1' -->
$mass_{obj} := 2\ kg$      <!-- OK: not 'mass' but 'mass_obj' -->
```

See also: [PINT_MIGRATION_ANALYSIS.md](../.planning/history/PINT_MIGRATION_ANALYSIS.md) for details on unit validation.

---

## Plain Text Benefits

- Source files readable without tools
- Version control friendly (Git diffs work)
- Searchable text
- Works offline
- No proprietary formats

---

## Import System (Planned)

Import definitions from other LiveMathTeX documents to share unit libraries, constants, and formulas.

### Basic Usage

```markdown
<!-- livemathtex: import=./units/currency.md -->
<!-- livemathtex: import=../shared/constants.md -->
```

The imported file is processed first, making all its definitions available:
- **Unit definitions** (`===`) - Custom units like `€`, `dag`
- **Variable assignments** (`:=`) - Constants like `g := 9.81\ m/s^2`
- **Function definitions** (`:=`) - Reusable formulas

### Relative Paths

Paths are relative to the importing document:

```
project/
├── units/
│   └── industrial.md      # Unit definitions
├── constants/
│   └── physics.md         # Physical constants
└── calculations/
    └── analysis.md        # <- import=../units/industrial.md
```

### Example Unit Library

Create a unit library file (`units/currency.md`):

```markdown
<!-- livemathtex: output=currency_output.md -->

## Currency Units

$$ € === € $$
$$ dollar === dollar $$
$$ cent === € / 100 $$

## Dutch Aliases

$$ dag === day $$
```

Use in your document:

```markdown
<!-- livemathtex: import=./units/currency.md -->

## Cost Calculation

$$ price := 150\ € $$
$$ quantity := 100 $$
$$ total := price \cdot quantity == $$
```

### Current Workaround

Until import is implemented, copy unit definitions to the top of each document.

See `examples/unit-library/input.md` for a comprehensive unit library template.

**Status:** See [ROADMAP.md - Phase 2.3](../.planning/ROADMAP.md) for implementation timeline.

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
