# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## ❌ Common Mistakes (These Will Error)

Using single-letter names that conflict with SI units:

$m := 10 \text{kg}$

$s := 5$

$t := 10$

## ✅ Correct Approach: Use Subscripts or Descriptive Names

### Option 1: Subscript notation (m_1, t_1, etc.)

$m_1 := 10 \text{kg}$
$a_1 := 9.81 \frac{m}{s^{2}}$

Calculate force:
$F_1 := a_1 \cdot m_1 == 39.24 \text{kg}^{2}$

### Option 2: Descriptive names

$mass := 25 \text{kg}$
$accel := 9.81 \frac{m}{s^{2}}$

Calculate force (without unit conversion):
$F_2 := \text{accel} \cdot \text{mass} == 98.1 \text{kg}^{2}$

Calculate force (with unit conversion to N):
$F_3 := \text{accel} \cdot \text{mass} == 98.1 \frac{\text{kg} \cdot \text{N} \cdot \text{s}^{2}}{\text{m}}$ <!-- [N] -->

$\text{accel} == 3924 \frac{\text{kg} \cdot \text{mm}}{\text{m}}$ <!-- [mm] -->

## Compare Results

$ratio_1 := \frac{F_2}{F_1} == 2.5$

$ratio_2 := \frac{F_3}{F_1} == 2.5$

The ratio should be 2.5 (25 kg / 10 kg).

---

> *livemathtex: 2026-01-05 01:37:29 | 12 definitions, 6 evaluations | no errors | 0.28s* <!-- livemathtex-meta -->
