---
description: Process Markdown files with LiveMathTeX calculations
---

# LiveMathTeX — Markdown Calculations (AI Command)

LiveMathTeX evaluates LaTeX math blocks inside Markdown and writes the computed results back into the Markdown output.

**Design intent:** Treat the document as the source of truth. Every number shown should be traceable to a formula in the same document (no manual/hardcoded calculated numbers).

## 🚨 CRITICAL: Use Units Rigorously!

**The entire point of LiveMathTeX is verification.** AI assistants can calculate values themselves, but LiveMathTeX provides a **double-check** through explicit unit-aware computation.

**DO:** Use units consistently to verify calculations are correct:
```latex
$P := 310.7\ \text{kW}$
$t := 8760\ \text{h}$
$E := P \cdot t ==$  <!-- [MWh] -->
% → LiveMathTeX computes AND converts: 2721.7 MWh
% → If you accidentally used seconds, you'd get 0.756 MWh (wrong!)
```

**DON'T:** Skip units because "you know the answer":
```latex
$P := 310.7$       % ← Is this kW? W? MW? Who knows!
$t := 8760$        % ← Hours? Seconds? Days?
$E := P \cdot t == 2721727$  % ← Computed, but what unit? No verification!
```

**Why this matters:**
- **Dimensional analysis catches errors:** If you mix kW with seconds instead of hours, the unit output reveals the mistake immediately
- **Self-documenting:** Units in the document explain what each variable means
- **The AI already knows the answer** - LiveMathTeX's value is the independent verification, not the computation itself

## Capabilities (what it can do)

- Parse Markdown and execute math blocks (`$...$` and `$$...$$`)
- **Define** variables/functions with `:=`
- **Evaluate** expressions with `==`
- **Symbolic** output with `=>` (e.g., `diff(...)`)
- **Define/alias units** with `===` (place before first use)
- **Display results in a requested unit** via `<!-- [unit] -->` comments
- **Fill table cells with number-only values** via `<!-- value:... -->`
- Generate + inspect an **IR JSON** (`.lmt.json`) for debugging/traceability

## AI Assistant Workflow

### Standard Processing Workflow

1. **Process document:**
   ```bash
   livemathtex process input.md
   ```

2. **Check for errors:**
   - If errors reported: Use `livemathtex inspect input.lmt.json` to debug
   - If "no errors" but error markup visible: Document has leftover errors from previous run

3. **Clean up errors:**
   ```bash
   livemathtex clear output.md  # Remove error markup
   livemathtex process output.md  # Reprocess
   ```

### Debugging Workflow

**When you see errors or unexpected results:**

1. **Generate IR JSON:**
   ```bash
   livemathtex process input.md --verbose
   ```

2. **Inspect errors:**
   ```bash
   livemathtex inspect input.lmt.json
   ```
   Shows: symbols, units, errors with line numbers

3. **Common issues:**
   - **Undefined variable:** Check definition order (define before use)
   - **Unit conversion failed:** See ISS-014 (recursive units like MWh, mol/day)
   - **Error markup in input:** Use `livemathtex clear` first (see ISS-016)

### Best Practices

- **Never type computed numbers manually.** Create variables and reference them.
- **Always use units** in definitions for verification:
  ```latex
  $P := 310.7\ \text{kW}$  # ✅ Good - unit documented
  $P := 310.7$             # ❌ Bad - what unit?
  ```
- **Put unit declarations and input values before dependent formulas.**
- **Prefer timestamped output** (default). Only overwrite input when explicitly requested.
- **Use `clear` before reprocessing** if document has error markup from previous runs.
- **Never use custom scripts** to remove error markup - use `livemathtex clear` instead.

### Error Detection Limitations

**⚠️ Known issues (ISS-016):**
- LiveMathTeX only detects **new errors** generated during processing
- **Existing error markup in input** is not detected or counted
- If you see error markup but "no errors" reported, the document has leftover errors from a previous run
- **Solution:** Always use `livemathtex clear` before processing documents with error markup

## CLI Commands

```bash
livemathtex process <input.md> [-o <output.md>] [--verbose] [--ir-output <path.json>]
livemathtex inspect <input.lmt.json>
livemathtex clear <input.md> [-o <output.md>]
```

### `process` - Evaluate calculations
Evaluates all math blocks and writes computed values.

**Options:**
- `-o/--output`: Output file path (default: timestamped or inplace based on document directive)
- `--verbose` or `json=true` directive: Generate IR JSON for debugging
- `--ir-output`: Custom path for IR JSON (default: `input.lmt.json`)

### `inspect` - Debug IR JSON
Shows symbols, units, and errors from the IR file. Use when debugging calculation issues.

```bash
livemathtex inspect input.lmt.json
```

### `clear` - Reset document
**✅ Available** - Removes computed values and error markup from processed documents.

**Use cases:**
- Clean up a document with errors before reprocessing
- Reset document to input state
- Remove error markup from previous runs

**What it removes:**
- Computed values after `==` (e.g., `$x == 42$` → `$x ==$`)
- Error markup (`\color{red}{...}`)
- Metadata comments (`<!-- livemathtex-meta -->`)

**What it preserves:**
- Definitions (`$x := 5$`)
- Unit definitions (`$kWh === 1000\ Wh$`)
- Unit hints (`<!-- [kJ] -->` and inline `$E == [kJ]$`)
- Document structure

**Examples:**
```bash
livemathtex clear output.md              # Overwrite in-place
livemathtex clear output.md -o input.md  # Write to different file
```

**⚠️ Important:** Always use `livemathtex clear` to remove error markup. **Never** use custom scripts or manual regex replacements - they can damage LaTeX structure.

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
- **Pint already knows most units** - you don't need to define them:
  - SI base: `m`, `kg`, `s`, `A`, `K`, `mol`, `cd`
  - Derived: `N`, `J`, `W`, `Pa`, `Hz`, `V`, `ohm`
  - Prefixed: `kW`, `MW`, `mm`, `km`, `kWh`, `MWh`, `mg`, `mL`
  - Time: `year`, `yr`, `day`, `d`, `hour`, `h`
  - **Compound units work automatically:** `mol/day`, `g/day`, `mg/L/day`, `kg/year`, `MWh/kg` (no definition needed!)

**Only define custom units:**
- Currency: `€`, `$`, `EUR`, `USD`
- Non-standard abbreviations: `dag === day` (Dutch for day)
- Industry-specific units

```markdown
$ € === € $                    # Currency (not in Pint)
$ dag === day $                 # Alias (Dutch abbreviation)
$ kWh === kW \cdot h $          # Only if you need custom definition
```

**⚠️ Don't redefine existing units:** Pint already knows `Wh`, `kWh`, `MWh`, `yr`, `d`, etc. Redefining them causes errors.

## Tables (recommended patterns)

- **Preferred:** Put formulas directly in table cells:
  - `| Energy | $E_{year} ==$ <!-- [MWh] --> |`
- Use `value:` only when you need a number-only cell:
  - `| Flow | $ $ <!-- value:Q [m³/h] :2 --> | m³/h |`

Known limitation: `value:` has limited unit support for custom/complex units (see [BACKLOG.md](../../docs/BACKLOG.md#issue-001-value-directive-doesnt-support-complexcustom-units), ISSUE-001).

## Common pitfalls (fix fast)

- **Math inside fenced code blocks** (```...``` or ~~~...~~~) is **ignored**
- **Inline `$...$` cannot contain newlines** → use `$$...$$`
- **Variable names that look like units** may error (e.g. `m`, `A`, `U`, `g`) → use subscripts like `A_{pipe}`, `U_{HX}`, `g_{acc}`
- **If you see red inline errors:** Fix the underlying definition/order/units and re-run (don't "edit around" them)
- **Error markup in input:** Use `livemathtex clear` to remove, don't manually edit
- **Redefining existing units:** Don't define `Wh`, `kWh`, `MWh`, `yr`, `d` - Pint already knows them
- **Compound units:** Don't define `mol/day`, `g/day`, `MWh/kg` - they work automatically
- **Unit conversion failures:** For recursive units (MWh, mol/day), see ISS-014 - conversion may fail but calculation is correct

## Known Issues

- **ISS-014:** Unit conversion fails for recursively defined units (MWh, mol/day, MWh/kg). Calculation is correct, but conversion to target unit fails. Workaround: Results show in SI base units.
- **ISS-016:** Error markup in input document not detected. If you see error markup but "no errors" reported, use `livemathtex clear` first.

## Deep references

- **[USAGE.md](../../docs/USAGE.md)** — full syntax & configuration
- **[ARCHITECTURE.md](../../docs/ARCHITECTURE.md)** — IR + internals
- **[ISSUES.md](../../.planning/ISSUES.md)** — known bugs and enhancements
- **[Examples](../../examples/)** — known-good patterns
- **`/livemathtex-setup`** — installation guide
