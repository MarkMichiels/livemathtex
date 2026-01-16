<!-- livemathtex: output=output.md, json=true, digits=4 -->

# Cross-References - LiveMathTeX Example

This example demonstrates **cross-references** (`{{variable}}`), which allow you to insert calculated values directly into your text, creating dynamic documentation that updates automatically.

---

## 1. Basic Cross-References

First, define some variables:

$len := 10\ m$

$wid := 5\ m$

$area := len \cdot wid ==$

Now reference them in text using `{{variable}}` syntax:

The room has dimensions {{len}} × {{wid}}, giving a total area of {{area}}.

---

## 2. Cross-References with Unit Conversion

Cross-references support unit conversion using `{{variable [unit]}}`:

$flow := 1000\ \text{L/h}$

$pressure := 250000\ Pa$

The flow rate is {{flow [m³/h]}} (or {{flow [L/min]}} in L/min).

The pressure is {{pressure [bar]}} bar (or {{pressure [kPa]}} kPa).

---

## 3. Real-World Example: Engineering Report

### Pump Specifications

$Q_p := 50\ \text{m}^3/\text{h}$

$head := 25\ m$

$P_{motor} := 5.5\ kW$

$\eta := 0.78$

### Report Text with Cross-References

The selected pump operates at a flow rate of {{Q_p}} with a head of {{head}}. The motor is rated for {{P_motor}}, achieving an efficiency of {{η}}.

At the design point, the pump delivers {{Q_p [L/min]}} liters per minute.

---

## 4. Cross-References in Tables

Cross-references work in Markdown tables:

### Calculated Values

$density := 1000\ \text{kg/m}^3$

$vol := 2.5\ \text{m}^3$

$mass := density \cdot vol ==$

$grav := 9.81\ \text{m/s}^2$

$weight := mass \cdot grav ==$

### Summary Table

| Parameter | Value | Unit |
|-----------|-------|------|
| Density | {{density}} | kg/m³ |
| Volume | {{vol}} | m³ |
| Mass | {{mass}} | kg |
| Weight | {{weight [kN]}} | kN |

---

## 5. Cross-References with Calculations

You can reference the result of any calculation:

### Input Parameters

$P_{in} := 100\ W$

$P_{out} := 85\ W$

### Efficiency Calculation

$\eta_{sys} := P_{out} / P_{in} ==$

### Report

The system converts {{P_in}} of input power to {{P_out}} of useful output, achieving an efficiency of {{η_sys}}.

---

## 6. Dynamic Cost Calculations

### Production Data

$$ € === € $$

$production := 500\ kg$

$unit\_cost := 25\ €/kg$

$total\_cost := production \cdot unit\_cost ==$

$selling\_price := 45\ €/kg$

$revenue := production \cdot selling\_price ==$

$profit := revenue - total\_cost ==$

### Financial Summary

With a production volume of {{production}}, total manufacturing cost is {{total_cost}}. At a selling price of {{selling_price}}, total revenue is {{revenue}}, yielding a profit of {{profit}}.

---

## 7. Cross-References Across Sections

Variables defined anywhere in the document can be referenced later:

### Design Section

$design\_flow := 100\ L/min$

$design\_pressure := 5\ bar$

### Testing Section (references earlier values)

Testing confirmed the system meets design specifications:
- Flow: {{design_flow}} ✓
- Pressure: {{design_pressure}} ✓

---

## 8. Formatting Cross-References

Cross-references follow the document's formatting settings:

<!-- livemathtex: smart_format=true -->

$bignum := 1234567.89$

$smallnum := 0.00123$

With smart formatting enabled:
- Large: {{bignum}}
- Small: {{smallnum}}

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
| Basic reference | `{{var}}` | The length is {{len}}. |
| With unit | `{{var [unit]}}` | Flow is {{flow}} (use unit hint). |
| In tables | Same syntax | Area = {{area}} |

**Key insight:** Cross-references create living documents where changing a calculation automatically updates every place that value is used!
