<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-034: Variable parsing fails for variables with commas in subscript

This test reproduces the bug where variables with commas in subscripts (e.g., `PAR_{R2,umol}`) fail to parse correctly in expressions.

## Test Case

**Setup:** Define variables with commas in subscripts and use them in calculations.

**Expected:** Variables should parse and evaluate correctly.

**Actual:** Parsing errors: "I expected something else here" when using variables with commas in expressions.

### Calculation

**Define variables:**
$PAR_{R2,umol} := 1413\ \frac{\text{µmol}}{s}$
$t_{day} := 86400\ \frac{s}{d}$

**Use in calculation:**
$PAR_{R2} := PAR_{R2,umol} \cdot t_{day} == 122.0832\ \text{mol/d}$ <!-- [mol/day] -->

**Expected result:** `PAR_{R2} = 1413 µmol/s × 86400 s/d = 122.0832 mol/d`

**Actual result:** Error: "Failed to parse LaTeX 'PAR_{R2,umol} \cdot t_{day}': I expected something else here"

### Steps to Reproduce

1. Run: `livemathtex clear test_iss_034_comma_in_subscript.md`
2. Run: `livemathtex process test_iss_034_comma_in_subscript.md`
3. Check line with `PAR_{R2}` - should calculate correctly but shows parsing error

### Root Cause

**Parsing failure:** LiveMathTeX's LaTeX parser (latex2sympy) fails to correctly parse variable names with commas in subscripts when they appear in expressions. The parser converts `PAR_{R2,umol}` to `PAR_{R2_umol}` internally, but then fails to match it when used in expressions.

**The bug:** Variable name normalization (converting commas to underscores) happens during definition, but expression parsing doesn't handle the normalized form correctly.

**Impact:** High - prevents using descriptive variable names with multiple subscripts (common in scientific notation).

---

> *livemathtex: 2026-01-14 10:05:44 | 3 definitions, 1 evaluation | no errors | 0.15s* <!-- livemathtex-meta -->
