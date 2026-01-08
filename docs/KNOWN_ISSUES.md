[LiveMathTeX](../README.md) / Known Issues & Backlog

# Known Issues & Backlog

This document tracks known limitations and planned improvements for LiveMathTeX.

---

## Critical Issues

*(None currently)*

---

## Medium Priority

*(None currently)*

---

## Low Priority / Nice-to-Have

*(None currently)*

---

## Resolved Issues

### ISSUE-002: Remove all hardcoded unit lists - use Pint as single source of truth

**Status:** RESOLVED
**Priority:** High
**Discovered:** 2026-01-08
**Resolved:** 2026-01-08

**Problem:**
The codebase contained **4 separate hardcoded unit lists** across 2 files, totaling ~230 unit definitions:
- `evaluator.py`: `RESERVED_UNIT_NAMES` (~50), `unit_map` (~20), `unit_mapping` (~40)
- `pint_backend.py`: `UNIT_ABBREVIATIONS` (~50)

**Key Discovery:** Pint already recognizes almost everything natively (MWh, kWh, m³/h, µm, etc.). Only currency (€, $) needs custom definition.

**Solution Implemented:**

All 4 hardcoded lists removed and replaced with dynamic Pint queries:
- `is_pint_unit()` - Check if token is Pint-recognized
- `is_custom_unit()` - Check if token is user-defined
- `pint_to_sympy_with_prefix()` - Dynamic Pint → SymPy conversion

**Result:**
- **Before:** ~230 hardcoded unit definitions
- **After:** 0 hardcoded definitions; Pint is single source of truth
- **Tests:** 102 passing (76 existing + 26 new in `tests/test_unit_recognition.py`)

**Files Changed:**
- `evaluator.py` - Removed all hardcoded unit lists
- `pint_backend.py` - Removed `UNIT_ABBREVIATIONS`, added dynamic functions
- `examples/unit-library/` - Updated as canonical custom unit reference

---

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

*Last updated: 2026-01-08 (ISSUE-002 resolved)*
