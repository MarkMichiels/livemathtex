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

$$ € === € $$

$$ price := 100\ € $$

$$ discount := 0.20 $$

$$ final\_price := price \cdot (1 - discount) == $$

**Expected:** 80 €

---

## Test 2: Kilowatt - SI Output vs Custom Unit

SymPy has `watt` and `kilo`, but not `kilowatt` or `kW`:

$$ kW === kilo \cdot W $$

$$ power := 5\ kW $$

$$ time := 8\ h $$

**Default (SI base units):**

$$ energy\_si := power \cdot time == $$

**In custom unit (kW·h):**

$$ energy\_kWh := power \cdot time == $$ <!-- [kWh] -->

**In decimal format (no scientific notation):**

$$ energy\_decimal := power \cdot time == $$ <!-- format:decimal [kWh] -->

**Expected:**
- SI: 1.44e+08 kg·m²/s²
- Custom: 40 kWh
- Decimal: 40.0000 kWh

---

## Test 3: Millibar - SI Output vs Custom Unit

SymPy has `bar` and `milli`, but not `millibar` or `mbar`:

$$ mbar === milli \cdot bar $$

$$ pressure\_atm := 1013\ mbar $$

$$ factor := 2 $$

**Default (SI = Pascal):**

$$ pressure\_si := pressure\_atm \cdot factor == $$

**In custom unit (mbar):**

$$ pressure\_mbar := pressure\_atm \cdot factor == $$ <!-- digits:4 [mbar] -->

**Expected:**
- SI: 202600 Pa (or 2.026e+05 kg/(m·s²))
- Custom: 2026 mbar

---

## Test 4: Kilowatt-hour - Unit Cancellation

The classic energy unit - must be defined:

$$ kWh === kilo \cdot W \cdot hour $$

$$ electricity\_price := 0.139\ €/kWh $$

$$ consumption := 1500\ kWh $$

$$ cost := electricity\_price \cdot consumption == $$

**Expected:** 208.5 € (kWh cancels out perfectly!)

---

## Test 5: Currency per Unit (Derived)

Combining custom euro with built-in kg:

$$ cost\_per\_kg := 25\ €/kg $$

$$ weight := 4\ kg $$

$$ total := cost\_per\_kg \cdot weight == $$

**Expected:** 100 € (kg cancels out)

---

## Test 6: Number Formatting

Control decimal places and notation:

$$ large\_number := 1234567 $$

**Default:**

$$ result\_default := large\_number == $$

**With 2 significant digits:**

$$ result\_2dig := large\_number == $$ <!-- digits:2 -->

**With scientific notation:**

$$ result\_sci := large\_number == $$ <!-- format:sci -->

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
