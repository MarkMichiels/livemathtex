<!-- livemathtex: output=output.md, json=true -->

# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## ⚠️ Single-Letter Variables: Use With Care!

Single-letter names like `m`, `s`, `t` CAN be used as variables, but they will
**shadow** the corresponding SI units in the same document.

**Example of the problem:**

If you write `m := 10 · kg` and then `accel := 9.81 · m/s²`, the `m` in the
acceleration formula becomes `10 kg` instead of `meter`!

**Best practice:** Use subscripts or descriptive names to avoid conflicts.

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

> *livemathtex: 2026-01-07 03:13:48 | 9 definitions, 5 evaluations | no errors | 0.21s* <!-- livemathtex-meta -->
