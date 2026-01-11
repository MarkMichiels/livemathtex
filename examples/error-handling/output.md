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
$V_{tot} == 37\,820$

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
$\text{time}_1 == 5$

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
    Error: Undefined variable 'x'. Define it first with a definition like '\$x := <value>\$'.}}$

**Explanation:** `x` was never defined. LiveMathTeX does NOT assume undeclared symbols are zero or unity.

**Fix:** Define x first:

$x_1 := 5$
$y_1 := x_1 \cdot 2$
$y_1 == 10$

### Error: Undefined variable that matches unit name (ISSUE-003 fix)

This is the critical fix - previously `V` in a formula with decimals would silently be interpreted as volt!

$Cap := V \cdot 15 \cdot 0.001
\\ \color{red}{\text{
    Error: Undefined variable 'V'. (Note: 'V' is also a unit (volt). Units must be attached to numbers like '5\textbackslash\{\} V', not used as standalone symbols in formulas.)}}$

**Explanation:** `V` matches the volt unit, but in a formula it should be a defined variable. The error message notes the unit conflict.

**Fix:** Use a subscript to disambiguate from the unit:

$V_{tot} := 37824$
$Cap_ok := V_{tot} \cdot 15 \cdot 0.001$
$\text{Cap}_{ok} == 567.4$

### Error: Another unit-like variable (Newton)

$force := N \cdot 10.5
\\ \color{red}{\text{
    Error: Undefined variable 'N'. (Note: 'N' is also a unit (newton). Units must be attached to numbers like '5\textbackslash\{\} N', not used as standalone symbols in formulas.)}}$

**Explanation:** `N` matches the Newton unit. Same issue as `V` above.

**Fix:**

$N_val := 100$
$force_ok := N_val \cdot 10.5$
$\text{force}_{ok} == 1050$

---

## Category 3: Undefined Variables in Evaluation

When using `==` to evaluate an expression, all referenced symbols must be defined.

### Error: Bare evaluation of undefined symbol

$z ==
\\ \color{red}{\text{
    Error: Undefined variable 'z'. Define it first with a definition like '\$z := <value>\$'.}}$

**Fix:**

$z_1 := 42$
$z_1 == 42$

### Error: Expression with undefined symbol

$result := q + 5 ==
\\ \color{red}{\text{
    Error: Undefined variable 'q'. Define it first with a definition like '\$q := <value>\$'.}}$

**Fix:**

$q_1 := 10$
$result_ok := q_1 + 5 == 15$

---

## Category 4: Unrecognized Units

When a unit is specified but not recognized by Pint or custom definitions.

### Error: Unrecognized unit in value definition

$x := 5\ foo$

**Explanation:** `foo` is not a recognized unit. Check spelling or define it with `===`.

**Fix (using standard unit):**

$x_ok := 5\ m$
$x_{\text{ok}} == 5\ \text{m}$

### Error: Unrecognized unit in conversion comment

$y_val := 1000$
$y_conv := y_val == 1000$ <!-- [bar_invalid_unit] -->

**Fix (using recognized unit):**

$y_val2 := 100000$
$y_conv2 := y_val2 == 100\,000$ <!-- [Pa] -->

---

## Category 5: Correct Usage Reference

These examples show the correct patterns to follow.

### Value definitions with units (backslash-space syntax)

$mass := 10\ kg
\\ \color{red}{\text{
    Error: Variable name 'mass' conflicts with unit 'milliarcsecond'. Use a subscript like 'mass\_1' or 'mass\_var' to disambiguate.}}$
$speed := 5\ \frac{m}{s}$
$energy := 1000\ kWh$

### Formula definitions (operators between defined variables)

$force := mass \cdot 9.81
\\ \color{red}{\text{
    Error: Undefined variable 'a'. (Note: 'a' is also a unit (unit). Units must be attached to numbers like '5\textbackslash\{\} a', not used as standalone symbols in formulas.)}}$
$force ==
\\ \color{red}{\text{
    Error: Undefined variable 'c'. (Note: 'c' is also a unit (unit). Units must be attached to numbers like '5\textbackslash\{\} c', not used as standalone symbols in formulas.)}}$

### Unit conversions

$force_N := force ==
\\ \color{red}{\text{
    Error: Undefined variable 'c'. (Note: 'c' is also a unit (unit). Units must be attached to numbers like '5\textbackslash\{\} c', not used as standalone symbols in formulas.)}}$ <!-- [N] -->

### Custom unit definition

$€ === €$
$cost := 100\ €$
$\text{cost} == 100\ \text{€}$

---

## Error Summary

| Category | Trigger | Solution |
|----------|---------|----------|
| Variable/Unit conflict | `V := 37824` | Use subscript: `V_tot := 37824` |
| Undefined variable | `y := x * 2` | Define x first |
| Undefined in eval | `x ==` | Define x first |
| Unrecognized unit | `5\ foo` | Use standard unit or define with `===` |

---

**Last updated:** 2026-01-11

---

> *livemathtex: 2026-01-11 17:33:02 | 33 definitions, 16 evaluations | 13 errors | 0.41s* <!-- livemathtex-meta -->
