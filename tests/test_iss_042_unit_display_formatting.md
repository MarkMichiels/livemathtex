<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-042: Better Unit Display Formatting

This test demonstrates the need for better unit formatting options (e.g., `mg/(L·d)` vs `mg/d/L`).

## Test Case

**Setup:** Compound units can be displayed in multiple formats

**Expected:** Can control unit display format (e.g., prefer `mg/(L·d)` over `mg/d/L`)

**Actual:** Units are displayed in Pint's default format (e.g., `mg/d/L`)

### Minimal Reproduction

$\gamma_{max} := \frac{m_{ax,rct}}{V_{rct}} ==
\\ \color{red}{\text{
    Error: Undefined variable: m\_\{ax,rct\}}}$ <!-- [mg/L/day] -->
<!-- Expected: 76.30 mg/(L·d) or 76.30 mg·L⁻¹·d⁻¹ -->
<!-- Actual: 76.30 mg/d/L (Pint default) -->

### Expected vs Actual

| Unit | Expected Format | Actual Format |
|------|----------------|---------------|
| mg/L/day | `mg/(L·d)` or `mg·L⁻¹·d⁻¹` | `mg/d/L` |
| µmol/J | `µmol/J` or `µmol·J⁻¹` | `micromol/J` |

### Steps to Reproduce

1. Clear: `livemathtex clear tests/test_iss_042_unit_display_formatting.md`
2. Process: `livemathtex process tests/test_iss_042_unit_display_formatting.md`
3. Observe: Units are displayed in Pint's default format

### Root Cause Analysis

Unit formatting uses Pint's default string representation, which may not match preferred scientific notation (e.g., `mg/(L·d)` vs `mg/d/L`).

### Impact

Low-Medium - Improves readability and matches scientific conventions. Some journals prefer specific unit formats.

### Feature Request

Add unit formatting options:
- Option 1: Prefer fraction notation: `mg/(L·d)` instead of `mg/d/L`
- Option 2: Use negative exponents: `mg·L⁻¹·d⁻¹`
- Option 3: Configurable via `<!-- unit-format:fraction -->` or document setting
- Option 4: Preserve user's unit hint format when possible

**Preferred:** Option 3 (configurable) with sensible defaults.

**⚠️ CRITICAL REQUIREMENT - Idempotence:**
Settings must be preserved after `process` and `clear` cycles:
- After `process`: Units formatted according to setting (e.g., `mg/(L·d)`)
- After `clear`: Unit format setting preserved in comment, formatted unit removed
- After `process` again: Units re-formatted correctly using preserved setting

This ensures the document remains stable and can be processed multiple times without losing formatting preferences.

**Example:**
```markdown
$\gamma_{max} ==$ <!-- [mg/L/day] unit-format:fraction -->
<!-- Output: 76.30 mg/(L·d) -->

$\gamma_{max} ==$ <!-- [mg/L/day] unit-format:exponent -->
<!-- Output: 76.30 mg·L⁻¹·d⁻¹ -->
```

---

---

> *livemathtex: 2026-01-16 00:27:47 | 1 definition, 1 evaluation | 1 error | 0.06s* <!-- livemathtex-meta -->
