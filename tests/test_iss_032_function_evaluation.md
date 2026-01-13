<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-032: Function evaluation fails with units

This test reproduces the bug where functions defined with units cannot be evaluated properly.

## Test Case

**Setup:** Define a function with units and try to evaluate it.

**Expected:** Function should evaluate correctly when called with arguments.

**Actual:** Function evaluation fails with "Cannot convert expression to float" error.

### Calculation

**Define function:**
$PPE_{eff}(r_{frac}) := (r_{frac} \cdot 4.29 + (1 - r_{frac}) \cdot 2.57) \cdot 0.9143$

**Try to evaluate function:**
$PPE_{result} := PPE_{eff}(0.90) == 3.765$ <!-- Should evaluate to ~3.765 -->

**Expected result:** `3.765` (or similar value)

**Actual result:** Error: "Cannot convert expression to float"

### Steps to Reproduce

1. Run: `livemathtex clear test_iss_032_function_evaluation.md`
2. Run: `livemathtex process test_iss_032_function_evaluation.md`
3. Check line with `PPE_{result}` - should show calculated value but shows error

### Root Cause

**Function evaluation failure:** When a function is defined and then called with arguments, LiveMathTeX cannot evaluate the function call. The function definition is stored as a Lambda, but the evaluation step fails to substitute the argument and compute the result.

**Manual calculation (correct):**
- `PPE_{eff}(0.90) = (0.90 × 4.29 + 0.10 × 2.57) × 0.9143 = 3.765` ✓

**LiveMathTeX calculation (bug):**
- Function definition works: `PPE_{eff}(r_{frac}) := ...` ✓
- Function call fails: `PPE_{eff}(0.90)` → Error: "Cannot convert expression to float" ✗

**The bug:** Function evaluation doesn't work - functions can be defined but not evaluated with arguments.

**Impact:** High - prevents using functions for reusable calculations, forcing repetition of formulas.

---

> *livemathtex: 2026-01-14 00:39:01 | 2 definitions, 1 evaluation | no errors | 0.24s* <!-- livemathtex-meta -->
