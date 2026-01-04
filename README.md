# LiveMathTeX

**Mathcad meets Markdown — live LaTeX calculations in plain text**

| | |
|---|---|
| **Status** | ✅ Core implementation complete |
| **Version** | 0.1.0 (alpha) |

---

## Why LiveMathTeX?

I used to work a lot with Mathcad — live calculations embedded in documentation. Powerful, but proprietary and not Git-friendly.

Then I discovered Markdown: plain text, version control, works everywhere. My philosophy became: **keep everything in Markdown**.

But I couldn't find a tool that combined both worlds: the calculation power of Mathcad with the simplicity of Markdown. LaTeX handles the notation beautifully, but doesn't compute. Jupyter computes, but uses JSON notebooks instead of plain Markdown.

So I built LiveMathTeX: write formulas in LaTeX notation, get computed results, stay in Markdown. Whether you write the formulas yourself or let an AI assistant generate them — the calculations are always verifiable and traceable.

---

## Quick Start

```bash
# Install
pip install -e .

# Process a file
livemathtex process calculation.md
```

**Using Cursor/AI assistant?** Type `/livemathtex-setup` for guided installation.

---

## Example

**Input:**
```markdown
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a ==$
```
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a ==$

**After processing:**
```markdown
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a == 49.05 \text{ N}$
```
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a == 49.05 \text{ N}$

**The result is computed, not typed.** Change $m$ → $F$ updates automatically.

---

## Syntax

Three operators. That's it.

| Operator | Meaning | Example |
|----------|---------|---------|
| `:=` | Define | `$x := 42$` |
| `==` | Evaluate | `$x ==$` → `$x == 42$` |
| `=>` | Symbolic | `$f'(x) =>$` (future) |

> ⚠️ **Why `==` not `=`?** Safety. A bare `=` gives an error to prevent accidents.

---

## Features

- ✅ LaTeX math in Markdown
- ✅ SI units (kg, m, s, N, etc.)
- ✅ Greek letters (Δ, α, θ)
- ✅ Functions (sin, cos, log, sqrt)
- ✅ Error handling with clear messages
- ✅ Debug mode (`--verbose`)

---

## What LiveMathTeX Does NOT Do

| Out of Scope | Use Instead |
|--------------|-------------|
| PDF export | `pandoc output.md -o output.pdf` |
| Live editor | Markdown Preview Enhanced |
| Plotting | Matplotlib |

**Philosophy:** Do one thing well — the calculation engine.

---

## Documentation

| Document | Description |
|----------|-------------|
| [`/livemathtex`](.cursor/commands/livemathtex.md) | Process files (Cursor command) |
| [`/livemathtex-setup`](.cursor/commands/livemathtex-setup.md) | Installation (Cursor command) |
| [SETUP.md](docs/SETUP.md) | Detailed installation |
| [USAGE.md](docs/USAGE.md) | Complete syntax reference |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical design |
| [ROADMAP.md](docs/ROADMAP.md) | Development phases |

---

## License

MIT License — See [LICENSE](LICENSE)

---

*"Write the formula once. Get the result everywhere."*
