# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## Single-Letter Variables (Now Supported!)

Using single-letter names that look like SI units - LiveMathTeX knows the context:

**Left of `:=` → always a variable:**
$m := 10 \cdot kg$

$s := 5$

$t := 10 \cdot s$

**Test: use `m` as variable AND `m` as unit in same formula:**
$distance := m \cdot t == 50 \text{m}$ <!-- [m] -->

## Alternative: Subscripts or Descriptive Names

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

> *livemathtex: 2026-01-05 03:28:17 | 13 definitions, 7 evaluations | no errors | 0.23s* <!-- livemathtex-meta -->
