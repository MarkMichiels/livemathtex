# Livemathtex - Examples

## Example 1: Basic Physics Calculation

### Input

```markdown
# Free Fall Calculation

## Given Parameters

$g := 9.81\ \text{m/s}^2$
$h := 100\ \text{m}$

## Calculations

Time to fall:
$t = \sqrt{\frac{2h}{g}} = ?$

Final velocity:
$v = g \cdot t = ?$

Kinetic energy (assuming $m := 1\ \text{kg}$):
$E_k = \frac{1}{2} m v^2 = ?$
```

### Output

```markdown
# Free Fall Calculation

## Given Parameters

$g := 9.81\ \text{m/s}^2$
$h := 100\ \text{m}$

## Calculations

Time to fall:
$t = \sqrt{\frac{2h}{g}} = 4.515\ \text{s}$

Final velocity:
$v = g \cdot t = 44.29\ \text{m/s}$

Kinetic energy (assuming $m := 1\ \text{kg}$):
$E_k = \frac{1}{2} m v^2 = 981\ \text{J}$
```

---

## Example 2: Engineering - Beam Design

### Input

```markdown
# Simply Supported Beam Analysis

## Material Properties

$E := 200\ \text{GPa}$           <!-- Young's modulus (steel) -->
$\sigma_{allow} := 250\ \text{MPa}$  <!-- Allowable stress -->

## Geometry

$L := 6\ \text{m}$               <!-- Span length -->
$b := 0.2\ \text{m}$             <!-- Width -->
$h := 0.4\ \text{m}$             <!-- Height -->

## Section Properties

$I = \frac{b \cdot h^3}{12} = ?$
$S = \frac{b \cdot h^2}{6} = ?$

## Loading

$w := 20\ \text{kN/m}$           <!-- Uniform distributed load -->

## Analysis

Maximum bending moment (at midspan):
$M_{max} = \frac{w \cdot L^2}{8} = ?$

Maximum stress:
$\sigma_{max} = \frac{M_{max}}{S} = ?$

Safety factor:
$SF = \frac{\sigma_{allow}}{\sigma_{max}} =>$

Maximum deflection:
$\delta_{max} = \frac{5 \cdot w \cdot L^4}{384 \cdot E \cdot I} = ?\ \text{mm}$

Deflection limit (L/360):
$\delta_{limit} = \frac{L}{360} = ?\ \text{mm}$
```

---

## Example 3: Electrical Engineering

### Input

```markdown
# RC Circuit Analysis

## Components

$R := 10\ \text{k}\Omega$
$C := 100\ \text{µF}$
$V_s := 12\ \text{V}$

## Time Constant

$\tau = R \cdot C = ?$

## Voltage at Time t

$t := 0.5\ \text{s}$

Charging:
$V_C = V_s \cdot (1 - e^{-t/\tau}) = ?$

Discharging (from fully charged):
$V_{discharge} = V_s \cdot e^{-t/\tau} = ?$

## Energy Stored

$E = \frac{1}{2} C V_s^2 = ?$
```

---

## Example 4: Chemistry - Solution Preparation

### Input

```markdown
# Solution Preparation

## Target Solution

$c_{target} := 0.1\ \text{mol/L}$
$V_{target} := 500\ \text{mL}$

## Stock Solution

$c_{stock} := 1\ \text{mol/L}$

## Calculation

Moles needed:
$n = c_{target} \cdot V_{target} = ?$

Volume of stock to use:
$V_{stock} = \frac{n}{c_{stock}} = ?\ \text{mL}$

Volume of solvent to add:
$V_{solvent} = V_{target} - V_{stock} = ?\ \text{mL}$

## Verification

Final concentration check:
$c_{final} = \frac{c_{stock} \cdot V_{stock}}{V_{target}} = ?$
```

---

## Example 5: Financial Calculation

### Input

```markdown
# Compound Interest

## Parameters

$P := 10000$                     <!-- Principal (€) -->
$r := 0.05$                      <!-- Annual interest rate (5%) -->
$n := 12$                        <!-- Compounding periods per year -->
$t := 10$                        <!-- Years -->

## Calculations

Future value:
$FV = P \cdot (1 + \frac{r}{n})^{n \cdot t} = ?$

Total interest earned:
$I = FV - P = ?$

Effective annual rate:
$r_{eff} = (1 + \frac{r}{n})^n - 1 = ?$
```

---

## Example 6: With Graph

### Input

````markdown
# Projectile Motion

## Parameters

$v_0 := 20\ \text{m/s}$          <!-- Initial velocity -->
$\theta := 45°$                  <!-- Launch angle -->
$g := 9.81\ \text{m/s}^2$

## Components

$v_{0x} = v_0 \cdot \cos(\theta) = ?$
$v_{0y} = v_0 \cdot \sin(\theta) = ?$

## Key Results

Time of flight:
$t_{flight} = \frac{2 v_{0y}}{g} = ?$

Maximum height:
$h_{max} = \frac{v_{0y}^2}{2g} = ?$

Range:
$R = v_{0x} \cdot t_{flight} =>$

## Trajectory

```plot
title: "Projectile Trajectory"
xlabel: "Distance (m)"
ylabel: "Height (m)"
y = v_{0y}/v_{0x} * x - g/(2*v_{0x}^2) * x^2
x = 0..R
```
````

---

## Example 7: Matrix Operations

### Input

```markdown
# System of Linear Equations

Solve: $3x + 2y = 7$ and $x - y = 1$

## Matrix Form

$A := [[3, 2]; [1, -1]]$
$b := [7, 1]$

## Solution

$x = A^{-1} \cdot b = ?$

## Verification

$A \cdot x = ?$  <!-- Should equal b -->

## Additional Properties

$\det(A) = ?$
$A^T = ?$
```

---

## Example 8: Symbolic Math

### Input

```markdown
# Calculus Examples

## Differentiation

$f(x) := x^3 - 3x^2 + 2x$

$f'(x) = \frac{d}{dx} f(x) = ?$
$f''(x) = \frac{d^2}{dx^2} f(x) = ?$

## Critical Points

$\text{solve}(f'(x) = 0, x) = ?$

## Integration

$F(x) = \int f(x)\, dx = ?$

Definite integral from 0 to 2:
$\int_0^2 f(x)\, dx = ?$

## Taylor Series

$\sin(x) \approx x - \frac{x^3}{6} + \frac{x^5}{120}$

At $x := 0.5$:
$\sin(0.5) = ?$
$\text{taylor\_approx} = 0.5 - \frac{0.5^3}{6} + \frac{0.5^5}{120} = ?$
```

---

## Example 9: Error Handling

### Input (with intentional errors)

```markdown
# Error Examples

## Undefined Variable
$y = x + 1 = ?$              <!-- x not defined -->

## Unit Mismatch
$m := 5\ \text{kg}$
$L := 10\ \text{m}$
$wrong = m + L = ?$          <!-- Can't add mass and length -->

## Division by Zero
$result = \frac{1}{0} = ?$

## Working Calculation
$a := 5$
$b := 3$
$c = a + b = ?$              <!-- This works -->
```

### Output

```markdown
# Error Examples

## Undefined Variable
$y = x + 1 = \textcolor{red}{\text{⚠️ Error: Undefined variable 'x'}}$

## Unit Mismatch
$m := 5\ \text{kg}$
$L := 10\ \text{m}$
$wrong = m + L = \textcolor{red}{\text{⚠️ Error: Cannot add kg + m}}$

## Division by Zero
$result = \frac{1}{0} = \textcolor{red}{\text{⚠️ Error: Division by zero}}$

## Working Calculation
$a := 5$
$b := 3$
$c = a + b = 8$
```

---

## Example 10: Complete Document Template

### Input

````markdown
# [Project Name] - Technical Calculation

**Author:** [Name]  
**Date:** [Date]  
**Revision:** 1.0

---

## 1. Introduction

Brief description of the calculation purpose.

## 2. Input Parameters

| Parameter | Symbol | Value | Unit | Source |
|-----------|--------|-------|------|--------|
| Load | $P$ | 100 | kN | Specification |
| Length | $L$ | 5 | m | Drawing |
| Factor | $\gamma$ | 1.5 | - | Code |

$P := 100\ \text{kN}$
$L := 5\ \text{m}$
$\gamma := 1.5$

## 3. Calculations

### 3.1 Step One

Description of calculation step.

$M = P \cdot L = ?$

### 3.2 Step Two

Description of next step.

$M_{design} = M \cdot \gamma =>$

## 4. Results Summary

| Result | Value | Unit | Status |
|--------|-------|------|--------|
| Moment | $M =$ | kN·m | ✅ |
| Design Moment | $M_{design} =$ | kN·m | ✅ |

## 5. Conclusion

Summary of findings and recommendations.

---

## Appendix A: References

- [1] Design Code ABC-123
- [2] Material Specification XYZ

## Appendix B: Revision History

| Rev | Date | Author | Changes |
|-----|------|--------|---------|
| 1.0 | 2026-01-04 | [Name] | Initial issue |
````

---

## Running the Examples

```bash
# Process single example
livemathtex examples/physics.md -o output/physics.md

# Watch mode for development
livemathtex examples/physics.md -o output/physics.pdf --watch

# All examples
for f in examples/*.md; do
    livemathtex "$f" -o "output/$(basename "$f")"
done
```

