<!-- livemathtex: output=output.md, json=true -->

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
    Error: Undefined variable: z}}$

## ✅ Correct Usage

## Definitions (:=)

Define some variables (note: single letters like 'a', 'b' conflict with
Pint units like "year" and "barn", so we use subscripts):

$a_1 := 10$
$b_1 := 5$

## Evaluation (==)

Calculate sum and product:

$total := a_1 + b_1 == 15$

$product := a_1 \cdot b_1 == 50$

## Combined Definition + Evaluation

$ratio := \frac{a_1}{b_1} == 2$

## Re-evaluate existing variable

$total == 15$

## Summary

- **Pure display** (`$E = mc^2$`): Passes through, no processing
- **Definition** (`:=`): Assigns value to variable
- **Evaluation** (`==`): Computes and shows result
- **Error**: Bare `=` only errors when block has operators

---

> *livemathtex: 2026-01-15 11:30:38 | 7 definitions, 5 evaluations | 2 errors | 0.06s* <!-- livemathtex-meta -->
