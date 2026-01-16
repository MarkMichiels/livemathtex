<!-- livemathtex: output=output.md, json=true, digits=4 -->

# Array Operations - LiveMathTeX Example

This example demonstrates **array operations** for performing repetitive calculations efficiently. Instead of writing the same formula multiple times for different inputs, define an array and let LiveMathTeX compute all results at once.

---

## 1. Basic Array Definition

Arrays are defined using square brackets with comma-separated values:

$values := [1, 2, 3, 4, 5]$

$temperatures := [20, 25, 30, 35, 40]$

$prices := [10.5, 15.0, 22.75, 8.25]$

---

## 2. Arrays with Units

Units can be attached to entire arrays - the unit applies to all elements:

$rates := [15, 30.5, 34]\ \text{mg/L/d}$

$volumes := [100, 250, 500, 1000]\ L$

$powers := [1.5, 2.0, 3.5, 5.0]\ kW$

---

## 3. Element Access (Zero-Based Indexing)

Access individual elements using `array[index]`. **Indexing starts at 0:**

$values := [10, 20, 30, 40, 50]$

$first := values[0] ==$

$second := values[1] ==$

$third := values[2] ==$

$last := values[4] ==$

---

## 4. Element Access with Units

Units are preserved when accessing array elements:

$rates := [15, 30.5, 34]\ \text{mg/L/d}$

$rate\_low := rates[0] ==$ <!-- [mg/L/d] -->

$rate\_mid := rates[1] ==$ <!-- [mg/L/d] -->

$rate\_high := rates[2] ==$ <!-- [mg/L/d] -->

---

## 5. Vectorized Operations (Broadcasting)

### 5.1 Scalar × Array

Multiply all array elements by a single value:

$base := [10, 20, 30, 40, 50]$

$doubled := base * 2 ==$

$halved := base / 2 ==$

$offset := base + 5 ==$

### 5.2 Variable × Array (with units)

A scalar variable multiplied by an array produces an array result:

$V_L := 37824\ L$

$rates := [15, 30.5, 34]\ \text{mg/L/d}$

$daily\_mass := V_L \cdot rates ==$ <!-- [g/d] -->

### 5.3 Array × Array (Element-wise)

Arrays of the **same length** can be combined element-wise:

$arr_1 := [10, 20, 30]$

$arr_2 := [1, 2, 3]$

$sum := arr_1 + arr_2 ==$

$diff := arr_1 - arr_2 ==$

$product := arr_1 * arr_2 ==$

$ratio := arr_1 / arr_2 ==$

---

## 6. Real-World Example: Production Analysis

Calculate daily and annual production for different productivity rates:

### Input Data

$productivity := [15, 30.5, 34]\ \text{mg/L/d}$

$reactor\_volume := 37824\ L$

$days\_per\_year := 365\ d$

### Daily Production

$daily\_prod := reactor\_volume \cdot productivity ==$ <!-- [g/d] -->

### Annual Production

$annual\_prod := daily\_prod \cdot days\_per\_year ==$ <!-- [kg] -->

### Summary Table

| Scenario | Productivity | Daily | Annual |
|----------|--------------|-------|--------|
| Low | $ $ <!-- value:productivity[0] [mg/L/d] --> | $ $ <!-- value:daily_prod[0] [g/d] --> | $ $ <!-- value:annual_prod[0] [kg] --> |
| Medium | $ $ <!-- value:productivity[1] [mg/L/d] --> | $ $ <!-- value:daily_prod[1] [g/d] --> | $ $ <!-- value:annual_prod[1] [kg] --> |
| High | $ $ <!-- value:productivity[2] [mg/L/d] --> | $ $ <!-- value:daily_prod[2] [g/d] --> | $ $ <!-- value:annual_prod[2] [kg] --> |

---

## 7. Cost Analysis with Arrays

### Define Costs

$$ € === € $$

$unit\_costs := [25, 35, 45]\ €/kg$

$quantities := [100, 150, 200]\ kg$

### Calculate Total Costs

$total\_costs := unit\_costs \cdot quantities ==$ <!-- [€] -->

### Element-wise Profit Calculation

$selling\_prices := [50, 60, 70]\ €/kg$

$revenues := selling\_prices \cdot quantities ==$ <!-- [€] -->

$profits := revenues - total\_costs ==$

---

## 8. Best Practices

### ✅ Do

- Use arrays for repetitive calculations with the same formula
- Give arrays descriptive names (`productivity_rates` not `arr`)
- Use unit hints `<!-- [unit] -->` for consistent output
- Remember: indexing is **zero-based** (first element is `[0]`)

### ❌ Don't

- Mix arrays of different lengths in element-wise operations
- Use arrays for single values (just use a scalar)
- Forget that `array[0]` is the first element, not `array[1]`

---

## Summary

| Feature | Syntax | Example |
|---------|--------|---------|
| Define array | `[a, b, c]` | `v := [1, 2, 3]` |
| Array with units | `[...] unit` | `r := [10, 20] kg` |
| Element access | `arr[i]` | `first := v[0]` |
| Scalar × array | `scalar * arr` | `doubled := v * 2` |
| Array × array | `arr1 * arr2` | `prod := arr_1 * arr_2` |

**Key insight:** Arrays eliminate repetitive calculations - define once, compute all scenarios at once!
