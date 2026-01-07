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

### Option 2: Descriptive names (with subscripts)

Note: Even descriptive names can conflict with Pint's unit database.
For example, `mass` is recognized as "milliarcsecond" (astronomy unit).
Always use subscripts to be safe.

$mass_{obj} := 25 \cdot kg$
$accel_{g} := 9.81 \cdot \frac{m}{s^2}$

Calculate force:
$F_2 := mass_{obj} \cdot accel_{g} == 245.2\ \text{kg} \cdot \text{m}/\text{s}^{2}$

Convert to Newtons:
$F_2N := F_2 == 245.2\ \text{N}$ <!-- [N] -->

Convert to kilonewtons:
$F_2kN := F_2 == 0.2452\ \text{kN}$ <!-- [kN] -->

## Compare Results

$ratio := \frac{mass_{obj}}{m_1} == 2.5$

The ratio should be 2.5 (25 kg / 10 kg).

---

## ❌ Intentional Errors (for demonstration)

### Error 1: Variable name conflicts with unit

This line tries to define `m` which conflicts with the SI unit meter:

$m := 10 \cdot kg
\\ \color{red}{\text{
    Error: Variable name 'm' conflicts with unit 'meter'. Use a subscript like 'm\_1' or 'm\_var' to disambiguate.}}$

### Error 2: Undefined variable in formula

This formula uses `g` (gravitational acceleration) which is NOT defined.
The tool correctly reports it as undefined:

$h_{drop} := 100$
$t_{fall} := \sqrt{\frac{2 \cdot h_{drop}}{g}} ==
\\ \color{red}{\text{
    Error: Undefined variable 'g' in formula. Note: 'g' is also a unit (gram), but formulas cannot mix variables and units. Define 'g' first with a subscript like g\_\{0\} or g\_\{acc\}.}}$

**Fix:** Define `g_{acc}` first (with subscript to avoid conflict with gram unit).

---

> *livemathtex: 2026-01-08 00:29:07 | 12 definitions, 6 evaluations | 2 errors | 0.38s* <!-- livemathtex-meta -->
