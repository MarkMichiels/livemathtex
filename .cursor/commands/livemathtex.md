---
description: Process Markdown files with LiveMathTeX calculations
---

# LiveMathTeX — Markdown Calculations (AI Command)

LiveMathTeX evaluates LaTeX math blocks inside Markdown and writes the computed results back into the Markdown output.

**Design intent:** Treat the document as the source of truth. Every number shown should be traceable to a formula in the same document (no manual/hardcoded calculated numbers).

## Capabilities (what it can do)

- Parse Markdown and execute math blocks (`$...$` and `$$...$$`)
- **Define** variables/functions with `:=`
- **Evaluate** expressions with `==`
- **Symbolic** output with `=>` (e.g., `diff(...)`)
- **Define/alias units** with `===` (place before first use)
- **Display results in a requested unit** via `<!-- [unit] -->` comments
- **Fill table cells with number-only values** via `<!-- value:... -->`
- Generate + inspect an **IR JSON** (`.lmt.json`) for debugging/traceability

## Safe workflow for a first-time AI assistant

- **Never type computed numbers manually.** Create variables and reference them.
- Put **unit declarations** and **input values** before dependent formulas.
- Prefer the default **timestamped** output (safe). Only overwrite input when explicitly requested.
- If results/units look wrong, re-run with IR output and inspect the JSON.

## CLI (the only commands)

```bash
livemathtex process <input.md> [-o <output.md>] [--verbose] [--ir-output <path.json>]
livemathtex inspect <input.lmt.json>
```

- `-o/--output` overrides the output path only (operational). Formatting belongs in the document/config.
- `--verbose` (or document directive `json=true`) writes `<input>.lmt.json` and prints a summary.

## Syntax cheat sheet

### Operators (inside `$...$` / `$$...$$`)

- `===` unit definition / alias
- `:=` define (store variable/function)
- `==` evaluate (prints numeric result)
- `:= ... ==` define + evaluate
- `=>` symbolic result

### Comments (must be on the **same line** as the math block)

- **Display conversion:** `$Q ==$ <!-- [m³/h] -->`
- **Value directive (number-only cell):** `$ $ <!-- value:Q [m³/h] :2 -->`
  - Note: `value:` outputs the **number only** (it fills the `$ $` placeholder). It does **not** append units.
- **Expression-level overrides (colon syntax):** `<!-- digits:6 format:sci trailing_zeros -->`

### Document directives (place near the top; comma-separated `key=value`)

```markdown
<!-- livemathtex: digits=6, format=engineering, output=inplace, json=true -->
```

- `output`: `timestamped` (default), `inplace`, or a filename (e.g., `output.md`)

## Units (important)

- By default, results are formatted in **SI base units** unless a display unit is requested via `<!-- [unit] -->`.
- Define non-standard units before using them:

```markdown
$ EUR === EUR $
$ kWh === kW \cdot h $
$ MWh === 1000 \cdot kWh $
$ dag === day $
```

## Tables (recommended patterns)

- **Preferred:** Put formulas directly in table cells:
  - `| Energy | $E_{year} ==$ <!-- [MWh] --> |`
- Use `value:` only when you need a number-only cell:
  - `| Flow | $ $ <!-- value:Q [m³/h] :2 --> | m³/h |`

Known limitation: `value:` has limited unit support for custom/complex units (see [KNOWN_ISSUES.md](../../docs/KNOWN_ISSUES.md#issue-001-value-directive-doesnt-support-complexcustom-units), ISSUE-001).

## Common pitfalls (fix fast)

- Math inside fenced code blocks (```...``` or ~~~...~~~) is **ignored**
- Inline `$...$` cannot contain newlines → use `$$...$$`
- Variable names that look like units may error (e.g. `m`, `A`, `U`, `g`) → use subscripts like `A_{pipe}`, `U_{HX}`, `g_{acc}`
- If you see red inline errors, fix the underlying definition/order/units and re-run (don’t “edit around” them)

## Deep references

- **[USAGE.md](../../docs/USAGE.md)** — full syntax & configuration
- **[ARCHITECTURE.md](../../docs/ARCHITECTURE.md)** — IR + internals
- **[KNOWN_ISSUES.md](../../docs/KNOWN_ISSUES.md)** — limitations + workarounds
- **[Examples](../../examples/)** — known-good patterns
- **`/livemathtex-setup`** — installation guide
