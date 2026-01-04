# LiveMathTeX

**Live LaTeX calculations in Markdown — built for the AI era**

| | |
|---|---|
| **Status** | ✅ Core implementation complete |
| **Version** | 0.1.0 (alpha) |
| **Built with** | AI assistance (Claude/Cursor) |

---

## The Core Idea

You don't write LaTeX by hand anymore — **LLMs do**.

But when an LLM generates a calculation, where do the numbers come from? You have to trust it, or run Python separately to verify. The formula and the result are disconnected.

**LiveMathTeX connects them.** AI generates the LaTeX formulas, LiveMathTeX computes the results. Everything stays in one Markdown file — verifiable, traceable, Git-friendly.

---

## Quick Example

**You (to LLM):** "Calculate force for 5 kg at 9.81 m/s²"

**LLM generates:**

```markdown
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a$
$F ==$
```
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a$
$F ==$

**After `livemathtex process`:**

```markdown
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a$
$F == 49.05 \text{ N}$
```

$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a$
$F == 49.05 \text{ N}$

**The result is computed, not typed.** Change $m$ → $F$ updates automatically.

---

## Why This Matters

| Traditional LLM output | With LiveMathTeX |
|------------------------|------------------|
| "The force is **49.05 N**" (trust me) | `$F = 49.05 \text{ N}$` (computed from formula) |
| Separate Python to verify | Formula and result in one place |
| Edit text → numbers become stale | Edit input → outputs auto-update |
| Binary tools or JSON notebooks | Plain Markdown, Git-friendly |

**Jupyter?** Great for code, but:
- `F = m * a` isn't what you put in a report — LaTeX renders beautifully
- JSON format loses all Markdown advantages: plain text, Git diffs, extensible tooling
- Markdown is an ecosystem — combine with Pandoc, static site generators, documentation tools

LaTeX is the universal language for math. LLMs already speak it fluently. Keep everything in Markdown.

---

## Syntax

Three operators. That's it.

| Operator | Meaning | Input | Output |
|----------|---------|-------|--------|
| `:=` | Define | `$x := 42$` | `$x := 42$` (unchanged) |
| `==` | Evaluate | `$x ==$` | `$x == 42$` (result filled in) |
| `:= ==` | Define + evaluate | `$y := x^2 ==$` | `$y := x^2 == 1764$` |
| `:=` | Define function | `$f(x) := x^2 + 2x$` | `$f(x) := x^2 + 2x$` |
| `=>` | Symbolic | `$f'(x) =>$` | `$f'(x) => 2x + 2$` |

**Notes:**
- Results are **overwritten** on re-run
- Unit support with SI default (see [USAGE.md](docs/USAGE.md) for details)

> ⚠️ **Why `==` not `=`?** Safety. You can't accidentally overwrite a variable by forgetting the `:` in `:=`.

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

## Usage

### CLI

```bash
# Process and update in place
livemathtex process calculation.md

# Output to specific file
livemathtex process calculation.md -o result.md

# Debug mode - writes IR (Intermediate Representation) to JSON
livemathtex process calculation.md --verbose
# Creates: calculation.lmt.json with all symbol values and mappings

# Inspect the IR
livemathtex inspect calculation.lmt.json
```

### Python API

```python
from livemathtex.core import process_text

output, ir = process_text("""
$x := 5$
$y := x^2 ==$
""")
# output: Markdown with results
# ir: LivemathIR with all symbol values

# Access computed values
print(ir.symbols['y'].value)  # 25.0
```

### With AI assistants

The typical workflow:

1. **Ask LLM** to set up a calculation (it generates the LaTeX)
2. **Run** `livemathtex process` to compute results
3. **Iterate** — adjust values, re-run, results update

You're not writing LaTeX by hand — you're reviewing and tweaking AI-generated formulas.

---

## Features

### Done

- [x] Project design and specification
- [x] Parse Markdown for LaTeX math blocks
- [x] Assignment (`:=`) and evaluation (`==`) operators
- [x] Variable storage and lookup
- [x] Basic arithmetic and common functions (sin, cos, log, sqrt, etc.)
- [x] Error handling (undefined variables, syntax errors, unit conflicts)
- [x] CLI: `livemathtex process`
- [x] SI units support (kg, m, s, N, etc.)
- [x] Unit conversion via HTML comments (`<!-- [mm] -->`)
- [x] Greek letter support (Δ, α, θ, etc.)
- [x] Complex subscripts (T_{h,in}, etc.)
- [x] IR (Intermediate Representation) layer for debugging
- [x] `--verbose` flag for JSON debug output

### In Progress

- [ ] Symbolic differentiation (`=>`)
- [ ] Watch mode

### Future

- [ ] **Import system** - Import symbols from other Markdown files via IR JSON
- [ ] VS Code extension

**Import System Preview:**
```bash
# 1. Create library: constants.md with $g := 9.81$ etc.
# 2. Process: livemathtex process constants.md --verbose
# 3. Import: livemathtex process calc.md --import constants.lmt.json
```

See [ROADMAP.md](docs/ROADMAP.md) for full details.

---

## What LiveMathTeX Does NOT Do

| Out of Scope | Why | Use Instead |
|--------------|-----|-------------|
| PDF export | Pandoc excels at this | `pandoc output.md -o output.pdf` |
| Live editor | VS Code + extensions exist | Markdown Preview Enhanced |
| GUI | Separate project | Build on top of LiveMathTeX |
| Plotting | Many libraries exist | Matplotlib, Plotly |

**Philosophy:** Do one thing well. The calculation engine. Everything else can build on top.

---

## Documentation

| Document | Description |
|----------|-------------|
| [BACKGROUND.md](docs/BACKGROUND.md) | Research: what we tried and why we built this |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical design |
| [USAGE.md](docs/USAGE.md) | Syntax, workflow, and examples |
| [ROADMAP.md](docs/ROADMAP.md) | Development phases |
| [DEPENDENCIES.md](docs/DEPENDENCIES.md) | Libraries and tools |

---

## Contributing

```bash
git clone https://github.com/MarkMichiels/livemathtex.git
cd livemathtex
pip install -e ".[dev]"
pytest
```

---

## License

MIT License — See [LICENSE](LICENSE)

---

*"AI writes the math. LiveMathTeX computes the results."*
