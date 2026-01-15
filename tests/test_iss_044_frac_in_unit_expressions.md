<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-044: Support \frac in Unit Expressions for Variable Definitions

This test demonstrates the desired behavior where `\frac` can be used in unit expressions for variable definitions, eliminating the need for workarounds.

## Test Case

**Setup:** Define a variable with a compound unit using `\frac` syntax

**Expected:** Can use `\frac` in unit expressions for definitions (e.g., `15\ \frac{\text{mg}}{\text{L} \cdot \text{d}}`)

**Actual:** Must use workaround (define as calculation instead of value with unit expression)

### Minimal Reproduction

<!-- Current workaround (works but verbose): -->
$\gamma_{26} := \frac{15\ \text{mg}}{\text{L} \cdot \text{d}} == 15\ \text{mg/d/L}$ <!-- [mg/L/day] -->

<!-- Desired syntax (should work but currently fails): -->
<!-- $gamma_{26} := 15\ \frac{\text{mg}}{\text{L} \cdot \text{d}} == 15\ \text{mg/d/L}$ <!-- [mg/L/day] --> -->

### Expected vs Actual

| Syntax | Status | Notes |
|---|---|---|
| **Desired:** `15\ \frac{\text{mg}}{\text{L} \cdot \text{d}}` | ❌ Fails | "Unexpected token after expression: frac" |
| **Workaround:** `\frac{15\ \text{mg}}{\text{L} \cdot \text{d}}` | ✅ Works | Must use calculation syntax instead |

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_044_frac_in_unit_expressions.md`
2. Process: `livemathtex process tests/test_iss_044_frac_in_unit_expressions.md`
3. Observe: Workaround syntax works, but desired syntax fails

### Root Cause Analysis

The parser doesn't support `\frac` in unit expressions for variable definitions (value with unit expression). However, `\frac` works fine in calculations (fraction of values). This forces users to use verbose workarounds when defining variables with compound units.

### Impact

**Medium** - Requires workarounds for compound unit definitions. The workaround works but is less intuitive and more verbose than the natural LaTeX syntax.

### Feature Request

Support `\frac` in unit expressions for variable definitions:
- Allow: `$gamma := 15\ \frac{\text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Variable name 'gamma' conflicts with unit 'gamma'. Use a subscript like 'gamma\_1' or 'gamma\_var' to disambiguate.}}$`
- Currently requires: `$gamma := \frac{15\ \text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Variable name 'gamma' conflicts with unit 'gamma'. Use a subscript like 'gamma\_1' or 'gamma\_var' to disambiguate.}}$` (calculation syntax)

**Preferred:** Support both syntaxes for consistency with LaTeX conventions.

**⚠️ CRITICAL REQUIREMENT:** Settings must be preserved after `process` and `clear` cycles (idempotence requirement). Unit expressions with `\frac` must remain after `clear`, only calculated results removed.

---

---

> *livemathtex: 2026-01-16 00:38:03 | 4 definitions, 2 evaluations | 2 errors | 0.06s* <!-- livemathtex-meta -->
