# Simple Calculation Example

This example demonstrates the basic livemathtex operators.

## ❌ Common Mistakes (These Will Error)

### Bare `=` instead of `:=` or `==`

$x = 10
\\ \color{red}{\text{
    Error: Invalid operator '='. Use ':=' for definition or '==' for evaluation.}}$

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

With simple definitions and evaluations, we can build up calculations step by step.

---

> *livemathtex: 2026-01-04 21:05:19 | 6 definitions, 5 evaluations | 2 errors | 0.05s* <!-- livemathtex-meta -->
