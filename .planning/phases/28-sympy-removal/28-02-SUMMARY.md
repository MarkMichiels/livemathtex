# Phase 28-02 Summary: Remove SymPy from pint_backend.py

## Completed: 2026-01-15

## Objective
Remove all SymPy dependencies from pint_backend.py. This file previously contained 148 sympy references, primarily for the SymPy AST evaluation path that is no longer needed since the custom parser was introduced.

## Changes Made

### 1. Removed SymPy-dependent functions (Task 1)
- `evaluate_sympy_ast_with_pint()` - SymPy AST walker for evaluation
- `build_pint_symbol_map()` - Builds symbol map from SymPy expressions
- `_sympy_unit_to_pint()` - Converts SymPy unit names to Pint
- `pint_to_sympy()` and `pint_to_sympy_with_prefix()` - SymPy unit conversion
- `get_sympy_unit_dimensionality()` - Extracts dimensions from SymPy Quantity
- `_sympy_*` parsing functions - SymPy unit parsing helpers
- Original `sympy_strip_unit_from_value()` implementation

### 2. Removed all SymPy imports (Task 2)
- Removed `from sympy.physics.units import ...` import block
- Zero SymPy imports remain in pint_backend.py
- Verified: `grep -c "import sympy\|from sympy" pint_backend.py` returns 0

### 3. Refactored CustomUnitRegistry (Task 3)
- Renamed `SymPyUnitRegistry` to `CustomUnitRegistry`
- Renamed `UnitDefinition` to `CustomUnitDefinition`
- Removed `sympy_unit` field from unit definitions
- Registry now only tracks custom unit names (for `is_custom_unit()`)
- Actual unit operations handled entirely by Pint

### 4. Added backwards compatibility aliases
- `get_sympy_unit_registry = get_custom_unit_registry`
- `reset_sympy_unit_registry = reset_custom_unit_registry`
- `UnitRegistry = CustomUnitRegistry`
- `sympy_strip_unit_from_value()` now delegates to `strip_unit_from_value()`

### 5. Updated exports in __init__.py
- Changed `get_sympy_unit_registry` to `get_custom_unit_registry`

### 6. Updated tests
- `test_pint_backend.py`: Updated SymPy-specific test to test CustomUnitRegistry
- `test_unit_recognition.py`: Removed `TestPintToSympy` class (tested removed functions)
- Updated imports to use `get_custom_unit_registry` instead of `get_sympy_unit_registry`

## Files Modified
1. `/src/livemathtex/engine/pint_backend.py` - Major refactoring
2. `/src/livemathtex/engine/__init__.py` - Updated import
3. `/tests/test_pint_backend.py` - Updated test
4. `/tests/test_unit_recognition.py` - Removed obsolete tests, updated imports

## Verification Results

### Import verification
```bash
$ python -c "from livemathtex.engine.pint_backend import get_unit_registry; print('OK')"
OK

$ python -c "
import sys
from livemathtex.engine.pint_backend import get_unit_registry
sympy_loaded = any('sympy' in mod for mod in sys.modules)
print(f'SymPy loaded: {sympy_loaded}')
"
SymPy loaded: False
```

### Test results
- All pint_backend tests pass: 45/45
- All unit_recognition tests pass: 20/20 (after removing obsolete SymPy tests)
- Pre-existing failures in other test files (not caused by these changes)

## Pre-existing Test Failures
56 tests in other files fail with "Unexpected token after expression" errors. These are **pre-existing issues** with the expression parser not handling unit suffixes in value definitions (e.g., `$x := 5\ V$`). Verified by running tests against original code before changes. This is out of scope for Phase 28-02.

## Metrics
- Lines removed: ~600 (SymPy-related code)
- Lines added: ~150 (backwards compatibility and simplified CustomUnitRegistry)
- Net reduction: ~450 lines
- SymPy references: 148 -> 5 (all 5 are backwards compatibility names/comments)

## Next Steps
- Phase 28-03: Remove SymPy from evaluator.py (already mostly done, cleanup remaining)
- Future: Fix expression parser to handle unit suffixes in value definitions
