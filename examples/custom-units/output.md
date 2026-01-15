<!-- livemathtex: output=output.md, json=true -->

# Custom Unit Definitions - LiveMathTeX Example

This example tests the `===` syntax for defining **truly custom** units - units that SymPy doesn't recognize by default.

---

## Built-in vs Custom Units

**Built-in** (no definition needed): `kg`, `m`, `s`, `W`, `bar`, `L`, `mL`, `Pa`, `hour`

**Also built-in** (via Pint): `kW`, `MW`, `mbar`, `kWh`, `MWh`, `EUR`, `dag`

**NOT built-in** (need `===` definition):
- Currency symbols: `€` (but EUR is built-in)
- Application-specific units: e.g., `STUKS`, `SEC` (specific energy consumption)

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

Pint knows `kW` (no definition needed):

$$power := 5\ kW$$

$$time := 8\ h$$

**Default (SI base units):**

$$energy\_si := power \cdot time == 40\ \text{h · kW}$$
$$energy\_si := power \cdot time == 40\ \text{h · kW}$$ <!-- format:scientific -->

**In custom unit (kW·h):**

$$energy\_kWh := power \cdot time == 40\ \text{h · kW}$$ <!-- [kW*h] -->
$$energy\_kWh := power \cdot time == 40\ \text{kWh}$$ <!-- [kWh] -->

**In decimal format (no scientific notation):**

$$energy\_decimal := power \cdot time == 40\ \text{kWh}$$ <!-- [kWh] format:decimal -->

**Expected:**
- SI: 1.44e+08 kg·m²/s²
- Custom: 40 kWh
- Decimal: 40.0000 kWh

---

## Test 3: Millibar - SI Output vs Custom Unit

Pint knows `mbar` (no definition needed):

$$pressure\_atm := 1013\ mbar$$

$$factor := 2$$

**Default (SI = Pascal):**

$$pressure\_si := pressure\_atm \cdot factor == 2\,026\ \text{mbar}$$

**In custom unit (mbar):**

$$pressure\_mbar := pressure\_atm \cdot factor == 2\,026\ \text{mbar}$$ <!-- [mbar] digits:4 -->

**Expected:**
- SI: 202600 Pa (or 2.026e+05 kg/(m·s²))
- Custom: 2026 mbar

---

## Test 4: Kilowatt-hour - Unit Cancellation

Pint knows `kWh` (no definition needed):

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

$$fmt\_general\_med := medium == 12\,345.6789$$

**`format:decimal`** - Force decimal notation:

$$fmt\_decimal := big == 144\,000\,000$$ <!-- format:decimal -->

**`format:scientific`** or `format:sci` - Scientific notation (1.23e+05):

$$fmt\_sci := big == 144\,000\,000$$ <!-- format:scientific -->

$$fmt\_sci\_small := small == 1.2345e-05$$ <!-- format:sci -->

**`format:engineering`** or `format:eng` - Powers of 3 (kilo, mega, etc.):

$$fmt\_eng := big == 144\,000\,000$$ <!-- format:engineering -->

$$fmt\_eng\_small := small == 1.2345e-05$$ <!-- format:eng -->

---

### Significant Digits

**`digits:N`** - Control precision:

$$dig\_default := pi\_val == 3.1416$$

$$dig\_2 := pi\_val == 3.14$$ <!-- digits:2 -->

$$dig\_4 := pi\_val == 3.1416$$ <!-- digits:4 -->

$$dig\_8 := pi\_val == 3.14159265$$ <!-- digits:8 -->

**Digits + Format combined:**

$$dig\_sci\_3 := big == 144\,000\,000$$ <!-- digits:3 format:sci -->

$$dig\_eng\_4 := big == 144\,000\,000$$ <!-- digits:4 format:eng -->

---

### Thousands Separators

Large numbers automatically get thin space separators (≥5 digits):

$$thou\_1 := 1234 == 1\,234$$ <!-- format:decimal -->

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

$$combo\_energy := combo\_power \cdot combo\_hours == 40\ \text{h · kW}$$

$$combo\_kwh := combo\_power \cdot combo\_hours == 40\ \text{kWh}$$ <!-- [kWh] -->

$$combo\_sci := combo\_power \cdot combo\_hours == 40\ \text{h · kW}$$ <!-- format:sci -->

$$combo\_full := combo\_power \cdot combo\_hours == 40\ \text{kWh}$$ <!-- [kWh] digits:2 -->

---

### Edge Cases

**Zero:**

$$zero := 0 == 0$$

**Negative numbers:**

$$neg := -12345678 == -12\,345\,678$$ <!-- format:decimal -->

**Very small (auto → scientific):**

$$tiny := 0.000000001 == 1.0000e-09$$

**Very small (forced scientific):**

$$tiny\_sci := 0.000000001 == 1.0000e-09$$ <!-- format:sci -->

**Very large (auto → scientific at 10⁹+):**

$$huge := 1000000000000000 == 1\,000\,000\,000\,000\,000$$

**Very large (engineering):**

$$huge\_eng := 1000000000000000 == 1\,000\,000\,000\,000\,000$$ <!-- format:eng -->

**Very large (forced decimal):**

$$huge\_dec := 1000000000000000 == 1\,000\,000\,000\,000\,000$$ <!-- format:decimal -->

---

## Summary: What Needs `===` Definition?

| Unit | Built-in? | Definition Needed |
|------|-----------|-------------------|
| `kg`, `m`, `s`, `W` | ✅ Yes | No |
| `bar`, `Pa`, `L` | ✅ Yes | No |
| `hour`, `day` | ✅ Yes | No |
| `kW`, `MW`, `GW` | ✅ Yes (Pint) | No |
| `mbar`, `kPa` | ✅ Yes (Pint) | No |
| `kWh`, `MWh` | ✅ Yes (Pint) | No |
| `EUR` | ✅ Yes (Pint) | No |
| `€` (symbol) | ❌ No | `€ === €` |
| Custom units | ❌ No | `STUKS === STUKS` |

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

## ISSUE-001 Test: value: Directive with Custom Units

This section specifically tests the `value:` directive with custom units (MWh, EUR, etc.).
This was broken before ISSUE-001 was fixed.

### Test Data

Note: MWh is built-in via Pint (no definition needed).

$$E := 5000\ kWh$$

$$cost\_eur := 750\ €$$

$$SEC := 0.5\ kWh$$

### value: Directive Tests (ISSUE-001)

These should display the correct converted values:

| Parameter | Value |
|-----------|-------|
| Energy (kWh) | $5000$ <!-- value:E [kWh] --> |
| Energy (MWh) | $5$ <!-- value:E [MWh] --> |
| Cost (€) | $750$ <!-- value:cost_eur [€] --> |
| SEC (kWh) | $0.5$ <!-- value:SEC [kWh] --> |

**Expected Results:**
- Energy (kWh): 5000
- Energy (MWh): 5
- Cost (€): 750
- SEC (kWh): 0.5

---

> *livemathtex: 2026-01-15 11:21:15 | 62 definitions, 42 evaluations, 4 value refs | no errors | 0.11s* <!-- livemathtex-meta -->
