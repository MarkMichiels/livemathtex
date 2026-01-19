# Unit Library - Custom Units for Industrial Applications

This example shows which units need custom definition with `===` syntax.

**Key insight (ISSUE-002):** Pint recognizes almost ALL standard units natively:

*   SI units: m, kg, s, A, K, mol, cd
*   Derived: N, J, W, Pa, Hz, V, ohm
*   Prefixed: kW, MW, mm, km, kWh, MWh, mg, mL
*   Compound: m/s, kWh/kg, m³/h, mg/L

**Only define what Pint doesn't know:**

*   Currency: €, $, EUR, USD
*   Industry-specific: SEC (specific energy consumption), etc.

---

## Custom Units Required

### Currency Units (NOT in Pint)

$$ € === € $$

$$ dollar === dollar $$

$$ cent === € / 100 $$

---

## Units Pint Already Knows (NO definition needed)

The following work automatically - do NOT define them:

*   Volume: L, mL, m³, m^3
*   Flow: L/h, m³/h, m³/day
*   Energy: kWh, MWh, Wh
*   Pressure: Pa, kPa, bar, mbar
*   Concentration: mg/L, g/L (compound units work)

---

## Example Calculations

### Energy Cost (Uses € custom unit + Pint's kWh)

$$ electricity\_price := 0.139\\ €/kWh $$

$$ consumption := 24000\\ kWh $$

$$ cost := electricity\_price \\cdot consumption == $$

### Biomass Production (All Pint units)

$$ productivity := 5\\ g/L $$

$$ reactor\_volume := 100\\ L $$

$$ total := productivity \\cdot reactor\_volume == $$

### Working Hours (Pure numbers)

$$ hours\_per\_day := 8 $$

$$ days\_per\_week := 5 $$

$$ weeks\_per\_year := 48 $$

$$ total\_hours := hours\_per\_day \\cdot days\_per\_week \\cdot weeks\_per\_year == $$

---

## Summary: What Needs Definition?

| Unit Type | Examples | Needs `===` Definition? |
| --- | --- | --- |
| SI base | m, kg, s, A, K | **No** - Pint knows these |
| SI derived | N, J, W, Pa, Hz | **No** - Pint knows these |
| Prefixed | kW, MW, mm, kWh | **No** - Pint knows these |
| Compound | m/s, kWh/kg | **No** - Pint parses these |
| Currency | €, $, EUR | **Yes** - not in Pint |
| Industry-specific | SEC, custom rates | **Yes** - define with `===` |

---

## Future: Import Mechanism

When the import system is implemented (see ROADMAP.md):

```
<!-- livemathtex: import=./units/currency.md -->
```

This will allow sharing unit libraries across documents.