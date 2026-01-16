<!-- livemathtex: output=output.md, json=true -->

# Smart Formatting - LiveMathTeX Example

This example demonstrates **smart formatting** (`smart_format=true`), which automatically adjusts number precision based on magnitude for cleaner, more readable output.

---

## The Problem: Fixed Precision

With default formatting (`digits=4`), all numbers get the same precision regardless of context:

$large := 123456 ==$

$medium := 42.5 ==$

$small := 0.00123 ==$

This can produce results that are either too precise (showing decimals on large numbers) or not precise enough (rounding small numbers too aggressively).

---

## The Solution: Smart Formatting

Enable smart formatting to get context-aware precision:

<!-- livemathtex: smart_format=true -->

### Large Numbers (≥1000): Rounded to Integer

$big\_1 := 12345.67 ==$

$big\_2 := 1234567.89 ==$

$big\_3 := 99999.5 ==$

### Medium-Large (100-999): 0-1 Decimal Places

$med\_large\_1 := 500.123 ==$

$med\_large\_2 := 123.456 ==$

$med\_large\_3 := 999.999 ==$

### Medium (10-99): 1 Decimal Place

$med\_1 := 42.567 ==$

$med\_2 := 99.123 ==$

$med\_3 := 10.789 ==$

### Small (1-9.99): 2 Decimal Places

$small\_1 := 5.6789 ==$

$small\_2 := 1.2345 ==$

$small\_3 := 9.9999 ==$

### Very Small (<1): 2-3 Significant Figures

$tiny\_1 := 0.12345 ==$

$tiny\_2 := 0.012345 ==$

$tiny\_3 := 0.00012345 ==$

### Very Large (≥10⁶): Scientific Notation

$huge\_1 := 1234567890 ==$

$huge\_2 := 9876543210000 ==$

---

## Comparison: Default vs Smart

Let's compare the same values with both formatting modes:

### Test Values

$test\_big := 12345.6789$

$test\_med := 42.5678$

$test\_small := 0.001234$

### Default Formatting (digits=4)

<!-- livemathtex: smart_format=false -->

$default\_big := test\_big ==$

$default\_med := test\_med ==$

$default\_small := test\_small ==$

### Smart Formatting

<!-- livemathtex: smart_format=true -->

$smart\_big := test\_big ==$

$smart\_med := test\_med ==$

$smart\_small := test\_small ==$

---

## Real-World Example: Engineering Report

Smart formatting produces cleaner engineering reports:

<!-- livemathtex: smart_format=true -->

### Pump Sizing Calculation

$Q_1 := 50\ \text{m}^3/\text{h}$

$head := 25\ m$

$\rho := 1000\ \text{kg/m}^3$

$grav := 9.81\ \text{m/s}^2$

$\eta := 0.75$

**Hydraulic power:**

$P_{hyd} := \rho \cdot grav \cdot Q_1 \cdot head ==$ <!-- [kW] -->

**Motor power (with efficiency):**

$P_{motor} := P_{hyd} / \eta ==$ <!-- [kW] -->

### Production Analysis

$prod_{daily} := 567.36\ \text{g/d}$

$num_{days} := 365\ d$

$prod_{annual} := prod_{daily} \cdot num_{days} ==$ <!-- [kg] -->

### Cost Calculation

$$ € === € $$

$energy\_cost := 0.139\ €/kWh$

$runtime := 8760\ h$

$power := 4.54\ kW$

$annual\_cost := energy\_cost \cdot runtime \cdot power ==$

---

## When to Use Smart Formatting

### ✅ Recommended For

- **Engineering reports** - Cleaner numbers in documentation
- **Business calculations** - Appropriate precision for costs/quantities
- **Summary tables** - Consistent, readable values

### ❌ Not Recommended For

- **Scientific data** - When exact precision is required
- **Intermediate calculations** - Rounding may accumulate errors
- **Small differences** - When detecting tiny changes matters

---

## Enabling Smart Formatting

### Document-wide (at top of file)

```markdown
<!-- livemathtex: smart_format=true -->
```

### Per-section (can toggle on/off)

```markdown
<!-- livemathtex: smart_format=true -->
... smart formatted section ...

<!-- livemathtex: smart_format=false -->
... default formatting section ...
```

---

## Summary

| Magnitude | Smart Format Output | Example |
|-----------|---------------------|---------|
| ≥10⁶ | Scientific notation | 1.23e+09 |
| ≥1000 | Integer | 12,346 |
| 100-999 | 0-1 decimals | 500.1 |
| 10-99 | 1 decimal | 42.6 |
| 1-9.99 | 2 decimals | 5.68 |
| <1 | 2-3 sig figs | 0.0123 |

**Key insight:** Smart formatting produces human-friendly numbers that are appropriately precise for their magnitude.
