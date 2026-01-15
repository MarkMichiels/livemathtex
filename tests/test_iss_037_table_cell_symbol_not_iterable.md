<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-037: Variables in table cells fail with "argument of type 'Symbol' is not iterable"

This test reproduces the bug where variables that work correctly outside tables fail when used in table cells with error "argument of type 'Symbol' is not iterable".

**Note:** This may be related to ISS-035 (multi-letter variable names in tables), but the error message is different.

## Test Case

**Setup:** Define a variable outside a table, then use it in a table cell.

**Expected:** Variable should evaluate correctly in table cells (same as outside tables).

**Actual:** Variable fails to parse/evaluate in table cells with "argument of type 'Symbol' is not iterable" error.

### Minimal Reproduction

**Define variables first:**
$T_{27} := 210\ \text{kg}$
$C_{27} := 379\ \text{kg}$

**Define variable outside table (this works):**
$U_{27} := \frac{T_{27}}{C_{27}} \cdot 90 == 49.8681$ <!-- [dimensionless] -->

**Use variable in table cell (this fails):**

| Year | Uptime |
|------|--------|
| 2027 | $U_{27} == 49.8681$ <!-- [dimensionless] --> |

### Expected vs Actual

| | Value | Unit |
|---|---|---|
| **Expected** | 49.87 | dimensionless (percentage) |
| **Actual** | Error: "Failed to parse LaTeX 'U_{27}': argument of type 'Symbol' is not iterable" |

**Note:** The same variable `U_{27}` works correctly when used outside the table, but fails when used inside a table cell.

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_037_table_cell_symbol_not_iterable.md`
2. Process: `livemathtex process tests/test_iss_037_table_cell_symbol_not_iterable.md`
3. Observe: Variable `U_{27}` evaluates correctly outside table but fails inside table cell

### Root Cause Analysis

**Table-specific parsing failure:** LiveMathTeX's table parser fails when processing variable references in table cells. The error "argument of type 'Symbol' is not iterable" suggests that the table parsing code tries to iterate over a Symbol object incorrectly.

**The bug:** Table cell parsing may use a different code path than regular text parsing, and this code path has a bug where it tries to iterate over Symbol objects.

**Impact:** High - prevents using calculated variables in tables, which is common in scientific/engineering documents.

**Related Issues:**
- ISS-035: Multi-letter variable names in tables parsed as implicit multiplication (different error, but also table-specific)

### Source Document

`mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

---

---

> *livemathtex: 2026-01-16 00:27:46 | 3 definitions, 2 evaluations | no errors | 0.07s* <!-- livemathtex-meta -->
