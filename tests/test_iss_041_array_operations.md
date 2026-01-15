<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-041: Array/Vector Operations for Repetitive Calculations

This test demonstrates the need for array operations to handle repetitive calculations (e.g., calculations for multiple years).

## Test Case

**Setup:** Many similar calculations for different values (e.g., years 2026-2030, multiple reactors)

**Expected:** Can define arrays and iterate over them to calculate values

**Actual:** Must manually define each calculation (e.g., `gamma_26`, `gamma_27`, `gamma_28`, etc.)

### Minimal Reproduction

**Current approach (verbose):**
$\gamma_{26} := 15\ mg/L/d$
$\gamma_{27} := 30.5\ mg/L/d$
$\gamma_{28} := 34\ mg/L/d$
$\gamma_{29} := 38\ mg/L/d$
$\gamma_{30} := 44\ mg/L/d$

$m_{26} := V_L \cdot \gamma_{26} ==$ <!-- [g/day] -->
$m_{27} := V_L \cdot \gamma_{27} ==$ <!-- [g/day] -->
$m_{28} := V_L \cdot \gamma_{28} ==$ <!-- [g/day] -->
$m_{29} := V_L \cdot \gamma_{29} ==$ <!-- [g/day] -->
$m_{30} := V_L \cdot \gamma_{30} ==$ <!-- [g/day] -->

**Desired approach (with arrays):**
$\gamma := [15, 30.5, 34, 38, 44]\ mg/L/d$
$m := V_L \cdot \gamma ==$ <!-- [g/day] -->
<!-- Results: m[0] = 567.36 g/d, m[1] = 1153.63 g/d, etc. -->

### Expected vs Actual

| Approach | Lines of Code | Maintainability |
|----------|---------------|-----------------|
| Current (manual) | 10+ lines | Low (must update each year) |
| Desired (arrays) | 2-3 lines | High (change array, all calculations update) |

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_041_array_operations.md`
2. Process: `livemathtex process tests/test_iss_041_array_operations.md`
3. Observe: Arrays are not supported - must define each calculation manually

### Root Cause Analysis

LiveMathTeX doesn't support array/vector operations. Each calculation must be defined individually, leading to verbose code for repetitive patterns.

### Impact

Medium - Reduces code duplication for repetitive calculations (years, reactors, scenarios). Improves maintainability when values change.

### Feature Request

Add array/vector support:
- Define arrays: `$gamma := [15, 30.5, 34, 38, 44]\ mg/L/d$`
- Element access: `$gamma[0]$` or `$gamma_26$` (if array indexed by year)
- Vectorized operations: `$m := V_L \cdot gamma$` (element-wise multiplication)
- Array indexing: Support for named indices (e.g., `gamma[2026]`)

**Preferred:** Start with basic array support, then add vectorized operations.

**⚠️ CRITICAL REQUIREMENT - Idempotence:**
Settings must be preserved after `process` and `clear` cycles:
- After `process`: Array definitions and calculations are evaluated
- After `clear`: Array definitions remain (syntax preserved), calculated results removed
- After `process` again: Arrays re-evaluated correctly using preserved definitions

This ensures the document remains stable and can be processed multiple times without losing array structure.

**Example:**
```markdown
$years := [2026, 2027, 2028, 2029, 2030]$
$gamma := [15, 30.5, 34, 38, 44]\ mg/L/d$
$m := V_L \cdot gamma ==$ <!-- [g/day] -->
<!-- Access: m[0] for 2026, m[1] for 2027, etc. -->
```

---
