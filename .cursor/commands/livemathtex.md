---
description: LiveMathTeX command reference and overview
---

# LiveMathTeX Command Reference

**LiveMathTeX** evaluates LaTeX math blocks inside Markdown and writes computed results back into the document.

**Design intent:** Treat the document as the source of truth. Every number shown should be traceable to a formula in the same document (no manual/hardcoded calculated numbers).

---

## Quick Start

1. **`/setup`** - Install and verify LiveMathTeX
2. **`/build-calculations`** - Iteratively build and verify calculations
3. **`/debug-calculations`** - Debug calculations and create issues for bugs

---

## Available Commands

### **`/livemathtex`**
Show this command reference (init/overview).

**Use when:** Starting a new chat to learn what LiveMathTeX can do.

**Output:** Complete command reference with syntax, examples, and best practices.

---

### **`/setup`**
Install and setup LiveMathTeX for first-time use.

**Use when:** First time using LiveMathTeX or setting up on a new machine.

**What it does:**
- Guides installation from source
- Verifies installation works
- Configures VS Code/Cursor integration (F9 keybinding)

**Usage:** `/setup`

---

### **`/build-calculations`**
Iteratively build and verify calculations until correct.

**Use when:** Building a new document or fixing calculations in an existing document.

**Workflow:**
1. Clean source document (remove error markup)
2. Calculate expected values manually
3. Add expected values to output document
4. Process with LiveMathTeX
5. Compare expected vs actual (git diff)
6. Fix discrepancies
7. Iterate until all correct

**Usage:** `/build-calculations`

**See:** Full workflow documentation in command file.

---

### **`/debug-calculations`**
Same as `/build-calculations`, but detects issues and creates ISS entries for bugs.

**Use when:** Debugging calculation problems and need to distinguish user errors from LiveMathTeX bugs.

**Workflow:**
- Same as `/build-calculations`
- Plus: Classifies discrepancies (bug vs user error)
- Plus: Creates ISS entries for LiveMathTeX bugs
- Plus: Documents workarounds for bugs

**Usage:** `/debug-calculations`

**See:** Full workflow documentation in command file.

---

## Core Concepts

### 🚨 CRITICAL: Use Units Rigorously!

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

---

## Syntax Reference

### Operators (inside `$...$` / `$$...$$`)

- `===` - Unit definition / alias
- `:=` - Define (store variable/function)
- `==` - Evaluate (prints numeric result)
- `:= ... ==` - Define + evaluate
- `=>` - Symbolic result

### Comments (must be on the **same line** as the math block)

- **Display conversion:** `$Q ==$ <!-- [m³/h] -->`
- **Value directive (number-only cell):** `$ $ <!-- value:Q [m³/h] :2 -->`
  - Note: `value:` outputs the **number only** (it fills the `$ $` placeholder). It does **not** append units.
- **Expression-level overrides:** `<!-- digits:6 format:sci trailing_zeros -->`

### Document Directives (place near the top; comma-separated `key=value`)

```markdown
<!-- livemathtex: digits=6, format=engineering, output=inplace, json=true -->
```

- `output`: `timestamped` (default), `inplace`, or a filename (e.g., `output.md`)

---

## Units

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

---

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
Removes computed values and error markup from processed documents.

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

---

## Best Practices

- **Never type computed numbers manually.** Create variables and reference them.
- **Always use units** in definitions for verification:
  ```latex
  $P := 310.7\ \text{kW}$  # ✅ Good - unit documented
  $P := 310.7$             # ❌ Bad - what unit?
  ```
- **Put unit declarations and input values before dependent formulas.**
- **Prefer timestamped output** (default). Only overwrite input when explicitly requested.
- **Use `clear` before reprocessing** if document has error markup from previous runs.
- **Use `/build-calculations` workflow** for systematic verification.

---

## Common Pitfalls

- **Math inside fenced code blocks** (```...``` or ~~~...~~~) is **ignored**
- **Inline `$...$` cannot contain newlines** → use `$$...$$`
- **Variable names that look like units** may error (e.g. `m`, `A`, `U`, `g`) → use subscripts like `A_{pipe}`, `U_{HX}`, `g_{acc}`
- **If you see red inline errors:** Fix the underlying definition/order/units and re-run (don't "edit around" them)
- **Error markup in input:** Use `livemathtex clear` to remove, don't manually edit
- **Redefining existing units:** Don't define `Wh`, `kWh`, `MWh`, `yr`, `d` - Pint already knows them
- **Compound units:** Don't define `mol/day`, `g/day`, `MWh/kg` - they work automatically
- **Unit conversion failures:** For recursive units (MWh, mol/day), see ISS-014 - conversion may fail but calculation is correct

---

## Known Issues

- **ISS-024:** Numerical calculations produce incorrect results (FIXED in v1.6 - now uses Pint)
- **ISS-025:** SymPy constants not handled (π, e, etc. cause errors) - OPEN
- **ISS-014:** Unit conversion fails for recursively defined units (MWh, mol/day, MWh/kg). Calculation is correct, but conversion to target unit fails. Workaround: Results show in SI base units.
- **ISS-016:** Error markup in input document not detected (FIXED - use `livemathtex clear` first)

**See:** `.planning/ISSUES.md` for complete list.

---

## Workflow Recommendations

### For New Documents

1. **`/setup`** - Verify installation
2. **`/build-calculations`** - Build document iteratively
3. **`/livemathtex`** - Reference syntax as needed

### For Debugging Problems

1. **`/debug-calculations`** - Systematic debugging with issue detection
2. **`/livemathtex`** - Check syntax and best practices

### For Quick Processing

```bash
livemathtex process input.md
```

---

## Deep References

- **[USAGE.md](../../docs/USAGE.md)** — full syntax & configuration
- **[ARCHITECTURE.md](../../docs/ARCHITECTURE.md)** — IR + internals
- **[ISSUES.md](../../.planning/ISSUES.md)** — known bugs and enhancements
- **[LESSONS_LEARNED.md](../../.planning/LESSONS_LEARNED.md)** — patterns and solutions
- **[Examples](../../examples/)** — known-good patterns

---

**Use this command at the start of a chat to learn what LiveMathTeX can do and how to use it effectively.**
