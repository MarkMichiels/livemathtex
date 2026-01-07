# Custom Unit Definitions - LiveMathTeX Example

This example tests the `===` syntax for defining **truly custom** units - units that SymPy doesn't recognize by default.

---

## Built-in vs Custom Units

**Built-in** (no definition needed): `kg`, `m`, `s`, `W`, `bar`, `L`, `mL`, `Pa`, `hour`

**NOT built-in** (need `===` definition):
- Prefix combinations: `kW`, `mbar`, `kWh`, `MW`
- Currency: `€`, `dollar`
- Custom abbreviations: `dag` (Dutch for day)

---

## Test 1: Currency (Completely Custom)

Currency doesn't exist in SymPy - must be defined:

$$€ === €$$

$$price := 100\ €$$

$$discount := 0.20$$

$$final\_price := price \cdot (1 - discount) == 80.00\ \text{€}$$

**Expected:** 80 €

---

## Test 2: Kilowatt (Prefix Combination)

SymPy has `watt` and `kilo`, but not `kilowatt` or `kW`:

$$kW === kilo \cdot W$$

$$power := 5\ kW$$

$$hours := 8$$

$$energy := power \cdot hours == 4.000e+04\ \text{kg} \cdot \text{m}^{2}/\text{s}^{3}$$

**Expected:** 40 kW·h (or converted to base units)

---

## Test 3: Millibar (Prefix Combination)

SymPy has `bar` and `milli`, but not `millibar` or `mbar`:

$$mbar === milli \cdot bar$$

$$pressure\_atm := 1013\ mbar$$

$$factor := 2$$

$$pressure\_double := pressure\_atm \cdot factor == 2.026e+05\ \text{kg}/\text{(m} \cdot \text{s}^{2)}$$

**Expected:** 2026 mbar

---

## Test 4: Kilowatt-hour (Compound Unit)

The classic energy unit - must be defined:

$$kWh === kilo \cdot W \cdot hour$$

$$electricity\_price := 0.139\ €/kWh$$

$$consumption := 1500\ kWh$$

$$cost := electricity\_price \cdot consumption == 208.5\ \text{€}$$

**Expected:** 208.5 € (kWh cancels out)

---

## Test 5: Currency per Unit (Derived)

Combining custom euro with built-in kg:

$$cost\_per\_kg := 25\ €/kg$$

$$weight := 4\ kg$$

$$total := cost\_per\_kg \cdot weight == 100.0\ \text{€}$$

**Expected:** 100 € (kg cancels out)

---

## Summary: What Needs `===` Definition?

| Unit | Built-in? | Definition Needed |
|------|-----------|-------------------|
| `kg`, `m`, `s`, `W` | ✅ Yes | No |
| `bar`, `Pa`, `L` | ✅ Yes | No |
| `hour`, `day` | ✅ Yes | No |
| `kW`, `MW`, `GW` | ❌ No | `kW === kilo \cdot W` |
| `mbar`, `kPa` | ❌ No | `mbar === milli \cdot bar` |
| `kWh`, `MWh` | ❌ No | `kWh === kilo \cdot W \cdot hour` |
| `€`, `$` | ❌ No | `€ === €` |

---

> *livemathtex: 2026-01-07 01:23:24 | 15 definitions, 5 evaluations | no errors | 0.15s* <!-- livemathtex-meta -->
