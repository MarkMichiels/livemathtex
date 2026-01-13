# LiveMathTeX Lessons Learned

This document tracks insights, patterns, and solutions discovered during LiveMathTeX usage. Use this to improve the workflow and help LLMs understand common issues.

**Purpose:** Build institutional knowledge about LiveMathTeX quirks, best practices, and debugging strategies.

---

## Workflow Insights

### Always Clean Before Processing

**Problem:** Error markup from previous runs can hide new errors or cause confusion.

**Solution:** Always run `livemathtex clear` on the source document before processing:
```bash
livemathtex clear input.md -o input_clean.md
livemathtex process input_clean.md
```

**Why:**
- Removes leftover error markup that might not be detected as "new errors"
- Ensures clean baseline for comparison
- Makes it easier to see what changed in git diff

**Date:** 2026-01-13

---

### Expected Values Workflow

**Problem:** Without expected values, it's hard to spot calculation errors.

**Solution:** Calculate expected values manually first, add them to output document, then run LiveMathTeX and compare:
```bash
# 1. Clean source
livemathtex clear input.md -o input_clean.md

# 2. Create output document with expected values
cp input_clean.md output_expected.md
# Manually add expected values: $x == 42.5\ \text{kg}$ <!-- EXPECTED: 42.5 kg -->

# 3. Process with LiveMathTeX
livemathtex process input_clean.md -o output_actual.md

# 4. Compare
git diff output_expected.md output_actual.md
```

**Why:**
- Makes discrepancies immediately visible
- Helps LLMs understand what went wrong
- Enables systematic debugging

**Date:** 2026-01-13

---

## Classification Patterns

### How to Distinguish Bugs from User Errors

**LiveMathTeX Bugs (create issue):**
- ✅ Order of magnitude errors (86,390x, 31,500x, etc.) - usually indicates calculation bug
- ✅ Rate × time calculations producing wrong results (ISS-029)
- ✅ Unit conversion failures with correct formulas (ISS-028)
- ✅ Error messages from LiveMathTeX
- ✅ Known issue patterns (check `ISSUES.md`)

**User Errors (fix in source):**
- ✅ Unit hint doesn't match result type
- ✅ Incorrect calculation formula (e.g., using `× 90` instead of `× 0.90`)
- ✅ Missing variable definitions
- ✅ Wrong unit definitions

**When in doubt:**
- Check `ISSUES.md` for similar issues
- Check `LESSONS_LEARNED.md` for patterns
- Investigate manually: if manual calculation matches expected → bug
- If manual calculation matches actual → user error

**Date:** 2026-01-13

---

## Calculation Issues

### SymPy Constants Not Handled (ISS-025)

**Problem:** Calculations with `\pi`, `e`, or other SymPy constants fail with `isinstance() arg 2 must be a type` error.

**Example:**
```latex
$d_{tube} := \frac{2 \cdot d_{weld}}{\pi} ==$  <!-- Error! -->
```

**Root Cause:** `evaluate_sympy_ast_with_pint()` doesn't handle `sympy.core.numbers.Pi`, `Exp1`, etc.

**Workaround:** None - requires code fix (ISS-025).

**Date:** 2026-01-13

---

### Rate × Time Calculations (ISS-024 - FIXED, ISS-029 - REGRESSION)

**Problem:** Calculations like `g/day × days` produced incorrect results (86,390x too low).

**Example:**
```latex
$m_{26} := 49,020\ g/day$
$d_{op} := 365\ d$
$C_{26} := m_{26} \cdot d_{op} \cdot 0.9 ==$  <!-- Expected: 16,103 kg, Got: 0.1864 kg -->
```

**Root Cause:** SymPy doesn't automatically convert time units (days → seconds) during multiplication.

**Solution (ISS-024):** Fixed in v1.6 Phase 14 - now uses Pint for numerical evaluation.

**Regression (ISS-029):** Despite ISS-024 being marked FIXED, the specific case `g/day × days` still fails. The fix may only work for power × time (`kW × h`), not all rate × time cases.

**Workaround:** Calculate manually and document in comments:
```latex
$C_{26} := m_{26} \cdot d_{op} \cdot u_{max} ==$ <!-- [kg] -->
<!-- WORKAROUND: ISS-029 - Manual: 49,020 g/day × 365 d × 0.90 = 16,103 kg -->
```

**Date:** 2026-01-13 (ISS-024 fixed, ISS-029 regression discovered)

**Update 2026-01-13:** ISS-029 is actually RESOLVED. Testing confirms rate × time calculations work correctly:
- `49020 g/day × 365 d × 0.90 = 16,103.07 kg` ✅ CORRECT
- `567.36 g/d × 365 d × 0.90 = 16,103.04 kg` ✅ CORRECT

**Important:** If a document shows incorrect values (like `0.1864 kg`), it likely contains **old cached values** from before the fix. The solution is to:
1. Clear the document: `livemathtex clear document.md`
2. Re-process: `livemathtex process document.md`
3. Verify calculations are correct

**Common pattern:** Documents may have old values that don't match current LiveMathTeX behavior. Always clear and re-process when debugging calculation issues.

---

### Currency Unit Conversion (ISS-028)

**Problem:** Unit definitions `$€ === €$` and `$k€ === 1000\ €$` are not recognized by Pint, which uses "EUR" as the currency unit. This causes unit conversion failures when using `<!-- [k€] -->` hints.

**Example:**
```latex
$€ === €$
$k€ === 1000\ €$
$c_{elec} := 139\ \frac{€}{MWh}$
$E_{26} := 1472\ MWh$
$Cost_{26} := E_{26} \cdot c_{elec} ==$ <!-- [k€] -->
% Expected: 204.608 k€
% Actual: 6.48855 EUR (with warning: Cannot convert from 'EUR' to 'k€')
```

**Root Cause:** Pint uses "EUR" as currency unit, but unit definitions use "€" which Pint doesn't recognize as equivalent.

**Workaround:** Calculate manually and document in comments:
```latex
$Cost_{26} := E_{26} \cdot c_{elec} ==$ <!-- [k€] -->
<!-- WORKAROUND: ISS-028 - Manual: 1,472 MWh × 139 €/MWh = 204,608 € = 204.608 k€ -->
```

**Date:** 2026-01-13

---

### Unit Hints vs Calculation Results

**Problem:** Unit hints like `<!-- [kg/year] -->` don't match calculation results when result is a total (not a rate).

**Example:**
```latex
$C_{26} := m_{26} \cdot d_{op} \cdot u_{max} ==$ <!-- [kg/year] -->
% Result: 0.1864 kg (wrong - should be 16,103 kg)
% Unit hint says "per year" but result is total mass
```

**Solution:** Change unit hint to match result type:
- Total mass → `<!-- [kg] -->`
- Rate → `<!-- [kg/year] -->`

**Date:** 2026-01-13

---

## Common Patterns

### Productivity Calculations

**Pattern:** When calculating productivity (e.g., `mg/L/day`), ensure all units are consistent:

```latex
$m_{ax,rct} := PAR_{rct} \cdot Y_{ax} ==$ <!-- [g/day] -->
$V_{rct} := 17.0\ L$
$\gamma_{max} := \frac{m_{ax,rct}}{V_{rct}} \cdot 1000 ==$ <!-- [mg/L/day] -->
```

**Common Error:** Forgetting to convert units (e.g., `g` → `mg` requires `× 1000`).

**Date:** 2026-01-13

---

### PAR Calculations

**Pattern:** PAR (Photosynthetically Active Radiation) calculations often involve:
- Power (W)
- PPE (µmol/J)
- Time (s/day)
- Conversion: µmol → mol

**Example:**
```latex
$PAR_{rct} := P_{LED,dc} \cdot PPE_{eff} ==$ <!-- [mol/day] -->
```

**Common Error:** Forgetting that `mol/day` requires time conversion (s → day).

**Date:** 2026-01-13

---

## Debugging Strategies

### Use Git Diff for Verification

**Strategy:** Use git diff to compare expected vs actual values:

```bash
# 1. Create expected output
cp input.md output_expected.md
# Add expected values manually

# 2. Process with LiveMathTeX
livemathtex process input.md -o output_actual.md

# 3. Compare
git diff --no-index output_expected.md output_actual.md
```

**Why:** Makes discrepancies immediately visible, shows exactly what changed.

**Date:** 2026-01-13

---

### Inspect IR JSON for Debugging

**Strategy:** When calculations are wrong, inspect the IR JSON:

```bash
livemathtex process input.md --verbose
livemathtex inspect input.lmt.json
```

**What to look for:**
- Symbol values (are they correct?)
- Unit conversions (did they work?)
- Error messages (what failed?)

**Date:** 2026-01-13

---

## Best Practices

### Always Use Units

**Rule:** Never define variables without units:

```latex
✅ Good: $P := 310.7\ \text{kW}$
❌ Bad:  $P := 310.7$
```

**Why:** Units enable dimensional analysis and catch errors.

**Date:** 2026-01-13

---

### Define Before Use

**Rule:** Always define variables before using them in calculations:

```latex
✅ Good:
$P := 310.7\ \text{kW}$
$t := 8760\ \text{h}$
$E := P \cdot t ==$ <!-- [MWh] -->

❌ Bad:
$E := P \cdot t ==$ <!-- [MWh] -->  (P and t not defined yet!)
$P := 310.7\ \text{kW}$
$t := 8760\ \text{h}$
```

**Date:** 2026-01-13

---

## Open Questions

### Why Do Some Calculations Still Fail?

**Question:** Even after ISS-024 fix (Pint evaluator), some calculations still produce incorrect results.

**Example:**
```latex
$PAR_{rct} := P_{LED,dc} \cdot PPE_{eff} == 650\,700\,000\ \text{mol/day}$
% This seems too high - should be around 650 mol/day, not 650 million!
```

**Investigation Needed:**
- Check if `PPE_{eff}` units are correct
- Verify time conversion in PAR calculation
- Check if Pint is handling unit multiplication correctly

**Date:** 2026-01-13

---

## Related Issues

- **ISS-024:** Numerical calculations produce incorrect results (FIXED in v1.6)
- **ISS-025:** SymPy constants not handled (OPEN)
- **ISS-026:** Compound unit rate calculations (mg/L/day) produce incorrect results (OPEN)
- **ISS-027:** EUR to k€ unit conversion fails (OPEN)
- **ISS-014:** Unit conversion fails for recursive units (FIXED)
- **ISS-016:** Error markup in input not detected (FIXED)

---

## New Issues Discovered (2026-01-13)

### Compound Rate Unit Calculations (ISS-026)

**Problem:** Calculations with compound rate units like `mg/L/day` produce results 86.4x too large.

**Example:**
```latex
$V_L := 37824\ L$
$\gamma_{26} := 15\ \frac{\text{mg}}{\text{L} \cdot \text{d}}$
$m_{26} := V_L \cdot \gamma_{26} ==$ <!-- [g/day] -->
% Expected: 567.36 g/day
% Actual: 49,020 g/day (86.4x too large)
```

**Workaround:** None - requires code fix (ISS-026). Manual calculation needed for now.

**Date:** 2026-01-13

---

### EUR to k€ Conversion (ISS-027)

**Problem:** Unit conversion from EUR to k€ fails with dimension incompatibility warning.

**Example:**
```latex
$€ === €$
$k€ === 1000\ €$
$Cost_{26} := E_{26} \cdot c_{elec} ==$ <!-- [k€] -->
% Warning: Cannot convert from 'EUR' to 'k€' - dimensions incompatible
% Result: 204.608 EUR (correct value, wrong unit)
```

**Workaround:** Use manual conversion or accept EUR unit. The numerical value is correct, only the unit display fails.

**Date:** 2026-01-13

---

### Currency Unit Definitions Not Recognized by Pint (ISS-028)

**Problem:** Currency unit definitions using `€` and `k€` are not recognized by Pint, which uses "EUR" as the currency unit. This causes conversion warnings when using `<!-- [k€] -->` hints.

**Example:**
```latex
$€ === €$
$k€ === 1000\ €$
$Cost := E \cdot c_{elec} ==$ <!-- [k€] -->
% Result: 204.608 EUR (with warning: Cannot convert from 'EUR' to 'k€')
```

**Workaround (until ISS-028 is fixed):**
1. **Option 1:** Use "EUR" directly in calculations (no custom definitions):
   ```latex
   $Cost := E \cdot c_{elec} ==$ <!-- [EUR] -->
   % Then manually note: "Cost = 204.608 EUR = 204.6 k€"
   ```

2. **Option 2:** Accept the warning and manually convert in documentation:
   ```latex
   $Cost := E \cdot c_{elec} ==$ <!-- [k€] -->
   <!-- WORKAROUND: ISS-028 - Result shows EUR, manually convert: 204.608 EUR = 204.6 k€ -->
   ```

3. **Option 3:** Use dimensionless values with explicit unit in comments:
   ```latex
   $Cost := \frac{E \cdot c_{elec}}{1000} ==$ <!-- [k€] -->
   % Divide by 1000 to get k€ directly
   ```

**Root Cause:** Pint uses "EUR" as the currency unit, but LiveMathTeX unit definitions use "€" which Pint doesn't recognize as equivalent. The `$€ === €$` definition doesn't create an alias to "EUR".

**Classification Pattern:**
- **Bug indicator:** Unit conversion warnings for currency (EUR/k€)
- **Not user error:** Unit definitions are correct, but Pint doesn't recognize them
- **Related issues:** ISS-027 (marked resolved, but this is a different aspect - unit definition recognition)

**Date:** 2026-01-13
**Document:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

---

### Unit Propagation Failure When Multiplying by Dimensionless Values (ISS-031)

**Problem:** When multiplying a unit by a dimensionless value, LiveMathTeX loses the unit and treats the result as dimensionless, causing unit conversion warnings.

**Example:**
```latex
$PPE_{red} := 4.29\ \frac{\text{µmol}}{\text{J}}$
$f_{geom} := 0.9143$  (dimensionless)
$PPE_{eff} := PPE_{red} \cdot f_{geom} ==$ <!-- [µmol/J] -->
% Expected: 3.922 µmol/J
% Actual: 3.922 (dimensionless) with warning: "Cannot convert from 'dimensionless' to 'µmol/J'"
```

**Root Cause:** Unit propagation fails when multiplying units by dimensionless values. The numeric calculation is correct, but the unit is not preserved.

**Workaround (until ISS-031 is fixed):**
1. **Option 1:** Define the result with explicit unit:
   ```latex
   $PPE_{eff} := 3.922\ \frac{\text{µmol}}{\text{J}}$  <!-- Manual calculation -->
   ```

2. **Option 2:** Use intermediate calculation with unit preservation:
   ```latex
   $PPE_{eff\_num} := PPE_{red} \cdot f_{geom}$  <!-- Gets numeric value -->
   $PPE_{eff} := PPE_{eff\_num}\ \frac{\text{µmol}}{\text{J}}$  <!-- Add unit explicitly -->
   ```

3. **Option 3:** Accept the dimensionless result and document the unit in comments:
   ```latex
   $PPE_{eff} := PPE_{red} \cdot f_{geom} ==$ <!-- Dimensionless (workaround ISS-031) -->
   <!-- WORKAROUND: ISS-031 - Result is 3.922 (should be 3.922 µmol/J). Manual: 4.29 µmol/J × 0.9143 = 3.922 µmol/J -->
   ```

**Impact:** High - causes cascading errors in dependent calculations. Any calculation that depends on a unit that was lost will also fail.

**Classification Pattern:**
- **Bug indicator:** Unit conversion warnings for calculations that multiply units by dimensionless values
- **Not user error:** The formula is correct, but LiveMathTeX loses the unit
- **Related issues:** ISS-031 (unit propagation failure)

**Date:** 2026-01-13
**Document:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

---

**Last Updated:** 2026-01-13
