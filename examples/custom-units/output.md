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

## Test 2: Kilowatt - SI Output vs Custom Unit

SymPy has `watt` and `kilo`, but not `kilowatt` or `kW`:

$$kW === kilo \cdot W$$

$$power := 5\ kW$$

$$hours := 8$$

**Default (SI base units):**

$$energy\_si := power \cdot hours == 4.000e+04\ \text{kg} \cdot \text{m}^{2}/\text{s}^{3}$$

**In custom unit (kW·h):** <!-- unit: kW·h -->

$$energy\_custom := power \cdot hours == 4.000e+04\ \text{kg} \cdot \text{m}^{2}/\text{s}^{3}$$ <!-- format: .0f, unit: kW·h -->

**Expected:**
- SI: 144000000 J (or scientific notation)
- Custom: 40 kW·h

---

## Test 3: Millibar - SI Output vs Custom Unit

SymPy has `bar` and `milli`, but not `millibar` or `mbar`:

$$mbar === milli \cdot bar$$

$$pressure\_atm := 1013\ mbar$$

$$factor := 2$$

**Default (SI = Pascal):**

$$pressure\_si := pressure\_atm \cdot factor == 2.026e+05\ \text{kg}/\text{(m} \cdot \text{s}^{2)}$$

**In custom unit (mbar):** <!-- unit: mbar -->

$$pressure\_mbar := pressure\_atm \cdot factor == 2.026e+05\ \text{kg}/\text{(m} \cdot \text{s}^{2)}$$ <!-- format: .0f, unit: mbar -->

**Expected:**
- SI: 202600 Pa (or 2.026e+05 kg/(m·s²))
- Custom: 2026 mbar

---

## Test 4: Kilowatt-hour - Unit Cancellation

The classic energy unit - must be defined:

$$kWh === kilo \cdot W \cdot hour$$

$$electricity\_price := 0.139\ €/kWh$$

$$consumption := 1500\ kWh$$

$$cost := electricity\_price \cdot consumption == 208.5\ \text{€}$$

**Expected:** 208.5 € (kWh cancels out perfectly!)

---

## Test 5: Currency per Unit (Derived)

Combining custom euro with built-in kg:

$$cost\_per\_kg := 25\ €/kg$$

$$weight := 4\ kg$$

$$total := cost\_per\_kg \cdot weight == 100.0\ \text{€}$$

**Expected:** 100 € (kg cancels out)

---

## Test 6: Number Formatting

Control decimal places and notation:

$$large\_number := 1234567$$

**Default:**

$$result\_default := large\_number == 1.235e+06$$

**With format .2e (scientific):** <!-- format: .2e -->

$$result\_sci := large\_number == 1.235e+06$$ <!-- format: .2e -->

**With format .0f (no decimals):** <!-- format: .0f -->

$$result\_int := large\_number == 1.235e+06$$ <!-- format: .0f -->

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

## Output Control (Planned Features)

| Feature | Syntax | Status |
|---------|--------|--------|
| SI output (default) | `== ` | ✅ Works |
| Unit cancellation | `€/kWh × kWh = €` | ✅ Works |
| Custom unit output | `== <!-- unit: mbar -->` | 🔜 Planned |
| Number format | `== <!-- format: .2f -->` | 🔜 Planned |
| Thousands separator | `== <!-- format: ,.0f -->` | 🔜 Planned |

---

> *livemathtex: 2026-01-07 01:26:36 | 21 definitions, 10 evaluations | no errors | 0.19s* <!-- livemathtex-meta -->
