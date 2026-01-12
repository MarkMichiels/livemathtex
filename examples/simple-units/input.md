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

$m_1 := 10\ kg$
$a_1 := 9.81\ \frac{m}{s^2}$

Calculate force:
$F_1 := m_1 \cdot a_1 ==$

### Option 2: Descriptive names (with subscripts)

Note: Even descriptive names can conflict with Pint's unit database.
For example, `mass` is recognized as "milliarcsecond" (astronomy unit).
Always use subscripts to be safe.

$mass_{obj} := 25\ kg$
$accel_{g} := 9.81\ \frac{m}{s^2}$

Calculate force:
$F_2 := mass_{obj} \cdot accel_{g} ==$

Convert to Newtons (HTML comment syntax):
$F_2N := F_2 ==$ <!-- [N] -->

Convert to kilonewtons (HTML comment syntax):
$F_2kN := F_2 ==$ <!-- [kN] -->

Convert to Newtons (inline syntax - recommended):
$F_2N_inline := F_2 == [N]$

Convert to kilonewtons (inline syntax - recommended):
$F_2kN_inline := F_2 == [kN]$

## Compare Results

$ratio := \frac{mass_{obj}}{m_1} == $

The ratio should be 2.5 (25 kg / 10 kg).

---

## ❌ Intentional Errors (for demonstration)

### Error 1: Variable name conflicts with unit

This line tries to define `m` which conflicts with the SI unit meter:

$m := 10\ kg$

### Error 2: Undefined variable in formula

This formula uses `g` (gravitational acceleration) which is NOT defined.
The tool correctly reports it as undefined:

$h_{drop} := 100$
$t_{fall} := \sqrt{\frac{2 \cdot h_{drop}}{g}} ==$

**Fix:** Define `g_{acc}` first (with subscript to avoid conflict with gram unit).
