<!-- livemathtex: output=output.md, json=true -->

# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## ⚠️ Single-Letter Variables: Error Detection

Single-letter names like `m`, `s`, `t` that conflict with SI units will
**generate an error** to prevent ambiguity.

**Example:**

Writing `m := 10 · kg` produces:

> Error: Variable name 'm' conflicts with unit 'm' (meter). 
> Use a subscript like m_{var} or m_{0} to disambiguate.

**Solution:** Use subscripts or descriptive names to avoid conflicts.

## ✅ Recommended: Subscripts or Descriptive Names

### Option 1: Subscript notation (m_1, t_1, etc.)

$m_1 := 10 \cdot kg$
$a_1 := 9.81 \cdot \frac{m}{s^2}$

Calculate force:
$F_1 := m_1 \cdot a_1 == 98.1\ \text{kg} \cdot \text{m}/\text{s}^{2}$

### Option 2: Descriptive names

$mass := 25 \cdot kg$
$accel := 9.81 \cdot \frac{m}{s^2}$

Calculate force:
$F_2 := mass \cdot accel == 245.2\ \text{kg} \cdot \text{m}/\text{s}^{2}$

Convert to Newtons:
$F_2N := F_2 == 245.2\ \text{N}$ <!-- [N] -->

Convert to kilonewtons:
$F_2kN := F_2 == 0.2452\ \text{kN}$ <!-- [kN] -->

## Compare Results

$ratio := \frac{mass}{m_1} == 2.5$

The ratio should be 2.5 (25 kg / 10 kg).

---

> *livemathtex: 2026-01-07 03:19:09 | 9 definitions, 5 evaluations | no errors | 0.21s* <!-- livemathtex-meta -->
