# Unit Library - Common Industrial Units

This example defines a comprehensive unit library for industrial and algae cultivation applications.
Copy this section to the top of your document to enable all units.

---

## Currency Units

$$€ === €$$

$$dollar === dollar$$

$$cent === € / 100$$

---

## Volume Units

Standard volume units (SI + common):

$$mL === mL$$

$$m³ === m^3$$

---

## Concentration Units

For algae cultivation:

$$mg/L === mg / L$$

$$g/L === g / L$$

---

## Flow Rate Units

$$L/h === L / h$$

$$m³/h === m^3 / h$$

$$m³/day === m^3 / day$$

---

## Energy Units

$$kWh === kW \cdot h$$

$$MWh === MW \cdot h$$

---

## Pressure Units

$$mbar === bar / 1000$$

$$kPa === Pa \cdot 1000$$

---

## Example Calculations

### Energy Cost (Electricity)

$$electricity\_price := 0.139\ €/kWh$$

$$consumption := 24000\ kWh$$

$$cost := electricity\_price \cdot consumption == 3.336e+03\ \text{€}$$

### Biomass Production

$$productivity := 5\ g/L$$

$$reactor\_volume := 100\ L$$

$$total := productivity \cdot reactor\_volume == 0.5000\ \text{kg}$$

### Working Hours

$$hours\_per\_day := 8$$

$$days\_per\_week := 5$$

$$weeks\_per\_year := 48$$

$$total\_hours := hours\_per\_day \cdot days\_per\_week \cdot weeks\_per\_year == 1.920e+03$$

---

## Usage in Your Documents

To use these units in your LiveMathTeX documents, copy the unit definitions
(the `===` sections) to the top of your document before any calculations.

In future versions, an import mechanism will allow:

```latex
<!-- livemathtex: import=unit-library -->
```

---

> *livemathtex: 2026-01-07 01:17:08 | 10 definitions, 3 evaluations | no errors | 0.09s* <!-- livemathtex-meta -->
