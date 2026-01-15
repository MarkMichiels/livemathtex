<!-- livemathtex: output=output.md, json=true -->

# Configuration Settings Demo

This example demonstrates all livemathtex configuration settings using **expression-level overrides**. Each calculation shows the same value formatted differently to illustrate what each setting does.

---

## Test Values

First, let's define some test values:

$\pi_{approx} := 3.141592653589793$
$large := 123456789.123456$
$small := 0.00000123456789$
$medium := 42.5$

---

## 1. The `digits` Setting

Controls the number of **significant figures** in numeric output.

| Setting | Description |
|---------|-------------|
| `digits:2` | 2 significant figures |
| `digits:4` | 4 significant figures (default) |
| `digits:6` | 6 significant figures |
| `digits:10` | 10 significant figures |

### Examples

**2 significant figures:**
$\pi_{approx} == 3.14$ <!-- digits:2 -->

**4 significant figures (default):**
$\pi_{approx} == 3.1416$

**6 significant figures:**
$\pi_{approx} == 3.141593$ <!-- digits:6 -->

**10 significant figures:**
$\pi_{approx} == 3.1415926536$ <!-- digits:10 -->

---

## 2. The `format` Setting

Controls **how numbers are displayed**. Four options available:

| Format | Description | Example |
|--------|-------------|---------|
| `general` | Auto-switches based on magnitude (default) | 1234 or 1.234e+08 |
| `decimal` | Fixed decimal places | 1234.5678 |
| `scientific` | Always exponential notation | 1.235e+03 |
| `engineering` | Exponents in multiples of 3 | 1.235e3, 123.5e6 |

### 2.1 General Format (Default)

Auto-switches between decimal and scientific notation based on `exponential_threshold`:

$large == 123\,456\,789.1235$

$medium == 42.5$

$small == 1.2346e-06$

### 2.2 Scientific Format

Always uses exponential notation (`1.23e+04`):

$large == 123\,456\,789.1235$ <!-- format:scientific -->

$medium == 42.5$ <!-- format:scientific -->

$small == 1.2346e-06$ <!-- format:scientific -->

### 2.3 Engineering Format

Like scientific, but exponents are always multiples of 3 (kilo, mega, milli, micro):

$large == 123\,456\,789.1235$ <!-- format:engineering -->

$medium == 42.5$ <!-- format:engineering -->

$small == 1.2346e-06$ <!-- format:engineering -->

### 2.4 Decimal Format

Fixed number of decimal places (digits = decimal places, not significant figures):

$medium == 42.5$ <!-- format:decimal digits:2 -->

$medium == 42.5$ <!-- format:decimal digits:4 -->

$medium == 42.5$ <!-- format:decimal digits:6 -->

---

## 3. Combining Settings

You can combine multiple settings in one override:

### High Precision Scientific
$large == 123\,456\,789.123456$ <!-- digits:8 format:scientific -->

### Engineering with 6 Digits
$large == 123\,456\,789.123456$ <!-- digits:6 format:engineering -->

### Low Precision Decimal
$\pi_{approx} == 3.14$ <!-- digits:2 format:decimal -->

---

## 4. Real-World Examples

### Financial Calculation

$price := 1299.99$
$tax_rate := 0.21$
$total := price \cdot (1 + tax_rate) == 1\,572.99$ <!-- digits:2 format:decimal -->

### Scientific Measurement

$wavelength := 0.000000532$
$wavelength == 5.320e-07$ <!-- format:scientific digits:3 -->

### Engineering Value

$power := 2500000$
$power == 2\,500\,000$ <!-- format:engineering digits:3 -->

---

## Summary

| Setting | Syntax | Effect |
|---------|--------|--------|
| `digits:N` | `<!-- digits:4 -->` | N significant figures |
| `format:general` | `<!-- format:general -->` | Auto decimal/scientific |
| `format:scientific` | `<!-- format:sci -->` | Always `1.23e+04` |
| `format:engineering` | `<!-- format:eng -->` | Powers of 3: `1.23e3` |
| `format:decimal` | `<!-- format:decimal -->` | Fixed decimal places |

**Shortcuts:** `sci` = `scientific`, `eng` = `engineering`

**Combining:** `<!-- digits:6 format:scientific -->`

---

> *livemathtex: 2026-01-15 11:21:16 | 9 definitions, 22 evaluations | no errors | 0.07s* <!-- livemathtex-meta -->
