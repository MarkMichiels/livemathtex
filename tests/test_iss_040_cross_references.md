<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-040: Cross-References to Calculated Values in Text

This test demonstrates the need for referencing calculated variables in regular text (outside math blocks).

## Test Case

**Setup:** Reference calculated values in prose text (e.g., executive summary, conclusions)

**Expected:** Can reference variables like `$C_{max}$` in text to display calculated values

**Actual:** Variables in text are not evaluated (or require full math block syntax)

### Minimal Reproduction

$C_{max} := 550\ kg$
$T_{2030} := 516\ kg$

**Executive Summary:**

The maximum capacity is **$C_{max}$ kg/year** and the 2030 target is **$T_{2030}$ kg/year**.

<!-- Expected: "The maximum capacity is **550 kg/year** and the 2030 target is **516 kg/year**." -->
<!-- Actual: Variables are not substituted in text -->

### Expected vs Actual

| Location | Expected | Actual |
|----------|----------|--------|
| Text reference | `**550 kg/year**` | `**$C_{max}$ kg/year**` (not evaluated) |

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_040_cross_references.md`
2. Process: `livemathtex process tests/test_iss_040_cross_references.md`
3. Observe: Variables in text are not substituted with their values

### Root Cause Analysis

LiveMathTeX only processes math blocks (`$...$`), not inline variable references in text. This requires manual copy-paste of calculated values into prose sections.

### Impact

High - Enables "single source of truth" documents where calculated values automatically appear in executive summaries, conclusions, and other prose sections. Reduces manual errors from copy-paste.

### Feature Request

Add syntax for inline variable references in text:
- Option 1: `{{variable}}` syntax (e.g., `{{C_max}}` → `550 kg`)
- Option 2: `$variable$` in text (outside math blocks) gets evaluated
- Option 3: Special syntax like `\ref{C_max}` or `@C_max`

**Preferred:** Option 1 (`{{variable}}`) to distinguish from math blocks and allow unit formatting.

**⚠️ CRITICAL REQUIREMENT - Idempotence:**
Settings must be preserved after `process` and `clear` cycles:
- After `process`: `{{C_max}}` → `550 kg` (evaluated)
- After `clear`: `{{C_max}}` → `{{C_max}}` (original syntax restored)
- After `process` again: `{{C_max}}` → `550 kg` (re-evaluated correctly)

This ensures the document remains stable and can be processed multiple times without losing the original syntax.

**Example:**
```markdown
The maximum capacity is **{{C_max}} kg/year**.
The 2030 target is **{{T_2030}} kg/year**, which is **{{T_2030 / C_max * 100}}%** of maximum.
```

---

---

> *livemathtex: 2026-01-16 00:27:47 | 2 definitions | no errors | 0.06s* <!-- livemathtex-meta -->
