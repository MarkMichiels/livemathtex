# Custom Unit Definitions - LiveMathTeX Example

This example tests the `===` syntax for defining custom units.

---

## Test 1: Base Unit (Currency) ✅

Define euro as a new base unit:

$$ € === € $$

Use the euro unit:

$$ prijs := 100\ € $$

$$ korting := 0.20 $$

$$ eindprijs := prijs \cdot (1 - korting) == $$

**Expected:** 80 €

---

## Test 2: Currency per Unit ✅

Using the euro we defined:

$$ prijs_{per\_kg} := 50\ €/kg $$

$$ gewicht := 3\ kg $$

$$ totaal := prijs_{per\_kg} \cdot gewicht == $$

**Expected:** 150 € (kg cancels out)

---

## Test 3: Electricity Cost ✅

The classic example:

$$ prijs_{kWh} := 0.139\ €/kWh $$

$$ verbruik := 1500\ kWh $$

$$ kosten := prijs_{kWh} \cdot verbruik == $$

**Expected:** 208.5 € (kWh cancels out)

---

## Test 4: Built-in Units (No Definition Needed)

These units work out of the box:

$$ massa := 5\ kg $$

$$ snelheid := 10\ m/s $$

$$ impuls := massa \cdot snelheid == $$

**Expected:** 50 kg·m/s

---

## Test 5: Area Calculation

$$ lengte := 4\ m $$

$$ breedte := 3\ m $$

$$ oppervlakte := lengte \cdot breedte == $$

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
- Alias definitions (`dag === day`) need more testing
- Derived units (`mbar === bar/1000`) need more testing
