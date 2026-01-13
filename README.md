# LiveMathTeX

**Mathcad-style recalculation for Markdown — LaTeX in, computed LaTeX out.**

| | |
|---|---|
| **Status** | Alpha (usable; interfaces may change) |
| **Version** | 1.6.0 |
| **Requires** | Python 3.10+ |

LiveMathTeX is a small CLI that reads a Markdown file, evaluates LaTeX-style calculations (with units), and writes the results back into Markdown.
The document stays plain text: easy to diff, review, and archive.

<!-- livemathtex: output=timestamped -->

---

## Quick example

Input (`calculation.md`):

```markdown
$m_1 := 5\ \text{kg}$
$a_1 := 9.81\ \text{m/s}^2$
$F_1 := m_1 \cdot a_1$
$F_1 ==$ <!-- [N] -->
```

The `<!-- [N] -->` comment requests the display unit (it stays in the source, but is invisible when rendered).

Rendered:

$m_1 := 5\ \text{kg}$

$a_1 := 9.81\ \text{m/s}^2$

$F_1 := m_1 \cdot a_1$

$F_1 == $ <!-- [N] -->

After processing (output file):

```markdown
$m_1 := 5\ \text{kg}$
$a_1 := 9.81\ \text{m/s}^2$
$F_1 := m_1 \cdot a_1$
$F_1 == 49.05\ \text{N}$ <!-- [N] -->
```

Rendered:

$m_1 := 5\ \text{kg}$

$a_1 := 9.81\ \text{m/s}^2$

$F_1 := m_1 \cdot a_1$

$F_1 == 49.05\ \text{N}$ <!-- [N] -->

Change `m_1`, re-run, and `F_1` updates. The value is computed, not typed.

---

## Install & run

```bash
pip install -e .
livemathtex process calculation.md
```

Output behavior is configurable (default: **timestamped output file** for safety). To overwrite in place:

```markdown
<!-- livemathtex: output=inplace -->
```

For debugging, generate an IR JSON file:

```bash
livemathtex process calculation.md --verbose
livemathtex inspect calculation.lmt.json
```

---

## Library usage

LiveMathTeX can also be used as a Python library:

```python
from livemathtex import process_text

content = """
$m := 5\\ \\text{kg}$
$a := 9.81\\ \\text{m/s}^2$
$F := m \\cdot a ==$
"""

output, ir = process_text(content)
print(output)  # Markdown with computed results
print(ir.symbols)  # Access symbol values
```

See [USAGE.md](docs/USAGE.md#library-usage-python-api) for full API documentation.

---

## Syntax at a glance

| Operator | Meaning | Example |
|---|---|---|
| `:=` | define | `x := 42` |
| `==` | evaluate | `x ==` → `x == 42` |
| `=>` | symbolic | `diff(x^2, x) =>` → `diff(x^2, x) => 2x` |
| `===` | define unit | `kWh === kW \cdot h` |

**Why `==` and not `=`?** In calculation blocks, a bare `=` is rejected to prevent accidental mistakes. Display-only formulas like `$E = mc^2$` pass through unchanged.

---

## Highlights

- **Markdown-first**: results are embedded into your LaTeX, but the file remains normal Markdown.
- **Units that behave**: unit-aware math via Pint; request display units with HTML comments: `Q ==  <!-- [m³/h] -->`
- **Custom units**: define currency / domain units with `===` (e.g. `€`, `kWh`, aliases like `dag === day`)
- **Tables without copy/paste**: value-only placeholders via `<!-- value:VAR [unit] :precision -->`
- **Inspectable state**: optional `.lmt.json` (IR) shows symbols, base units, and conversions.

---

## Editor workflow (VS Code / Cursor)

This repo includes VS Code tasks (bind to F9) that run `livemathtex process` on the current file.
See [Editor Integration](docs/EDITOR_INTEGRATION.md) for setup.

If you're using Cursor, this repo also includes command wrappers:
- [`/livemathtex`](.cursor/commands/livemathtex.md)
- [`/livemathtex-setup`](.cursor/commands/livemathtex-setup.md)

---

## What LiveMathTeX does NOT do

| Out of scope | Use instead |
|---|---|
| PDF export | `pandoc output.md -o output.pdf` |
| Live preview UI | your Markdown previewer |
| Plotting | Matplotlib, etc. |

---

## Documentation

| Document | Description |
|---|---|
| [SETUP.md](docs/SETUP.md) | Installation |
| [USAGE.md](docs/USAGE.md) | Syntax reference (units, tables, config) |
| [BACKGROUND.md](docs/BACKGROUND.md) | Research and alternatives |
| [EDITOR_INTEGRATION.md](docs/EDITOR_INTEGRATION.md) | VS Code/Cursor setup |
| [ROADMAP.md](.planning/ROADMAP.md) | Development phases (GSD planning) |
| [ARCHITECTURE.md](.planning/codebase/ARCHITECTURE.md) | Technical design (IR, parser/engine/renderer) |
| [ISSUES.md](.planning/ISSUES.md) | Open issues and enhancements |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## License

MIT License — See [LICENSE](LICENSE)

---

*Write the formula once. Get the result everywhere.*

---