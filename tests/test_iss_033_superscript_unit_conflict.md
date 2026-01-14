<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-033: Variable name with superscript (R^2) conflicts with unit

This test reproduces the bug where variable names with superscripts (like `R^2` for R-squared) conflict with Pint unit names (like `molar_gas_constant ** 2`).

## Test Case

**Setup:** Define a variable with superscript (R^2 for R-squared statistic).

**Expected:** Variable should be defined and used without conflict.

**Actual:** Error: "Variable name 'R^2' conflicts with unit 'molar_gas_constant ** 2'"

### Calculation

**Define variable:**
$R^2 := 0.904$

**Expected result:** Variable `R^2` should be defined as `0.904` (dimensionless)

**Actual result:** Error: "Variable name 'R^2' conflicts with unit 'molar_gas_constant ** 2'. Use a subscript like 'R^2_1' or 'R^2_var' to disambiguate."

### Steps to Reproduce

1. Run: `livemathtex clear test_iss_033_superscript_unit_conflict.md`
2. Run: `livemathtex process test_iss_033_superscript_unit_conflict.md`
3. Check line with `R^2` - should define variable but shows unit conflict error

### Root Cause

**Variable name conflict:** LiveMathTeX's unit conflict detection incorrectly flags variable names with superscripts (like `R^2`) as conflicts with Pint unit names that use exponentiation (like `molar_gas_constant ** 2`). This is a false positive - `R^2` as a variable name should not conflict with `molar_gas_constant ** 2` as a unit.

**The bug:**
1. **Timing issue:** Error occurs during processing/evaluation, not at definition time. The error should appear when `$R^2 := 0.904$` is defined, not when it's used.
2. **False positive:** Unit conflict detection is too aggressive and doesn't distinguish between:
   - Variable names with superscripts (user-defined symbols like `R^2` for R-squared)
   - Unit names with exponentiation (Pint unit definitions like `molar_gas_constant ** 2`)
3. **Incorrect conflict:** `R^2` as a variable name should NOT conflict with `molar_gas_constant ** 2` as a unit - these are in different namespaces.

**Impact:** High - prevents using standard statistical notation (R², R², etc.) in variable names. The suggested workaround (`R_{squared}`) is incorrect - `R^2` is the proper mathematical notation and should be supported.

---

> *livemathtex: 2026-01-14 10:08:14 | 2 definitions | no errors | 0.00s* <!-- livemathtex-meta -->
