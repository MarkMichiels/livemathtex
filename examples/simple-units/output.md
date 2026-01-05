# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## ❌ Common Mistakes (These Will Error)

Using single-letter names that conflict with SI units:

$m := 10 \cdot kg$

$s := 5$

$t := 10$

## ✅ Correct Approach: Use Subscripts or Descriptive Names

### Option 1: Subscript notation (m_1, t_1, etc.)

$m_1 := 10 \cdot kg$
$a_1 := 9.81 \cdot \frac{m}{s^2}$

Calculate force:
$F_1 := m_1 \cdot a_1 == 39.24 \text{kg}^{2}$

### Option 2: Descriptive names

$mass := 25 \cdot kg$
$accel := 9.81 \cdot \frac{m}{s^2}$

Calculate force (without unit conversion):
$F_2 := mass \cdot accel == 98.1 \text{kg}^{2}$

Calculate force (with unit conversion to N):
$F_3 := mass \cdot accel == 98.1 \text{kg}^{2}$ <!-- [N] -->

$\text{accel} == 3.924 \text{kg}$ <!-- [mm] -->

## Compare Results

$ratio_1 := \frac{F_2}{F_1} == 2.5$

$ratio_2 := \frac{F_3}{F_1} == 2.5$

The ratio should be 2.5 (25 kg / 10 kg).

---

> *livemathtex: 2026-01-05 03:26:21 | 12 definitions, 6 evaluations | no errors | 0.23s* <!-- livemathtex-meta -->
