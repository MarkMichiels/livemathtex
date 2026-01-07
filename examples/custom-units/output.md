<!-- livemathtex: output=output.md, json=true -->

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

$$final\_price := price \cdot (1 - discount) == 80\ \text{€}$$

**Expected:** 80 €

---

## Test 2: Kilowatt - SI Output vs Custom Unit

SymPy has `watt` and `kilo`, but not `kilowatt` or `kW`:

$$kW === kilo \cdot W$$

$$power := 5\ kW$$

$$time := 8\ h$$

**Default (SI base units):**

$$energy\_si := power \cdot time == 144\,000\,000\ \text{kg} \cdot \text{m}^{2}/\text{s}^{2}$$
$$energy\_si := power \cdot time == 1.440e+08\ \text{kg} \cdot \text{m}^{2}/\text{s}^{2}$$ <!-- format:scientific -->

**In custom unit (kW·h):**

$$energy\_kWh := power \cdot time == 40\ \text{kW*h}$$ <!-- [kW*h] -->
$$energy\_kWh := power \cdot time == 40\ \text{kWh}$$ <!-- [kWh] -->

**In decimal format (no scientific notation):**

$$energy\_decimal := power \cdot time == 40\ \text{kWh}$$ <!-- [kWh] format:decimal -->

**Expected:**
- SI: 1.44e+08 kg·m²/s²
- Custom: 40 kWh
- Decimal: 40.0000 kWh

---

## Test 3: Millibar - SI Output vs Custom Unit

SymPy has `bar` and `milli`, but not `millibar` or `mbar`:

$$mbar === milli \cdot bar$$

$$pressure\_atm := 1013\ mbar$$

$$factor := 2$$

**Default (SI = Pascal):**

$$pressure\_si := pressure\_atm \cdot factor == 202\,600\ \text{kg}/\text{(m} \cdot \text{s}^{2)}$$

**In custom unit (mbar):**

$$pressure\_mbar := pressure\_atm \cdot factor == 2026\ \text{mbar}$$ <!-- [mbar] digits:4 -->

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

$$total := cost\_per\_kg \cdot weight == 100\ \text{€}$$

**Expected:** 100 € (kg cancels out)

---

## Test 6: Formatting Playground

Explore all formatting possibilities!

### Base values for testing

$$big := 144000000$$
$$medium := 12345.6789$$
$$small := 0.000012345$$
$$integer := 40$$
$$pi\_val := 3.14159265359$$

---

### Format Types

**`format:general`** (default) - Automatic, strips trailing zeros:

$$fmt\_general := big == 144\,000\,000$$

$$fmt\_general\_med := medium == 12\,350$$

**`format:decimal`** - Force decimal notation:

$$fmt\_decimal := big == 144\,000\,000$$ <!-- format:decimal -->

**`format:scientific`** or `format:sci` - Scientific notation (1.23e+05):

$$fmt\_sci := big == 1.440e+08$$ <!-- format:scientific -->

$$fmt\_sci\_small := small == 1.234e-05$$ <!-- format:sci -->

**`format:engineering`** or `format:eng` - Powers of 3 (kilo, mega, etc.):

$$fmt\_eng := big == 144.0e6$$ <!-- format:engineering -->

$$fmt\_eng\_small := small == 12.35e-6$$ <!-- format:eng -->

---

### Significant Digits

**`digits:N`** - Control precision:

$$dig\_default := pi\_val == 3.142$$

$$dig\_2 := pi\_val == 3.1$$ <!-- digits:2 -->

$$dig\_4 := pi\_val == 3.142$$ <!-- digits:4 -->

$$dig\_8 := pi\_val == 3.1415927$$ <!-- digits:8 -->

**Digits + Format combined:**

$$dig\_sci\_3 := big == 1.44e+08$$ <!-- digits:3 format:sci -->

$$dig\_eng\_4 := big == 144.0e6$$ <!-- digits:4 format:eng -->

---

### Thousands Separators

Large numbers automatically get thin space separators (≥5 digits):

$$thou\_1 := 1234 == 1234$$ <!-- format:decimal -->

$$thou\_2 := 12345 == 12\,345$$ <!-- format:decimal -->

$$thou\_3 := 1234567 == 1\,234\,567$$ <!-- format:decimal -->

$$thou\_4 := 123456789 == 123\,456\,789$$ <!-- format:decimal -->

$$thou\_5 := 1234567890 == 1\,234\,567\,890$$ <!-- format:decimal -->

---

### Trailing Zeros

By default, trailing zeros are stripped:

$$trail\_1 := 40.0000 == 40$$

$$trail\_2 := 3.14000 == 3.14$$

$$trail\_3 := integer == 40$$

---

### Combined: Units + Formatting

Electricity example with different views:

$$combo\_power := 5\ kW$$
$$combo\_hours := 8\ h$$

$$combo\_energy := combo\_power \cdot combo\_hours == 144\,000\,000\ \text{kg} \cdot \text{m}^{2}/\text{s}^{2}$$

$$combo\_kwh := combo\_power \cdot combo\_hours == 40\ \text{kWh}$$ <!-- [kWh] -->

$$combo\_sci := combo\_power \cdot combo\_hours == 1.440e+08\ \text{kg} \cdot \text{m}^{2}/\text{s}^{2}$$ <!-- format:sci -->

$$combo\_full := combo\_power \cdot combo\_hours == 40\ \text{kWh}$$ <!-- [kWh] digits:2 -->

---

### Edge Cases

**Zero:**

$$zero := 0 == 0$$

**Negative numbers:**

$$neg := -12345678 == -12\,345\,678$$ <!-- format:decimal -->

**Very small (auto → scientific):**

$$tiny := 0.000000001 == 1.000e-09$$

**Very small (forced scientific):**

$$tiny\_sci := 0.000000001 == 1.000e-09$$ <!-- format:sci -->

**Very large (auto → scientific at 10⁹+):**

$$huge := 1000000000000000 == 1.000e+15$$

**Very large (engineering):**

$$huge\_eng := 1000000000000000 == 1.000e15$$ <!-- format:eng -->

**Very large (forced decimal):**

$$huge\_dec := 1000000000000000 == 1\,000\,000\,000\,000\,000$$ <!-- format:decimal -->

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

## Output Control Syntax

```markdown
# SI output (default) - no comment needed
$x ==$

# Custom unit - wrap in [brackets]
$x ==$ <!-- [mbar] -->

# Digits control
$x ==$ <!-- digits:2 -->

# Format control (sci, eng, decimal)
$x ==$ <!-- format:sci -->

# Combined: digits + unit
$x ==$ <!-- digits:4 [mbar] -->
```

---

> *livemathtex: 2026-01-07 03:13:50 | 59 definitions, 42 evaluations | no errors | 0.41s* <!-- livemathtex-meta -->
