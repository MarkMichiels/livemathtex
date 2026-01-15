<!-- livemathtex: output=inplace, json=true, digits=4, smart_format=true -->

# Test: Smart Number Formatting (ISS-046)

Verifies context-aware number formatting with `smart_format=true`.

## Test Cases

### Case 1: Large numbers (>=1000) - integer format
$large_1 := 1234.5678\ \text{kg} == 1\,235\ \text{kg}$
$large_2 := 16103.07\ \text{kg} == 16\,103\ \text{kg}$
$large_3 := 186377.8\ \text{kg} == 186\,378\ \text{kg}$

**Expected:** 1235, 16103, 186378 (rounded to integers, thousands separator)

### Case 2: Medium-large numbers (100-999)
$med_lg_1 := 165.347\ \text{m} == 165.3\ \text{m}$
$med_lg_2 := 543.219\ \text{W} == 543\ \text{W}$

**Expected:** 165.3 or 165, 543 (0-1 decimal)

### Case 3: Medium numbers (10-99)
$med_1 := 24.1916\ \text{mm} == 24.2\ \text{mm}$
$med_2 := 54.0837 == 54.1$

**Expected:** 24.2, 54.1 (1 decimal)

### Case 4: Small numbers (1-9.99)
$small_1 := 3.9223 == 3.92$
$small_2 := 7.1456 == 7.15$

**Expected:** 3.92, 7.15 (2 decimals)

### Case 5: Very small numbers (<1)
$tiny_1 := 0.00753\ \text{mol/s} == 0.00753\ \text{mol/s}$
$tiny_2 := 0.1234 == 0.123$

**Expected:** 0.00753, 0.123 (2-3 sig figs)

### Case 6: Very large numbers (scientific)
$huge_1 := 1234567.89 == 1.23e+06$

**Expected:** 1.23e6 (scientific notation)

---

---

> *livemathtex: 2026-01-16 00:47:23 | 12 definitions, 12 evaluations | no errors | 0.07s* <!-- livemathtex-meta -->
