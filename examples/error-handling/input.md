<!-- livemathtex: output=output.md, json=true -->

# LiveMathTeX Error Catalog

This document demonstrates all error types that LiveMathTeX can produce, with explanations and fixes.

---

## Category 1: Variable Name Conflicts with Units

Single-letter variable names often conflict with Pint's unit database. Pint recognizes thousands of units including SI, imperial, astronomy, and more.

### Error: V conflicts with volt

$V := 37824$

**Explanation:** `V` is the SI symbol for volt. Use a subscript to disambiguate.

**Fix:**

$V_{tot} := 37824$
$V_{tot} ==$

### Error: m conflicts with meter

$m := 10$

**Fix:**

$m_1 := 10$
$m_1 ==$

### Error: s conflicts with second

$s := 5$

**Fix:**

$time_1 := 5$
$time_1 ==$

### Error: a conflicts with year (annum)

Even non-obvious letters conflict:

$a := 9.81$

**Fix:**

$accel := 9.81$

---

## Category 2: Undefined Variables in Formulas

When a symbol is referenced but never defined, LiveMathTeX produces an error. If the symbol also happens to be a unit name, the error message notes this.

### Error: Undefined variable (no unit conflict)

$y := x \cdot 2$

**Explanation:** `x` was never defined. LiveMathTeX does NOT assume undeclared symbols are zero or unity.

**Fix:** Define x first:

$x_1 := 5$
$y_1 := x_1 \cdot 2$
$y_1 ==$

### Error: Undefined variable that matches unit name (ISSUE-003 fix)

This is the critical fix - previously `V` in a formula with decimals would silently be interpreted as volt!

$Cap := V \cdot 15 \cdot 0.001$

**Explanation:** `V` matches the volt unit, but in a formula it should be a defined variable. The error message notes the unit conflict.

**Fix:** Use a subscript to disambiguate from the unit:

$V_{tot} := 37824$
$Cap_ok := V_{tot} \cdot 15 \cdot 0.001$
$Cap_ok ==$

### Error: Another unit-like variable (Newton)

$force := N \cdot 10.5$

**Explanation:** `N` matches the Newton unit. Same issue as `V` above.

**Fix:**

$N_val := 100$
$force_ok := N_val \cdot 10.5$
$force_ok ==$

---

## Category 3: Undefined Variables in Evaluation

When using `==` to evaluate an expression, all referenced symbols must be defined.

### Error: Bare evaluation of undefined symbol

$z ==$

**Fix:**

$z_1 := 42$
$z_1 ==$

### Error: Expression with undefined symbol

$result := q + 5 ==$

**Fix:**

$q_1 := 10$
$result_ok := q_1 + 5 ==$

---

## Category 4: Unrecognized Units

Unknown units are silently ignored - the value is stored without a unit. This can lead to unexpected results.

### Unknown unit is ignored

$x_{foo} := 5\ foo$
$x_{foo} ==$

Note: `foo` is not a recognized unit, so `x_foo` becomes just `5` (unitless).

### Another unknown unit

$y_{stuks} := 10\ stuks$
$y_{stuks} ==$

Same problem: `stuks` is not recognized, unit is lost.

### Solution: Define custom units first

Use `===` to define custom units before using them:

$stuks === stuks$
$aantal := 100\ stuks$
$aantal ==$

Now the custom unit is preserved:

$prijs_{per\_stuk} := 2.50\ €$
$n_{stuks} := 4\ stuks$

Note: Euro (`€`) is a built-in unit and works without definition.

---

## Category 5: Dimension Mismatch Errors

Adding or subtracting quantities with incompatible dimensions produces an error (ISSUE-006).

### Error: Adding mass and length

$mass_1 := 5\ kg$
$dist_1 := 3\ m$
$invalid_1 := mass_1 + dist_1 ==$

**Explanation:** Cannot add kilograms (mass) to meters (length). These have different physical dimensions.

### Error: Subtracting time and velocity

$time_1 := 10\ s$
$vel_1 := 5\ \frac{m}{s}$
$invalid_2 := time_1 - vel_1 ==$

**Explanation:** Cannot subtract velocity from time. Dimensions must match.

### Multiplication and division are OK

Different units CAN be multiplied or divided:

$prod := mass_1 \cdot dist_1 ==$
$velocity_1 := dist_1 / time_1 ==$

### Compatible units work fine

Same dimensions (even different scales) can be added:

$d_1 := 1\ km$
$d_2 := 500\ m$
$total_d := d_1 + d_2 ==$

---

## Category 6: Correct Usage Reference

These examples show the correct patterns to follow.

### Value definitions with units (backslash-space syntax)

$m_1 := 10\ kg$
$v_1 := 5\ \frac{m}{s}$
$E_1 := 1000\ kWh$
$g_{acc} := 9.81\ \frac{m}{s^2}$

### Formula definitions (operators between defined variables)

$F_1 := m_1 \cdot g_{acc}$
$F_1 ==$

### Unit conversions

$F_{1,N} := F_1 ==$ <!-- [N] -->

---

## Error Summary

| Category | Trigger | Solution |
|----------|---------|----------|
| Variable/Unit conflict | `V := 37824` | Use subscript: `V_tot := 37824` |
| Undefined variable | `y := x * 2` | Define x first |
| Undefined in eval | `x ==` | Define x first |
| Unknown unit (ignored!) | `5\ foo` | Use standard unit or define with `===` |
| Dimension mismatch | `kg + m` | Only add/subtract compatible dimensions |

---

**Last updated:** 2026-01-11

---

> *livemathtex: 2026-01-13 23:18:32 | cleared 0 evaluations | no errors | <1s* <!-- livemathtex-meta -->
