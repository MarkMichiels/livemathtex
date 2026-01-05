# Simple Calculation Example

This example demonstrates the basic livemathtex operators.

## Display-Only Formulas

Pure LaTeX without operators passes through unchanged (no error):

$E = mc^2$

$F = ma$

## ❌ Common Mistakes (These Will Error)

### Bare `=` in a calculation block

When a block contains operators, bare `=` triggers an error:

$$x := 5
y = x + 3
\\ \color{red}{\text{
    Error: Invalid operator '='. Use ':=' for definition or '==' for evaluation.}}$$

### Undefined variable

$result := z + 5 ==
\\ \color{red}{\text{
    Error: Undefined variable(s): z}}$

## ✅ Correct Usage

## Definitions (:=)

Define some variables:

$a := 10$
$b := 5$

## Evaluation (==)

Calculate sum and product:

$total := a + b == 15$

$product := a \cdot b == 50$

## Combined Definition + Evaluation

$ratio := \frac{a}{b} == 2$

## Re-evaluate existing variable

$\text{total} == 15$

## Summary

- **Pure display** (`$E = mc^2$`): Passes through, no processing
- **Definition** (`:=`): Assigns value to variable
- **Evaluation** (`==`): Computes and shows result
- **Error**: Bare `=` only errors when block has operators

---

> *livemathtex: 2026-01-05 03:36:26 | 7 definitions, 5 evaluations | 2 errors | 0.05s* <!-- livemathtex-meta -->
