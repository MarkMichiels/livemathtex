<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-039: Thousands Separator Formatting

This test demonstrates the need for automatic thousands separator formatting in number output.

## Test Case

**Setup:** Large numbers should be formatted with thousands separators for readability

**Expected:** Numbers >= 1000 should display with thousands separators (e.g., `37,824` instead of `37824`)

**Actual:** Numbers are displayed without separators (e.g., `37824`)

### Minimal Reproduction

$V_{tot} := 192 \cdot 197\ L == 37\,824\ \text{L}$ <!-- [L] -->
<!-- Expected: 37,824 L -->
<!-- Actual: 37824 L (no separator) -->

$PAR_{hdr} := 273798276.1583\ mol/d ==
\\ \color{red}{\text{
    Error: Undefined variable: d}}$ <!-- [mol/day] -->
<!-- Expected: 273,798,276 mol/day -->
<!-- Actual: 273798276.1583 mol/day (no separator) -->

### Expected vs Actual

| Value | Expected | Actual |
|-------|----------|--------|
| 37,824 | `37,824\ \text{L}` | `37824\ \text{L}` |
| 273,798,276 | `273,798,276\ \text{mol/d}` | `273798276.1583\ \text{mol/d}` |

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_039_thousands_separator.md`
2. Process: `livemathtex process tests/test_iss_039_thousands_separator.md`
3. Observe: Numbers >= 1000 are displayed without thousands separators

### Root Cause Analysis

The number formatting in `_format_si_value()` and related functions doesn't add thousands separators. This makes large numbers harder to read in scientific/engineering documents.

### Impact

Medium - Improves readability of large numbers in documents, especially for engineering calculations with values in thousands/millions.

### Feature Request

Add automatic thousands separator formatting:
- Option 1: Always format numbers >= 1000 with separators
- Option 2: Configurable via `<!-- format:thousands -->` or document setting
- Option 3: Use locale-aware formatting (US: comma, EU: space or period)

**Preferred:** Option 2 (configurable) with default enabled for numbers >= 1000.

**⚠️ CRITICAL REQUIREMENT - Idempotence:**
Settings must be preserved after `process` and `clear` cycles:
- After `process`: `37824` → `37,824` (formatted with separator)
- After `clear`: `37,824` → `37824` (original value restored, separator setting preserved in comment)
- After `process` again: `37824` → `37,824` (re-formatted correctly using preserved setting)

This ensures the document remains stable and can be processed multiple times without losing formatting preferences.

---

---

> *livemathtex: 2026-01-16 00:27:46 | 2 definitions, 2 evaluations | 1 error | 0.06s* <!-- livemathtex-meta -->
