<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test: Array Operations (ISS-041)

Tests array definition, indexing, and vectorized operations.

## Basic Array Definition

$values := [1, 2, 3, 4, 5]$
$rate := [15, 30.5, 34]\ \text{mg/L/d}$

## Element Access

$first_value := values[0] == 1$
$rate_1 := rate[1] == 30.5\ \text{mg/d/L}$ <!-- [mg/d/L] -->

## Vectorized Operations

$V_L := 37824\ L$
$mass := V_L \cdot rate == [567.36, 1\,153.632, 1\,286.016]\ \text{g/d}$ <!-- [g/d] -->

## Scalar Operations on Arrays

$doubled := values * 2 == [2, 4, 6, 8, 10]$ <!-- [2, 4, 6, 8, 10] -->
$sum_arr := [10, 20] + [5, 3] == [15, 23]$ <!-- [15, 23] -->

---

---

> *livemathtex: 2026-01-16 00:59:02 | 8 definitions, 5 evaluations | no errors | 0.07s* <!-- livemathtex-meta -->
