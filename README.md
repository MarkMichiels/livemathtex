# Livemathtex

**Live LaTeX calculations in Markdown documents**

A preprocessor that brings live calculations to Markdown files. Define variables with `:=` and evaluate expressions with `=` — all in beautiful LaTeX notation.

---

## The Problem

Engineers and scientists often need to:
1. **Document calculations** with proper mathematical notation
2. **Keep calculations live** — change an input, all outputs update
3. **Version control** their work (Git-friendly plain text)
4. **Export** to PDF for reports and publications

Current solutions fall short:

| Tool | Math Notation | Live Calc | Git-friendly | Free |
|------|---------------|-----------|--------------|------|
| Mathcad | ✅ Excellent | ✅ Yes | ❌ Binary | ❌ $$$$ |
| Excel | ❌ Poor | ✅ Yes | ❌ Binary | ❌ $ |
| Jupyter | ⚠️ Code-style | ✅ Yes | ⚠️ JSON | ✅ Yes |
| LaTeX | ✅ Excellent | ❌ No | ✅ Yes | ✅ Yes |
| Markdown | ✅ Good (KaTeX) | ❌ No | ✅ Yes | ✅ Yes |

**Livemathtex combines the best:** LaTeX notation + live calculations + plain Markdown.

---

## The Solution

Write calculations in natural mathematical notation:

### Input (`calculation.md`)

```markdown
# Electricity Cost Calculation

## Parameters

$P_{LED} := 3273.6 \text{ kW}$
$t_{year} := 8760 \text{ h}$
$\eta := 0.90$
$price := 0.25 \text{ €/kWh}$

## Annual Energy Consumption

$E_{year} := P_{LED} \cdot t_{year} \cdot \eta$

$E_{year} = ?$

## Annual Cost

$C_{year} := E_{year} \cdot price$

$C_{year} = ?$
```

### Output (after processing)

```markdown
# Electricity Cost Calculation

## Parameters

$P_{LED} := 3273.6 \text{ kW}$
$t_{year} := 8760 \text{ h}$
$\eta := 0.90$
$price := 0.25 \text{ €/kWh}$

## Annual Energy Consumption

$E_{year} := P_{LED} \cdot t_{year} \cdot \eta$

$E_{year} = 25{,}808{,}726.4 \text{ kWh}$

## Annual Cost

$C_{year} := E_{year} \cdot price$

$C_{year} = 6{,}452{,}181.60 \text{ €}$
```

---

## Syntax

### Assignment (`:=`)

Define a variable. No output is shown (like Mathcad's definition operator).

```latex
$x := 42$
$y := x^2 + 2x + 1$
$\alpha := \frac{\pi}{4}$
```

### Evaluation (`=` or `= ?`)

Request the calculated value. Livemathtex fills in the result.

```latex
$y = ?$           → $y = 1849$
$\sin(\alpha) =$  → $\sin(\alpha) = 0.7071$
```

### Units (planned)

```latex
$F := 100 \text{ N}$
$d := 2 \text{ m}$
$W := F \cdot d$
$W = ?$           → $W = 200 \text{ J}$
```

### Symbolic (planned)

```latex
$f(x) := x^2 + 2x + 1$
$f'(x) = ?$       → $f'(x) = 2x + 2$
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Livemathtex Pipeline                       │
└─────────────────────────────────────────────────────────────┘

  input.md          Parser           Engine           output.md
 ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
 │ LaTeX   │ ──── │ Extract │ ──── │ SymPy   │ ──── │ LaTeX   │
 │ + := =  │      │ AST     │      │ Evaluate│      │ + values│
 └─────────┘      └─────────┘      └─────────┘      └─────────┘

Components:
1. Parser     - Extract LaTeX math blocks, detect := and =
2. Translator - Convert LaTeX to SymPy expressions
3. Engine     - SymPy for symbolic/numeric computation
4. Renderer   - Insert results back into LaTeX
```

### Core Dependencies

- **Python 3.10+**
- **SymPy** — Symbolic mathematics engine
- **latex2sympy2** — LaTeX to SymPy parser
- **regex** — Advanced pattern matching

---

## Features

### Phase 1: Core (MVP)

- [ ] Parse Markdown for LaTeX math blocks (`$...$` and `$$...$$`)
- [ ] Detect assignment operator `:=`
- [ ] Detect evaluation operator `=` or `= ?`
- [ ] Variable storage and lookup
- [ ] Basic arithmetic: `+ - * / ^`
- [ ] Common functions: `sin cos tan log exp sqrt`
- [ ] Greek letters: `\alpha \beta \gamma` etc.
- [ ] Number formatting (thousands separator, decimals)
- [ ] CLI: `livemathtex process input.md -o output.md`

### Phase 2: Scientific

- [ ] Units support (SI, imperial, custom)
- [ ] Unit conversion
- [ ] Dimensional analysis (catch unit errors)
- [ ] Symbolic differentiation and integration
- [ ] Matrix operations
- [ ] Summation and product notation

### Phase 3: Integration

- [ ] VS Code extension (live preview)
- [ ] Watch mode (auto-update on save)
- [ ] PDF export (via Pandoc/WeasyPrint)
- [ ] Jupyter kernel (alternative execution)
- [ ] Web playground

### Phase 4: Advanced

- [ ] Tables with calculations
- [ ] Conditional expressions
- [ ] Iteration and solving
- [ ] Custom function definitions
- [ ] Import/include other files
- [ ] Charts/plots from calculated data

---

## Usage

### CLI

```bash
# Process single file
livemathtex process calculation.md

# Output to specific file
livemathtex process calculation.md -o result.md

# Watch mode (auto-update)
livemathtex watch calculation.md

# Export to PDF
livemathtex export calculation.md -o calculation.pdf
```

### Python API

```python
from livemathtex import LivemathtexProcessor

processor = LivemathtexProcessor()
result = processor.process_file("calculation.md")
result.save("output.md")

# Or process string
output = processor.process_string("""
$x := 5$
$y := x^2$
$y = ?$
""")
print(output)
# $x := 5$
# $y := x^2$
# $y = 25$
```

---

## Comparison with Alternatives

| Feature | Livemathtex | Mathcad | SMath | Jupyter | Typst |
|---------|-----------|---------|-------|---------|-------|
| LaTeX notation | ✅ Native | ✅ Yes | ⚠️ Similar | ❌ Code | ⚠️ Own syntax |
| Plain text source | ✅ Markdown | ❌ Binary | ❌ XML | ⚠️ JSON | ✅ Yes |
| Git-friendly | ✅ Yes | ❌ No | ⚠️ Partial | ⚠️ Partial | ✅ Yes |
| Free & open source | ✅ MIT | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Runs offline | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Units support | 🔜 Planned | ✅ Yes | ✅ Yes | ⚠️ Libraries | ⚠️ Package |
| PDF export | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Installation

```bash
# From PyPI (when published)
pip install livemathtex

# From source
git clone https://github.com/MarkMichiels/livemathtex.git
cd livemathtex
pip install -e .
```

---

## Examples

### Engineering Calculation

```markdown
# Beam Deflection Calculator

## Inputs

$E := 200 \times 10^9 \text{ Pa}$      (Young's modulus, steel)
$I := 8.33 \times 10^{-6} \text{ m}^4$  (Second moment of area)
$L := 3 \text{ m}$                      (Beam length)
$P := 10000 \text{ N}$                  (Point load at center)

## Maximum Deflection (simply supported, center load)

$\delta_{max} := \frac{P \cdot L^3}{48 \cdot E \cdot I}$

$\delta_{max} = ?$
```

### Financial Model

```markdown
# Investment Analysis

$principal := 100000$
$rate := 0.07$
$years := 10$

$future\_value := principal \cdot (1 + rate)^{years}$

$future\_value = ?$
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [SPEC.md](docs/SPEC.md) | Full specification and requirements |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture and design |
| [UX.md](docs/UX.md) | User experience and workflow |
| [SYNTAX.md](docs/SYNTAX.md) | Complete syntax reference |
| [DEPENDENCIES.md](docs/DEPENDENCIES.md) | Libraries and technology choices |
| [ROADMAP.md](docs/ROADMAP.md) | Development phases and milestones |
| [EXAMPLES.md](docs/EXAMPLES.md) | Example documents |

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/MarkMichiels/livemathtex.git
cd livemathtex
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **Mathcad** — The original inspiration for live document calculations
- **SymPy** — The powerful symbolic mathematics library
- **latex2sympy2** — LaTeX to SymPy parsing

---

*"Write calculations like a mathematician, version them like a developer."*
