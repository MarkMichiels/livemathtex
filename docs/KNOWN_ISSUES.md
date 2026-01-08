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

*Last updated: 2026-01-08*
