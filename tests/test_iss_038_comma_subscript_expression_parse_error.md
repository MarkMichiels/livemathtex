<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-038: Variables with commas in subscripts fail in expressions with "I expected something else here"

This test reproduces the bug where variables with commas in subscripts fail when used in expressions (multiplication, division, addition) with error "I expected something else here".

**Note:** This is a different error than ISS-036 ("argument of type 'Symbol' is not iterable"). This error occurs when the variable is used in an expression, not just referenced.

## Test Case

**Setup:** Define variables with commas in subscripts, then use them in expressions.

**Expected:** Variables should work correctly in expressions.

**Actual:** Parsing fails with "I expected something else here" error.

### Minimal Reproduction

**Define variables with commas in subscripts:**
$PAR_{R2,umol} := 1413\ \frac{\text{µmol}}{s}$
$t_{day} := 86400\ \frac{s}{d}$

**Use variable with comma in subscript in an expression (THIS FAILS):**
$PAR_{R2} := PAR_{R2,umol} \cdot t_{day} == 10\,547\,988.48\ \text{mol/d}$ <!-- [mol/day] -->

**Also fails in other expressions:**
$PAR_{hdr,umol} := PAR_{R2,umol} + PAR_{R1,umol} ==
\\ \color{red}{\text{
    Error: Undefined variable: PAR\_\{R1,umol\}}}$ <!-- [µmol/s] -->
$PPE_{eff,avg} := \frac{PAR_{hdr,umol}}{P_{hdr,tot}} ==
\\ \color{red}{\text{
    Error: Undefined variable: PAR\_\{hdr,umol\}}}$ <!-- [µmol/J] -->

### Expected vs Actual

| | Value | Unit |
|---|---|---|
| **Expected** | 122.0832 | mol/day |
| **Actual** | Error: "Failed to parse LaTeX 'PAR_{R2,umol} \cdot t_{day}': I expected something else here" |

**Note:** The error message shows that the variable name is being normalized (comma → underscore) internally: `PAR_{R2_umol}`, but the parser still fails.

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_038_comma_subscript_expression_parse_error.md`
2. Process: `livemathtex process tests/test_iss_038_comma_subscript_expression_parse_error.md`
3. Observe: Expressions using variables with commas fail with "I expected something else here"

### Root Cause Analysis

**Expression parsing failure:** When variables with commas in subscripts are used in expressions (multiplication, division, addition), the parser fails with "I expected something else here". The variable name normalization (comma → underscore) happens, but the parser still can't handle the normalized form in expressions.

**The bug:** Variable name normalization may work for simple references, but fails when the variable is used in expressions. The parser expects a different syntax after normalization.

**Impact:** High - prevents using variables with commas in any calculations, which is common in scientific notation.

**Related Issues:**
- ISS-036: Variables with commas in subscripts fail with "argument of type 'Symbol' is not iterable" (different error, different context)
- ISS-034: Variable parsing fails for variables with commas in subscript (marked RESOLVED, but this is a different manifestation)

### Source Document

`mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

---

---

> *livemathtex: 2026-01-16 00:27:46 | 5 definitions, 3 evaluations | 2 errors | 0.06s* <!-- livemathtex-meta -->
