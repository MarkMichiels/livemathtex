<!-- livemathtex: output=output.md, json=true -->

# LiveMathTeX Error Catalog

This document demonstrates all error types that LiveMathTeX can produce, with explanations and fixes.

---

## Category 1: Variable Name Conflicts with Units

Single-letter variable names often conflict with Pint's unit database. Pint recognizes thousands of units including SI, imperial, astronomy, and more.

### Error: V conflicts with volt

$V := 37824
\\ \color{red}{\text{
    Error: Variable name 'V' conflicts with unit 'volt'. Use a subscript like 'V\_1' or 'V\_var' to disambiguate.}}$

**Explanation:** `V` is the SI symbol for volt. Use a subscript to disambiguate.

**Fix:**

$V_{tot} := 37824$
$V_{tot} == 37\,824$

### Error: m conflicts with meter

$m := 10
\\ \color{red}{\text{
    Error: Variable name 'm' conflicts with unit 'meter'. Use a subscript like 'm\_1' or 'm\_var' to disambiguate.}}$

**Fix:**

$m_1 := 10$
$m_1 == 10$

### Error: s conflicts with second

$s := 5
\\ \color{red}{\text{
    Error: Variable name 's' conflicts with unit 'second'. Use a subscript like 's\_1' or 's\_var' to disambiguate.}}$

**Fix:**

$time_1 := 5$
$time_1 == 5$

### Error: a conflicts with year (annum)

Even non-obvious letters conflict:

$a := 9.81
\\ \color{red}{\text{
    Error: Variable name 'a' conflicts with unit 'year'. Use a subscript like 'a\_1' or 'a\_var' to disambiguate.}}$

**Fix:**

$accel := 9.81$

---

## Category 2: Undefined Variables in Formulas

When a symbol is referenced but never defined, LiveMathTeX produces an error. If the symbol also happens to be a unit name, the error message notes this.

### Error: Undefined variable (no unit conflict)

$y := x \cdot 2
\\ \color{red}{\text{
    Error: Undefined variable: x}}$

**Explanation:** `x` was never defined. LiveMathTeX does NOT assume undeclared symbols are zero or unity.

**Fix:** Define x first:

$x_1 := 5$
$y_1 := x_1 \cdot 2$
$y_1 == 10$

### Error: Undefined variable that matches unit name (ISSUE-003 fix)

This is the critical fix - previously `V` in a formula with decimals would silently be interpreted as volt!

$Cap := V \cdot 15 \cdot 0.001
\\ \color{red}{\text{
    Error: Undefined variable: V}}$

**Explanation:** `V` matches the volt unit, but in a formula it should be a defined variable. The error message notes the unit conflict.

**Fix:** Use a subscript to disambiguate from the unit:

$V_{tot} := 37824$
$Cap_ok := V_{tot} \cdot 15 \cdot 0.001$
$Cap_ok == 567.36$

### Error: Another unit-like variable (Newton)

$force := N \cdot 10.5
\\ \color{red}{\text{
    Error: Undefined variable: N}}$

**Explanation:** `N` matches the Newton unit. Same issue as `V` above.

**Fix:**

$N_val := 100$
$force_ok := N_val \cdot 10.5$
$force_ok == 1\,050$

---

## Category 3: Undefined Variables in Evaluation

When using `==` to evaluate an expression, all referenced symbols must be defined.

### Error: Bare evaluation of undefined symbol

$z ==
\\ \color{red}{\text{
    Error: Undefined variable: z}}$

**Fix:**

$z_1 := 42$
$z_1 == 42$

### Error: Expression with undefined symbol

$result := q + 5 ==
\\ \color{red}{\text{
    Error: Undefined variable: q}}$

**Fix:**

$q_1 := 10$
$result_ok := q_1 + 5 == 15$

---

## Category 4: Unrecognized Units

Unknown units are silently ignored - the value is stored without a unit. This can lead to unexpected results.

### Unknown unit is ignored

$x_{foo} := 5\ foo
\\ \color{red}{\text{
    Error: Unexpected token after expression: variable 'foo' at position 3}}$
$x_{foo} ==
\\ \color{red}{\text{
    Error: Undefined variable: x\_\{foo\}}}$

Note: `foo` is not a recognized unit, so `x_foo` becomes just `5` (unitless).

### Another unknown unit

$y_{stuks} := 10\ stuks
\\ \color{red}{\text{
    Error: Unexpected token after expression: variable 'stuks' at position 4}}$
$y_{stuks} ==
\\ \color{red}{\text{
    Error: Undefined variable: y\_\{stuks\}}}$

Same problem: `stuks` is not recognized, unit is lost.

### Solution: Define custom units first

Use `===` to define custom units before using them:

$stuks === stuks$
$aantal := 100\ stuks$
$aantal == 100\ \text{stuks}$

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
$invalid_1 := mass_1 + dist_1 ==
\\ \color{red}{\text{
    Error: Cannot convert from 'kilogram' ([mass]) to 'meter' ([length])}}$

**Explanation:** Cannot add kilograms (mass) to meters (length). These have different physical dimensions.

### Error: Subtracting time and velocity

$time_1 := 10\ s$
$vel_1 := 5\ \frac{m}{s}$
$invalid_2 := time_1 - vel_1 ==
\\ \color{red}{\text{
    Error: Cannot convert from 'second' ([time]) to 'meter / second' ([length] / [time])}}$

**Explanation:** Cannot subtract velocity from time. Dimensions must match.

### Multiplication and division are OK

Different units CAN be multiplied or divided:

$prod := mass_1 \cdot dist_1 == 15\ \text{kg·m}$
$velocity_1 := dist_1 / time_1 == 0.3\ \text{m/s}$

### Compatible units work fine

Same dimensions (even different scales) can be added:

$d_1 := 1\ km$
$d_2 := 500\ m$
$total_d := d_1 + d_2 == 1.5\ \text{km}$

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
$F_1 == 98.1\ \text{kg·m/s^2}$

### Unit conversions

$F_{1,N} := F_1 == 98.1\ \text{N}$ <!-- [N] -->

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

> *livemathtex: 2026-01-15 11:30:38 | 43 definitions, 20 evaluations | 14 errors | 0.08s* <!-- livemathtex-meta -->
