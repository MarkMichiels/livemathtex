# Unit Library - Common Industrial Units

This example defines a comprehensive unit library for industrial and algae cultivation applications.
Copy this section to the top of your document to enable all units.

---

## Currency Units

$$ € === € $$

$$ dollar === dollar $$

$$ cent === € / 100 $$

---

## Volume Units

Standard volume units (SI + common):

$$ mL === mL $$

$$ m³ === m^3 $$

---

## Concentration Units

For algae cultivation:

$$ mg/L === mg / L $$

$$ g/L === g / L $$

---

## Flow Rate Units

$$ L/h === L / h $$

$$ m³/h === m^3 / h $$

$$ m³/dag === m^3 / day $$

---

## Energy Units

$$ kWh === kW \cdot h $$

$$ MWh === MW \cdot h $$

---

## Pressure Units

$$ mbar === bar / 1000 $$

$$ kPa === Pa \cdot 1000 $$

---

## Dutch Time Aliases

$$ dag === day $$

$$ uur === hour $$

$$ minuut === minute $$

---

## Example Calculations

### Energy Cost (Electricity)

$$ prijs_{elektriciteit} := 0.139\ €/kWh $$

$$ verbruik := 24000\ kWh $$

$$ kosten := prijs_{elektriciteit} \cdot verbruik == $$

### Biomass Production

$$ productie := 5\ g/L $$

$$ volume_{reactor} := 100\ L $$

$$ totaal := productie \cdot volume_{reactor} == $$

### Working Hours

$$ uren_{dag} := 8 $$

$$ dagen_{week} := 5 $$

$$ weken_{jaar} := 48 $$

$$ totaal_{uren} := uren_{dag} \cdot dagen_{week} \cdot weken_{jaar} == $$

---

## Usage in Your Documents

To use these units in your LiveMathTeX documents, copy the unit definitions
(the `===` sections) to the top of your document before any calculations.

In future versions, an import mechanism will allow:

```latex
<!-- livemathtex: import=unit-library -->
```
