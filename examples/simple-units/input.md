# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## Single-Letter Variables (Now Supported!)

Using single-letter names that look like SI units - LiveMathTeX knows the context:

**Left of `:=` → always a variable:**
$m := 10 \cdot kg$

$s := 5$

$t := 10 \cdot s$

**Test: use `m` as variable AND `m` as unit in same formula:**
$distance := m \cdot t ==$ <!-- [m] -->

## Alternative: Subscripts or Descriptive Names

### Option 1: Subscript notation (m_1, t_1, etc.)

$m_1 := 10 \cdot kg$
$a_1 := 9.81 \cdot \frac{m}{s^2}$

Calculate force:
$F_1 := m_1 \cdot a_1 ==$

### Option 2: Descriptive names

$mass := 25 \cdot kg$
$accel := 9.81 \cdot \frac{m}{s^2}$

Calculate force (without unit conversion):
$F_2 := mass \cdot accel ==$

Calculate force (with unit conversion to N):
$F_3 := mass \cdot accel ==$ <!-- [N] -->

$accel == $ <!-- [mm] -->

## Compare Results

$ratio_1 := \frac{F_2}{F_1} == $

$ratio_2 := \frac{F_3}{F_1} == $

The ratio should be 2.5 (25 kg / 10 kg).
