# Custom Unit Definitions - LiveMathTeX Example

This example demonstrates the `===` syntax for defining custom units.

## Unit Definition Syntax

### Base Units (New Units)

Define completely new units (like currencies):

$$€ === €$$

$$dollar === dollar$$

### Derived Units (From Existing)

Define units as fractions or multiples of existing units:

$$mbar === bar / 1000$$

### Compound Units

Define units as products of other units:

$$kWh === kW \cdot h$$

### Aliases (Dutch → English)

Create aliases for built-in units:

$$dag === day$$

$$uur === hour$$

---

## Using Custom Units in Calculations

Now we can use these units in our calculations:

### Electricity Cost Calculation

$$prijs_{kWh} := 0.139$$

$$energie := 1500$$

$$kosten := prijs_{kWh} \cdot energie == 208.5$$

### Pressure Conversion

$$P_{bar} := 2.5$$

$$P_{mbar} := P_{bar} \cdot 1000 == 2.500e+03$$

### Time Calculation

$$uren_{dag} := 8$$

$$dagen := 22$$

$$totaal_{uren} := uren_{dag} \cdot dagen == 176.0$$

---

## Built-in Unit Abbreviations

LiveMathTeX recognizes these abbreviations:

| Category | Abbreviations |
|----------|---------------|
| Mass | `kg`, `g`, `mg` |
| Length | `m`, `cm`, `mm`, `km` |
| Time | `s`, `h`, `min`, `dag` (→ day) |
| Volume | `L`, `mL` |
| Power | `W`, `kW`, `MW` |
| Pressure | `Pa`, `kPa`, `bar`, `mbar` |
| Temperature | `K` |

---

## Summary

The `===` operator allows you to:

1. **Create new base units** for domain-specific quantities (currency, custom metrics)
2. **Define derived units** from existing SI units
3. **Create compound units** for complex dimensions
4. **Alias units** for localization (Dutch: dag → day)

This keeps your documents readable while enabling accurate unit-aware calculations.

---

> *livemathtex: 2026-01-07 00:46:43 | 8 definitions, 3 evaluations | no errors | 0.09s* <!-- livemathtex-meta -->
