# Livemathtex

**Live LaTeX calculations in Markdown — built for the AI era**

| | |
|---|---|
| **Status** | 🚧 Design phase — documentation complete, implementation not started |
| **Version** | 0.0.0 (pre-alpha) |
| **Built with** | AI assistance (Claude/Cursor) |

---

## The Core Idea

You don't write LaTeX by hand anymore — **LLMs do**.

But when an LLM generates a calculation, where do the numbers come from? You have to trust it, or run Python separately to verify. The formula and the result are disconnected.

**Livemathtex connects them.** AI generates the LaTeX formulas, Livemathtex computes the results. Everything stays in one Markdown file — verifiable, traceable, Git-friendly.

---

## Quick Example

**You (to LLM):** "Calculate force for 5 kg at 9.81 m/s²"

**LLM generates:**

```markdown
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a =$
```

> $m := 5 \text{ kg}$
> $a := 9.81 \text{ m/s}^2$
> $F := m \cdot a =$

**After `livemathtex process`:**

```markdown
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$
$F := m \cdot a = 49.05 \text{ N}$
```

> $m := 5 \text{ kg}$
> $a := 9.81 \text{ m/s}^2$
> $F := m \cdot a = 49.05 \text{ N}$

**The result is computed, not typed.** Change $m$ → $F$ updates. No disconnect.

---

## Why This Matters

| Traditional LLM output | With Livemathtex |
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

| Operator | Meaning | Example |
|----------|---------|---------|
| `:=` | Assign (define) | `$x := 42$` |
| `=` | Evaluate (compute) | `$y = 1764$` |
| `=>` | Symbolic (show derivation) | `$f'(x) => 2x + 2$` |

### Assignment

```latex
$x := 42$
$\alpha := \frac{\pi}{4}$
$E := 200 \times 10^9 \text{ Pa}$
```

### Evaluation

```latex
$y := x^2$
$y =$           → Livemathtex fills in: $y = 1764$
```

### Symbolic (planned)

```latex
$f(x) := x^2 + 2x + 1$
$f'(x) =>$      → Livemathtex shows: $f'(x) = 2x + 2$
```

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

## Usage

### CLI

```bash
# Process and update in place
livemathtex process calculation.md

# Output to specific file
livemathtex process calculation.md -o result.md

# Watch mode (auto-update on save)
livemathtex watch calculation.md
```

### Python API

```python
from livemathtex import process

output = process("""
$x := 5$
$y := x^2$
$y =$
""")
# Returns: $x := 5$  $y := x^2$  $y = 25$
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

### Phase 1: Core (MVP)

- [ ] Parse Markdown for LaTeX math blocks
- [ ] Assignment (`:=`) and evaluation (`=`) operators
- [ ] Variable storage and lookup
- [ ] Basic arithmetic and common functions
- [ ] Error handling (undefined variables, syntax errors)
- [ ] CLI: `livemathtex process`

### Phase 2: Scientific

- [ ] Units (SI, imperial, custom)
- [ ] Symbolic differentiation (`=>`)
- [ ] Matrix operations

### Phase 3: Integration

- [ ] VS Code extension
- [ ] Watch mode

See [ROADMAP.md](docs/ROADMAP.md) for full details.

---

## What Livemathtex Does NOT Do

| Out of Scope | Why | Use Instead |
|--------------|-----|-------------|
| PDF export | Pandoc excels at this | `pandoc output.md -o output.pdf` |
| Live editor | VS Code + extensions exist | Markdown Preview Enhanced |
| GUI | Separate project | Build on top of Livemathtex |
| Plotting | Many libraries exist | Matplotlib, Plotly |

**Philosophy:** Do one thing well. The calculation engine. Everything else can build on top.

---

## Documentation

| Document | Description |
|----------|-------------|
| [BACKGROUND.md](docs/BACKGROUND.md) | Research: what we tried and why we built this |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical design |
| [SYNTAX.md](docs/SYNTAX.md) | Complete syntax reference |
| [EXAMPLES.md](docs/EXAMPLES.md) | Example calculations |
| [ROADMAP.md](docs/ROADMAP.md) | Development phases |

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

*"AI writes the math. Livemathtex computes the results."*
