# Custom Unit Definitions - LiveMathTeX Example

This example tests the `===` syntax for defining custom units.

---

## Test 1: Base Unit (Currency)

Define euro as a new base unit:

$$€ === €$$

Use the euro unit:

$$price := 100\ €$$

$$discount := 0.20$$

$$final\_price := price \cdot (1 - discount) == 80.00\ \text{€}$$

**Expected:** 80 €

---

## Test 2: Currency per Unit

Using the euro we defined:

$$price\_per\_kg := 50\ €/kg$$

$$weight := 3\ kg$$

$$total := price\_per\_kg \cdot weight == 150.0\ \text{€}$$

**Expected:** 150 € (kg cancels out)

---

## Test 3: Electricity Cost

The classic example:

$$price\_kWh := 0.139\ €/kWh$$

$$consumption := 1500\ kWh$$

$$cost := price\_kWh \cdot consumption == 208.5\ \text{€}$$

**Expected:** 208.5 € (kWh cancels out)

---

## Test 4: Built-in Units (No Definition Needed)

These units work out of the box:

$$mass := 5\ kg$$

$$velocity := 10\ m/s$$

$$momentum := mass \cdot velocity == 50.00\ \text{kg} \cdot \text{m}/\text{s}$$

**Expected:** 50 kg·m/s

---

## Test 5: Area Calculation

$$length := 4\ m$$

$$width := 3\ m$$

$$area := length \cdot width == 12.00\ \text{m}^{2}$$

**Expected:** 12 m²

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Base unit `€ === €` | ✅ Works | Currency fully supported |
| Unit propagation | ✅ Works | €/kWh × kWh = € |
| Built-in SI units | ✅ Works | kg, m, s, W, etc. |
| Compound expressions | ✅ Works | €/kg, m/s, kWh |

### Known Limitations

- Units are converted to SI base units in output
- Alias definitions (`day_alias === day`) need more testing
- Derived units (`mbar === bar/1000`) need more testing

---

> *livemathtex: 2026-01-07 01:21:21 | 15 definitions, 5 evaluations | no errors | 0.15s* <!-- livemathtex-meta -->
