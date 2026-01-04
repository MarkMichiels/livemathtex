# Livemathtex - Syntax Reference

## Quick Reference

| Syntax | Meaning | Example |
|--------|---------|---------|
| `:=` | Definition (assign) | `x := 5` |
| `=` | Evaluation (compute) | `y = x + 1` |
| `=>` | Symbolic / highlight | `diff(x^2, x) =>` |
| `#` | Comment | `# this is ignored` |

---

## Definitions

### Variable Definition

```latex
$x := 5$
$mass := 10\ \text{kg}$
$\alpha := 0.5$
$T_{ambient} := 25\ \text{°C}$
```

**Rules:**
- Left side must be a valid variable name
- Right side is any expression
- No output is generated (definition only)
- Variable is available for subsequent calculations

### Function Definition

```latex
$f(x) := x^2 + 2x + 1$
$g(x, y) := x^2 + y^2$
$\text{area}(r) := \pi \cdot r^2$
```

**Rules:**
- Parameters in parentheses
- Single expression body
- Can reference previously defined variables

### Constant Definition

```latex
$g := 9.81\ \text{m/s}^2$
$c := 299792458\ \text{m/s}$
$\pi := 3.14159$  <!-- overrides built-in -->
```

---

## Evaluations

### Numeric Evaluation (`=`)

```latex
$F = m \cdot a$
$E = \frac{1}{2} m v^2$
```

**Output:** Expression with computed numeric result appended.

### Symbolic Evaluation (`=>`)

```latex
$\frac{d}{dx}(x^2) =>$
$\text{solve}(x^2 - 5x + 6 = 0) =>$
```

**Output:** Symbolic result (derivative, solution, simplification).

### Unit Conversion

```latex
$v := 100\ \text{km/h}$
$v_{\text{m/s}} = v\ [\text{m/s}]$    <!-- Convert to m/s -->
$v_{\text{mph}} = v\ [\text{mph}]$    <!-- Convert to mph -->
```

### Highlighted Result

Use `=>` for important results you want to emphasize:

```latex
$\text{Total Cost} = price \cdot quantity =>$
```

**Output:** Result with visual emphasis (boxed, bold).

Note: `=>` serves dual purpose: symbolic operations AND highlighting important numeric results.

---

## Variable Names

### Simple Variables

```
x, y, z, a, b, c
mass, force, velocity
```

### Greek Letters

```latex
$\alpha$, $\beta$, $\gamma$, $\delta$
$\epsilon$, $\theta$, $\lambda$, $\mu$
$\pi$, $\sigma$, $\tau$, $\omega$
```

### Subscripts and Superscripts

```latex
$x_1$, $x_2$, $x_{max}$, $x_{min}$
$T_{ambient}$, $v_{initial}$, $F_{net}$
$x^2$ (in expressions, not as variable name)
```

### Text in Variables

```latex
$\text{mass}$, $\text{force}$
$m_{\text{total}}$
```

---

## Numbers

### Integers and Decimals

```
5, 42, 1000
3.14, 0.001, 2.5
```

### Scientific Notation

```latex
$1.5 \times 10^{-3}$
$6.022 \times 10^{23}$
```

Or simplified:
```
1.5e-3
6.022e23
```

### Fractions

```latex
$\frac{1}{2}$
$\frac{3}{4}$
$\frac{x + 1}{x - 1}$
```

---

## Units

### Basic Units

```latex
$5\ \text{kg}$
$10\ \text{m}$
$3\ \text{s}$
$100\ \text{N}$
```

### Compound Units

```latex
$9.81\ \text{m/s}^2$
$50\ \text{km/h}$
$1.2\ \text{kg/m}^3$
$100\ \text{kN·m}$
```

### SI Prefixes

| Prefix | Symbol | Factor |
|--------|--------|--------|
| pico | p | 10⁻¹² |
| nano | n | 10⁻⁹ |
| micro | µ | 10⁻⁶ |
| milli | m | 10⁻³ |
| centi | c | 10⁻² |
| kilo | k | 10³ |
| mega | M | 10⁶ |
| giga | G | 10⁹ |

### Custom Unit Definition

```latex
$1\ \text{lightyear} := 9.461 \times 10^{15}\ \text{m}$
$1\ \text{mph} := 1\ \text{mile/hour}$
```

---

## Operators

### Arithmetic

| Operator | LaTeX | Meaning |
|----------|-------|---------|
| `+` | `+` | Addition |
| `-` | `-` | Subtraction |
| `*` | `\cdot` or `\times` | Multiplication |
| `/` | `\frac{}{}` or `/` | Division |
| `^` | `^{}` | Exponentiation |

### Comparison (for conditionals)

| Operator | LaTeX | Meaning |
|----------|-------|---------|
| `<` | `<` | Less than |
| `>` | `>` | Greater than |
| `<=` | `\leq` | Less or equal |
| `>=` | `\geq` | Greater or equal |
| `==` | `=` | Equal (in conditions) |

---

## Functions

### Trigonometric

```latex
$\sin(x)$, $\cos(x)$, $\tan(x)$
$\arcsin(x)$, $\arccos(x)$, $\arctan(x)$
$\sinh(x)$, $\cosh(x)$, $\tanh(x)$
```

### Exponential and Logarithmic

```latex
$\exp(x)$, $e^x$
$\ln(x)$, $\log(x)$      <!-- natural log -->
$\log_{10}(x)$           <!-- base 10 -->
$\log_2(x)$              <!-- base 2 -->
```

### Roots and Powers

```latex
$\sqrt{x}$
$\sqrt[3]{x}$            <!-- cube root -->
$x^{1/n}$                <!-- nth root -->
$|x|$, $\text{abs}(x)$   <!-- absolute value -->
```

### Rounding

```latex
$\text{floor}(x)$
$\text{ceil}(x)$
$\text{round}(x)$
$\text{round}(x, n)$     <!-- n decimal places -->
```

### Aggregation

```latex
$\min(a, b, c)$
$\max(a, b, c)$
$\sum_{i=1}^{n} x_i$
$\prod_{i=1}^{n} x_i$
```

---

## Matrices and Vectors

### Vector Definition

```latex
$\vec{v} := [1, 2, 3]$
$\mathbf{v} := \begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix}$
```

### Matrix Definition

```latex
$A := [[1, 2]; [3, 4]]$

$A := \begin{bmatrix}
  1 & 2 \\
  3 & 4
\end{bmatrix}$
```

### Matrix Operations

```latex
$A^T$                    <!-- transpose -->
$A^{-1}$                 <!-- inverse -->
$\det(A)$                <!-- determinant -->
$A \cdot B$              <!-- multiplication -->
$\text{solve}(A, b)$     <!-- solve Ax = b -->
```

---

## Symbolic Operations

### Differentiation

```latex
$\frac{d}{dx}(x^2) =>$
$\text{diff}(x^3, x) =>$
```

### Integration

```latex
$\int x^2\, dx =>$
$\text{integrate}(x^2, x) =>$
```

### Equation Solving

```latex
$\text{solve}(x^2 - 5x + 6 = 0, x) =>$
```

### Simplification

```latex
$\text{simplify}(\sin^2(x) + \cos^2(x)) =>$
```

---

## Comments

### Line Comments

```latex
# This entire line is a comment
$x := 5$  # Inline comment after expression
```

### Block Comments

```latex
<!--
This is a multi-line
comment block
-->
```

---

## Document Directives

### Precision Control

```latex
<!-- livemathtex: digits=4 -->
$\pi =$  <!-- Shows 3.142 -->

<!-- livemathtex: digits=10 -->
$\pi =$  <!-- Shows 3.141592654 -->
```

### Scientific Notation

```latex
<!-- livemathtex: scientific=true -->
$1000000 =$  <!-- Shows 1.0 × 10⁶ -->
```

### Unit System

```latex
<!-- livemathtex: units=SI -->      <!-- Default -->
<!-- livemathtex: units=imperial -->
```

---

## Code Blocks

### Calculation Block

````markdown
```livemathtex
# Parameters
m := 5 kg
g := 9.81 m/s^2

# Calculation
F = m * g
```
````

### Plot Block

````markdown
```plot
title: "Sine Wave"
y = sin(x)
x = 0..2*pi
grid: true
```
````

### Configuration Block

````markdown
```livemathtex-config
digits: 4
scientific: false
units: SI
```
````

---

## Examples

### Basic Calculation

```latex
## Physics Problem

Given:
$m := 10\ \text{kg}$
$a := 2\ \text{m/s}^2$

Calculate force:
$F = m \cdot a$
```

**Output:**
```
F = m · a = 20 N
```

### With Unit Conversion

```latex
$v := 100\ \text{km/h}$
$t := 2\ \text{h}$
$d = v \cdot t\ [\text{m}]$
```

**Output:**
```
d = v · t = 200000 m
```

### Function and Graph

```latex
$f(x) := x^2 - 4x + 3$

The roots are at $\text{solve}(f(x) = 0) =>$

```plot
y = x^2 - 4x + 3
x = -1..5
```
```

---

## Error Messages

| Error | Cause | Example |
|-------|-------|---------|
| `Undefined variable` | Variable not defined | `$y = x$` without `$x := ...$` |
| `Unit mismatch` | Incompatible units | `$5\ \text{kg} + 3\ \text{m}$` |
| `Division by zero` | Divide by zero | `$1/0$` |
| `Invalid syntax` | Parse error | `$x := := 5$` |
| `Circular dependency` | Self-reference | `$x := x + 1$` |
| `Computation timeout` | Too complex | Very large matrix operations |

---

## Reserved Keywords

The following are reserved and cannot be used as variable names:

```
sin, cos, tan, asin, acos, atan
sinh, cosh, tanh
log, ln, exp, sqrt
abs, floor, ceil, round
min, max, sum, prod
diff, integrate, solve, simplify
det, inv, transpose
pi, e, i
true, false
```
