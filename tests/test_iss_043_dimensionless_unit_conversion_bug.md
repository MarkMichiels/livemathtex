<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-043: Dimensionless Calculation Incorrectly Converted to kg/mg Units

This test reproduces the bug where a dimensionless calculation (ratio × dimensionless) is incorrectly displayed with `kg/mg` units, causing the value to be divided by 1,000,000.

## Test Case

**Setup:** Calculate a dimensionless percentage from a ratio

**Expected:** Result should be dimensionless (e.g., `54.08` or `54.08%`)

**Actual:** Result is displayed as `5.4084e-05 kg/mg` (1,000,000x too small)

### Minimal Reproduction

$T_{26} := 112\ \text{kg}$
$C_{26} := 186.3778\ \text{kg}$

<!-- The calculation: (T_26 / C_26) × 90 should be dimensionless -->
$U_{26} := \frac{T_{26}}{C_{26}} \cdot 90 ==$ <!-- Dimensionless (percentage) -->

### Expected vs Actual

| | Value | Unit |
|---|---|---|
| **Expected** | 54.08 | dimensionless (percentage) |
| **Actual** | 5.4084e-05 | kg/mg (wrong!) |

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_043_dimensionless_unit_conversion_bug.md`
2. Process: `livemathtex process tests/test_iss_043_dimensionless_unit_conversion_bug.md`
3. Observe: Result shows `5.4084e-05 kg/mg` instead of `54.08` (dimensionless)

### Root Cause Analysis

LiveMathTeX is calculating the correct numeric value (54.08) but then incorrectly trying to convert it to `kg/mg` units. To convert dimensionless to `kg/mg`, it divides by 1,000,000 (since 1 kg = 1,000,000 mg), producing the wrong displayed value.

**Note:** The unit hint `<!-- Dimensionless (percentage) -->` is present but doesn't prevent the incorrect unit conversion. There is no `[kg/mg]` unit hint in the input.

### Impact

**High** - Causes cascading errors in all dependent calculations (energy, SEC, cost calculations that depend on uptime values). The numeric calculation is correct, but the displayed value is wrong, making it impossible to use the result in subsequent calculations.

---
