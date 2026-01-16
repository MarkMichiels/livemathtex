<!-- livemathtex: output=output.md, json=true, digits=4 -->

# Cross-References - LiveMathTeX Example

This example demonstrates **cross-references** (`{{variable}}`), which allow you to insert calculated values directly into your text, creating dynamic documentation that updates automatically.

---

## 1. Basic Cross-References

First, define some variables:

$len := 10\ m$

$wid := 5\ m$

$area := len \cdot wid == 50\ \text{m^2}$

Now reference them in text using `{{variable}}` syntax:

The room has dimensions 10.00 m<!-- {{len}} --> × 5.00 m<!-- {{wid}} -->, giving a total area of 50.00 m²<!-- {{area}} -->.

---

## 2. Cross-References with Unit Conversion

Cross-references support unit conversion using `{{variable [unit]}}`:

$flow := 1000\ \text{L/h}$

$pressure := 250000\ Pa$

The flow rate is 1.00 m³/h<!-- {{flow [m³/h]}} --> (or 16.67 L/min<!-- {{flow [L/min]}} --> in L/min).

The pressure is 2.50 bar<!-- {{pressure [bar]}} --> bar (or 250.00 kiloPa<!-- {{pressure [kPa]}} --> kPa).

---

## 3. Real-World Example: Engineering Report

### Pump Specifications

$Q_p := 50\ \text{m}^3/\text{h}$

$head := 25\ m$

$P_{motor} := 5.5\ kW$

$\eta := 0.78$

### Report Text with Cross-References

The selected pump operates at a flow rate of 34.72 m³/s<!-- {{Q_p}} --> with a head of 25.00 m<!-- {{head}} -->. The motor is rated for 5 500 W<!-- {{P_motor}} -->, achieving an efficiency of 0.7800<!-- {{η}} -->.

At the design point, the pump delivers 2 083 333 L/min<!-- {{Q_p [L/min]}} --> liters per minute.

---

## 4. Cross-References in Tables

Cross-references work in Markdown tables:

### Calculated Values

$density := 1000\ \text{kg/m}^3$

$vol := 2.5\ \text{m}^3$

$mass := density \cdot vol == 1.56e+10\ \text{kg^3}$

$grav := 9.81\ \text{m/s}^2$

$weight := mass \cdot grav == 1.50e+12\ \text{kg^3·m^2/s^2}$

### Summary Table

| Parameter | Value | Unit |
|-----------|-------|------|
| Density | 1 000 000 000 kg³/m³<!-- {{density}} --> | kg/m³ |
| Volume | 15.62 m³<!-- {{vol}} --> | m³ |
| Mass | 15 625 000 000 kg³<!-- {{mass}} --> | kg |
| Weight | {{ERROR: Cannot convert to kN: Cannot convert from 'kilogram ** 3 * meter ** 2 / second ** 2' ([mass] ** 3 * [length] ** 2 / [time] ** 2) to 'kilonewton' ([mass] * [length] / [time] ** 2)}} | kN |

---

## 5. Cross-References with Calculations

You can reference the result of any calculation:

### Input Parameters

$P_{in} := 100\ W$

$P_{out} := 85\ W$

### Efficiency Calculation

$\eta_{sys} := P_{out} / P_{in} == 0.85$

### Report

The system converts 100.00 W<!-- {{P_in}} --> of input power to 85.00 W<!-- {{P_out}} --> of useful output, achieving an efficiency of 0.8500<!-- {{η_sys}} -->.

---

## 6. Dynamic Cost Calculations

### Production Data

$$€ === €$$

$production := 500\ kg$

$unit\_cost := 25\ €/kg$

$total\_cost := production \cdot unit\_cost == 12\,500\ \text{€}$

$selling\_price := 45\ €/kg$

$revenue := production \cdot selling\_price == 22\,500\ \text{€}$

$profit := revenue - total\_cost == 10\,000\ \text{€}$

### Financial Summary

With a production volume of 500.00 kg<!-- {{production}} -->, total manufacturing cost is 12 500 EUR<!-- {{total_cost}} -->. At a selling price of 45.00 EUR/kg<!-- {{selling_price}} -->, total revenue is 22 500 EUR<!-- {{revenue}} -->, yielding a profit of 10 000 EUR<!-- {{profit}} -->.

---

## 7. Cross-References Across Sections

Variables defined anywhere in the document can be referenced later:

### Design Section

$design\_flow := 100\ L/min$

$design\_pressure := 5\ bar$

### Testing Section (references earlier values)

Testing confirmed the system meets design specifications:
- Flow: 0.0017 m³/s<!-- {{design_flow}} --> ✓
- Pressure: 500 000 kg/m/s²<!-- {{design_pressure}} --> ✓

---

## 8. Formatting Cross-References

Cross-references follow the document's formatting settings:

<!-- livemathtex: smart_format=true -->

$bignum := 1234567.89$

$smallnum := 0.00123$

With smart formatting enabled:
- Large: 1 234 568<!-- {{bignum}} -->
- Small: 0.0012<!-- {{smallnum}} -->

---

## Best Practices

### ✅ Do

- Use cross-references for values that appear multiple times
- Add unit conversion `{{var [unit]}}` for readability
- Update calculations and text updates automatically

### ❌ Don't

- Reference variables before they're defined
- Use cross-references for complex expressions (define a variable first)
- Forget that changes to calculations update all references

---

## Summary

| Feature | Syntax | Example |
|---------|--------|---------|
| Basic reference | `{{var}}` | The length is 10.00 m<!-- {{len}} -->. |
| With unit | `{{var [unit]}}` | Flow is 0.0003 m³/s<!-- {{flow}} --> (use unit hint). |
| In tables | Same syntax | Area = 50.00 m²<!-- {{area}} --> |

**Key insight:** Cross-references create living documents where changing a calculation automatically updates every place that value is used!

---

> *livemathtex: 2026-01-16 02:13:04 | 27 definitions, 7 evaluations | no errors | 0.10s* <!-- livemathtex-meta -->
