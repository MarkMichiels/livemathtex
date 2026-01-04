# Newton's Second Law: F = m × a

This example demonstrates SI units and variable naming.

## ❌ Common Mistakes (These Will Error)

Using single-letter names that conflict with SI units:

$m := 10 \cdot kg \\ \color{red}{\text{Error: Variable name 'm' conflicts with SI unit 'm'. Use a different name like 'm\_val' or 'my\_m'.}}$

$s := 5 \\ \color{red}{\text{Error: Variable name 's' conflicts with SI unit 's'. Use a different name like 's\_val' or 'my\_s'.}}$

$t := 10 \\ \color{red}{\text{Error: Variable name 't' conflicts with SI unit 't'. Use a different name like 't\_val' or 'my\_t'.}}$

## ✅ Correct Approach: Use Subscripts or Descriptive Names

### Option 1: Subscript notation (m_1, t_1, etc.)

$m_1 := 10 \text{kg}$
$a_1 := 9.81 \frac{m}{s^{2}}$

Calculate force:
$F_1 := a_1 \cdot m_1 == 98.1 \frac{\text{kg} \cdot \text{m}}{\text{s}^{2}}$

### Option 2: Descriptive names

$mass := 25 \text{kg}$
$accel := 9.81 \frac{m}{s^{2}}$

Calculate force:
$F_2 := \text{accel} \cdot \text{mass} == 245.25 \frac{\text{kg} \cdot \text{m}}{\text{s}^{2}}$

## Compare Results

$ratio := \frac{F_2}{F_1} == 2.5$

The ratio should be 2.5 (25 kg / 10 kg).

---

> *livemathtex: 2026-01-04 20:47:36 | 10 definitions, 3 evaluations | 3 errors | 0.16s* <!-- livemathtex-meta -->
