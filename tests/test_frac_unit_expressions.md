<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test: \frac in Unit Expressions (ISS-044)

Verifies that `\frac` can be used in unit expressions for variable definitions.

## Test Cases

### Case 1: Simple fraction unit
**Definition:** Value with unit fraction `\frac{mg}{L}`

$conc_1 := 15\ \frac{\text{mg}}{\text{L}} == 15\ \text{mg/L}$ <!-- [mg/L] -->

**Expected:** 15 mg/L = 0.015 g/L

### Case 2: Compound fraction unit with multiplication
**Definition:** Value with compound unit `\frac{mg}{L \cdot d}`

$rate_1 := 15\ \frac{\text{mg}}{\text{L} \cdot \text{d}} == 15\ \text{mg/d/L}$ <!-- [mg/d/L] -->

**Expected:** 15 mg/(L·d) - a rate per volume per day

### Case 3: Reference to validate value
**Evaluation:** Using the defined rate in a calculation

$Vol := 1000\ \text{L}$
$daily_{mass} := rate_1 \cdot Vol == 15\ \text{g/d}$ <!-- [g/d] -->

**Expected:** 15 mg/(L·d) × 1000 L = 15 g/d

### Case 4: More complex unit fractions
**Definition:** Power production rate

$power_{rate} := 100\ \frac{\text{kW}}{\text{m}^{3}} == 100\ \text{kW/m^3}$ <!-- [kW/m^3] -->

**Expected:** 100 kW/m³

---

---

> *livemathtex: 2026-01-16 00:39:22 | 5 definitions, 4 evaluations | no errors | 0.07s* <!-- livemathtex-meta -->
