<!-- livemathtex: output=output.md, json=true, digits=4 -->

# Function Definitions - LiveMathTeX Example

This example demonstrates how to **define and use functions** in LiveMathTeX.

---

## 1. User-Defined Function

### Define Function

$PPE_{eff}(r) := (r \cdot 4.29 + (1 - r) \cdot 2.57) \cdot 0.9143$

This function calculates weighted photosynthetic photon efficacy (PPE) for LED mixtures, where `r` is the red LED fraction.

### Evaluate Function

$PPE_{result} := PPE_{eff}(0.90) == 3.7651$

The result shows that a 90% red LED mixture yields a PPE of approximately 3.77 µmol/J.

---

## 2. Built-in Mathematical Functions

LiveMathTeX supports standard mathematical functions directly:

### Trigonometric Functions

$angle := 0.5236$

$sin_v := \sin(angle) == 0.5$

$cos_v := \cos(angle) == 0.866$

$tan_v := \tan(angle) == 0.5774$

### Exponential and Logarithmic

$exp_v := \exp(2) == 7.3891$

$ln_v := \ln(10) == 2.3026$

### Square Root

$sqrt_v := \sqrt{144} == 12$

### Powers

$power_v := 2^{10} == 1\,024$

---

## 3. Combining Functions with Variables

### Define Base Values

$base := 100$

$factor := 1.5$

### Apply Mathematical Functions

$log_base := \ln(base) == 4.6052$

$scaled := base \cdot factor == 150$

$root_scaled := \sqrt{scaled} == 12.2474$

---

## Summary

| Feature | Syntax | Description |
|---------|--------|-------------|
| Define function | `f(x) := expr` | Creates reusable formula |
| Call function | `result := f(val) == expected` | Evaluates function |
| Built-in math | `sin(x)`, `sqrt{x}`, `ln(x)` | Standard functions |

**Key insight:** Functions make calculations reusable - define once, call with different inputs!

**Usage note:** Function calls use the format `result := func(value) == expected`

---

> *livemathtex: 2026-01-16 01:34:38 | 15 definitions, 11 evaluations | no errors | 0.10s* <!-- livemathtex-meta -->
