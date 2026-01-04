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
$F_1 := m_1 \cdot a_1 ==$

### Option 2: Descriptive names

$mass := 25 \cdot kg$
$accel := 9.81 \cdot \frac{m}{s^2}$

Calculate force:
$F_2 := mass \cdot accel ==$

## Compare Results

$ratio := \frac{F_2}{F_1} ==$

The ratio should be 2.5 (25 kg / 10 kg).
