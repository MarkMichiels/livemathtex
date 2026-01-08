[LiveMathTeX](../README.md) / Known Issues & Backlog

# Known Issues & Backlog

This document tracks known limitations and planned improvements for LiveMathTeX.

---

## Critical Issues

### ISSUE-002: Remove all hardcoded unit lists - use Pint as single source of truth

**Status:** OPEN
**Priority:** High
**Discovered:** 2026-01-08

**Problem:**
The codebase contains **4 separate hardcoded unit lists** across 2 files, totaling ~230 unit definitions. This creates:

1. **Maintenance burden** - Same units defined in multiple places
2. **Inconsistency** - Some units in one list but not another
3. **Incompleteness** - New units require manual addition to multiple files
4. **Architectural debt** - Contradicts "Pint as single source of truth" goal

**Discovery:**
Testing revealed that **Pint already recognizes almost everything**:

```python
import pint
ureg = pint.UnitRegistry()

# Pint recognizes ALL of these natively:
ureg('MWh')    # ✅ megawatt_hour
ureg('kWh/kg') # ✅ kilowatt_hour / kilogram
ureg('m³/h')   # ✅ meter ** 3 / hour
ureg('µm')     # ✅ micrometer
ureg('°C')     # ✅ degree_Celsius

# Only these need custom definition:
ureg('EUR')    # ❌ Not recognized (currency)
ureg('€')      # ❌ Not recognized (currency)
```

**Hardcoded Lists Location:**

| File | List | Lines | Purpose |
|------|------|-------|---------|
| `evaluator.py` | `RESERVED_UNIT_NAMES` | 68-72 | Prevent variable/unit name conflicts |
| `evaluator.py` | `unit_map` | 1352-1361 | Parse units in `value:` directive |
| `evaluator.py` | `unit_mapping` | 1932-1974 | Substitute units in formula evaluation |
| `pint_backend.py` | `UNIT_ABBREVIATIONS` | 1127-1260 | SymPy unit compatibility layer |

**Root Cause:**
ISSUE-001 was "fixed" by adding MORE hardcoded units instead of removing them. The architecture should be:

```
User Input → Pint (single source) → SymPy (generated dynamically)
```

Instead we have:

```
User Input → Hardcoded List 1? → Hardcoded List 2? → Pint? → Hardcoded List 3?
```

---

**Solution Plan:**

#### Phase 1: Create `is_pint_unit()` function

Replace all hardcoded checks with a single Pint query:

```python
def is_pint_unit(token: str) -> bool:
    """Check if token is a valid Pint unit."""
    try:
        _pint_ureg.parse_expression(token)
        return True
    except:
        return False
```

#### Phase 2: Replace `RESERVED_UNIT_NAMES`

**Current:** Hardcoded set of ~50 unit names
**New:** Dynamic check via `is_pint_unit(name)` or `is_custom_unit(name)`

```python
# OLD
if symbol_name in RESERVED_UNIT_NAMES:
    raise Error("conflicts with unit")

# NEW
if is_pint_unit(symbol_name) or is_custom_unit(symbol_name):
    raise Error("conflicts with unit")
```

#### Phase 3: Replace `unit_map` (value: directive)

**Current:** Hardcoded dict for unit parsing
**New:** Use Pint directly for parsing

```python
# OLD
unit_map = {'m': u.meter, 'kg': u.kilogram, ...}
if unit_str in unit_map:
    return unit_map[unit_str]

# NEW
def get_sympy_unit(unit_str: str):
    """Convert Pint unit to SymPy unit dynamically."""
    pint_unit = _pint_ureg.parse_expression(unit_str)
    return _pint_to_sympy(pint_unit)
```

#### Phase 4: Replace `unit_mapping` (formula evaluation)

**Current:** Hardcoded substitution dict
**New:** Dynamic lookup via Pint + custom registry

#### Phase 5: Replace `UNIT_ABBREVIATIONS` (SymPy compatibility)

**Current:** 150+ hardcoded SymPy unit mappings
**New:** Dynamic creation from Pint:

```python
def _pint_to_sympy(pint_unit) -> sympy.Expr:
    """Convert Pint unit to SymPy expression dynamically."""
    # Use Pint's dimensionality to construct SymPy unit
    dims = pint_unit.dimensionality
    # Map dimensions to SymPy base units
    # e.g., {'[length]': 1, '[time]': -1} → meter/second
```

#### Phase 6: Update unit-library example

Update `examples/unit-library/input.md` to serve as the **canonical reference** for custom units:

- Currency: `€ === €`, `dollar === dollar`
- Aliases: `dag === day` (Dutch)
- Compound convenience: `SEC === kWh/kg` (specific energy consumption)

#### Phase 7: Add unit library import (future)

**See:**
- [USAGE.md - Import System](USAGE.md#import-system-planned) for full documentation
- [ROADMAP.md - Phase 2.3](ROADMAP.md) for implementation timeline

Enables loading unit libraries via relative paths:

```markdown
<!-- livemathtex: import=./units/currency.md -->
```

**Current workaround:** Copy unit definitions to top of each document (see `examples/unit-library/input.md`).

---

**Files to Modify:**

| File | Action |
|------|--------|
| `pint_backend.py` | Add `is_pint_unit()`, `get_sympy_unit()`, remove `UNIT_ABBREVIATIONS` |
| `evaluator.py` | Remove `RESERVED_UNIT_NAMES`, `unit_map`, `unit_mapping`; use new functions |
| `examples/unit-library/` | Expand as canonical custom unit reference |

**Testing Strategy:**

1. Run all existing tests after each phase
2. Add specific tests for:
   - All Pint-recognized units work without custom definition
   - Custom units (`===`) still work
   - Variable names that look like units are handled correctly
   - Edge cases: `m` (meter vs variable), `s` (second vs variable)

**Expected Outcome:**

- **Before:** ~230 hardcoded unit definitions across 4 lists
- **After:** 0 hardcoded unit definitions; Pint is single source of truth

---

## Medium Priority

*(None currently)*

---

## Low Priority / Nice-to-Have

*(None currently)*

---

## Resolved Issues

### ISSUE-001: `value:` directive doesn't support complex/custom units

**Status:** RESOLVED
**Priority:** High
**Discovered:** 2026-01-08
**Resolved:** 2026-01-08

**Problem:**
The `value:` directive for displaying variable values in tables only supported simple units from a hardcoded `unit_map`. Custom units (EUR, €), energy units (MWh, kWh), and compound units (MWh/kg) did not work.

**Solution implemented:**
1. **Pint-based unit conversion** - `_get_numeric_in_unit_latex()` now uses Pint via `convert_value_to_unit()` for unit conversion
2. **Custom unit registration** - Unit definitions (`===`) are registered in both Pint and SymPy registries
3. **Complete unit support** - All Pint-recognized units now work in value directives, including:
   - Energy: MWh, kWh, GWh
   - Currency: EUR (€), USD ($)
   - Compound: MWh/kg, €/kWh
4. **Removed `units.py`** - All unit handling consolidated in `pint_backend.py`

**Test coverage:**
- Added ISSUE-001 test section in `examples/custom-units/input.md`
- Tests MWh conversion (5000 kWh → 5 MWh)
- Tests EUR value display
- All 76 tests passing

**Files changed:**
- `src/livemathtex/engine/evaluator.py` - Use Pint for value: directive conversions
- `src/livemathtex/engine/pint_backend.py` - Added `convert_value_to_unit()`, SymPy compatibility layer
- `src/livemathtex/engine/units.py` - REMOVED (all code migrated to pint_backend.py)
- `examples/custom-units/input.md` - Added ISSUE-001 test cases

---

## Contributing

When adding new issues:
1. Use format: `ISSUE-XXX: Brief title`
2. Include: Status, Priority, Discovered date, Context
3. Describe: Problem, What works/doesn't, Root cause, Impact
4. Propose: Solution options with short/medium/long term
5. List: Affected files and workarounds

---

*Last updated: 2026-01-08 (ISSUE-002 added)*
