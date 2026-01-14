# Summary 22-01: Fix Superscript Unit Conflict (ISS-033)

## Status: COMPLETE

## Problem

Variable names with superscripts (like `R^2` for R-squared coefficient of determination) incorrectly conflicted with Pint unit expressions. Error: "Variable name 'R^2' conflicts with unit 'molar_gas_constant ** 2'".

## Root Cause

The `check_variable_name_conflict()` function in `pint_backend.py` used `is_unit_token()` which internally calls `clean_latex_unit()` to convert LaTeX notation to Pint format. This converted:
- `R^2` → `R**2`
- `R` in Pint is `molar_gas_constant`
- Therefore `R**2` was a valid unit expression (molar_gas_constant squared)

## Solution

Updated `check_variable_name_conflict()` to treat superscripts (`^`) the same as subscripts (`_`) for disambiguation:

```python
# Names with subscripts or superscripts are explicitly disambiguated
# ISS-033: R^2 should be allowed as a variable name (R-squared statistic)
# The ^ character indicates user intent to define a variable, not a unit expression
if '_' in name or '^' in name:
    return None
```

## Test Results

- All 365 tests pass + 3 xpassed
- ISS-033 test file processes correctly: `$R^2 := 0.904$` works without error
- ISS-034 verified already fixed (comma in subscript)
- ISS-035 updated - same root cause as ISS-018 (implicit multiplication)

## Files Modified

- `src/livemathtex/engine/pint_backend.py`:
  - Lines 328-332: Added `^` to disambiguation check

## Verification

```bash
livemathtex clear tests/test_iss_033_superscript_unit_conflict.md
livemathtex process tests/test_iss_033_superscript_unit_conflict.md
# Output: 0 errors - R^2 := 0.904 works correctly
```
