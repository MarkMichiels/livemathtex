<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-035: "argument of type 'Symbol' is not iterable" error in markdown tables

This test reproduces the bug where evaluating variables in markdown table cells produces "argument of type 'Symbol' is not iterable" errors.

## Test Case

**Setup:** Define variables and use them in markdown table cells.

**Expected:** Variables should evaluate and display values in table cells.

**Actual:** Error: "Failed to parse LaTeX 'E_{26}': argument of type 'Symbol' is not iterable"

### Calculation

**Define variables:**
$E_{26} := 1473.1166\ MWh$
$SEC_{26} := 13.1528\ \frac{MWh}{kg}$
$Cost_{26} := 204.7632\ k€
\\ \color{red}{\text{
    Error: Unexpected token after expression: unit '€' at position 11}}$

**Use in table:**
| Year | Energy (MWh) | SEC (MWh/kg) | Cost (k€) |
|------|--------------|--------------|-----------|
| 2026 | $E_{26} == 1\,473.1166\ \text{MWh}$ <!-- [MWh] --> | $SEC_{26} == 13.1528\ \text{MWh/kg}$ <!-- [MWh/kg] --> | $Cost_{26} ==
\\ \color{red}{\text{
    Error: Undefined variable: Cost\_\{26\}}}$ <!-- [k€] --> |

**Expected result:** Table should display calculated values: `1473.1166 MWh`, `13.1528 MWh/kg`, `204.7632 k€`

**Actual result:** Error: "Failed to parse LaTeX 'E_{26}': argument of type 'Symbol' is not iterable"

### Steps to Reproduce

1. Run: `livemathtex clear test_iss_035_symbol_not_iterable_in_tables.md`
2. Run: `livemathtex process test_iss_035_symbol_not_iterable_in_tables.md`
3. Check table cells - should show values but show parsing errors

### Root Cause

**Table cell parsing:** LiveMathTeX's parser fails when processing variables inside markdown table cells. The error "argument of type 'Symbol' is not iterable" suggests that the parser is trying to iterate over a SymPy Symbol object, which is not iterable.

**The bug:** Table cell context (pipe-delimited cells) interferes with LaTeX parsing, causing the parser to mishandle Symbol objects.

**Impact:** High - prevents using calculated values in markdown tables, a common use case for technical documents.

---

> *livemathtex: 2026-01-16 00:27:44 | 3 definitions, 3 evaluations | 2 errors | 0.06s* <!-- livemathtex-meta -->
