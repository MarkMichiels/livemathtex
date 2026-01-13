# Phase 13 Plan: SI Value Fix (ISS-023)

## Goal

Fix `_format_si_value()` and `_extract_unit_string()` LaTeX cleanup that produces malformed output by removing ALL `}` characters instead of just `\text{}` wrappers.

## Problem

**Current code (lines 1313, 1339):**
```python
result.replace('\\text{', '').replace('}', '')  # WRONG - removes ALL }
```

**Example bug:**
- SymPy LaTeX output: `\frac{7.62969 \times 10^{7} \text{kg}}{\text{m}^{3}}`
- After `.replace('\\text{', '')`: `\frac{7.62969 \times 10^{7} kg}{m^{3}}` (correct)
- After `.replace('}', '')`: `\frac{7.62969 \times 10^{7} kg{m^{3` (MALFORMED)

## Solution

Use regex to match and remove only `\text{...}` pairs:
```python
import re
re.sub(r'\\text\{([^}]+)\}', r'\1', result)
```

This extracts the content inside `\text{}` without breaking other braces.

## Tasks

### 13-01: Fix LaTeX cleanup in evaluator.py

1. **Line 1313** (`_extract_unit_string()`):
   - Change: `sympy.latex(unit_part).replace('\\text{', '').replace('}', '')`
   - To: `re.sub(r'\\text\{([^}]+)\}', r'\1', sympy.latex(unit_part))`

2. **Line 1339** (`_format_si_value()`):
   - Change: `result.replace('\\cdot', '*').replace('\\text{', '').replace('}', '')`
   - To: `re.sub(r'\\text\{([^}]+)\}', r'\1', result.replace('\\cdot', '*'))`

3. **Add test**: Verify SI fallback output is valid LaTeX (can be parsed without KaTeX errors)

## Verification

1. Run existing tests: `pytest tests/`
2. Process a document with unit conversion warnings
3. Verify output LaTeX is well-formed (balanced braces)

## Effort

~15 minutes (simple regex fix + test)

---

*Plan created: 2026-01-13*
