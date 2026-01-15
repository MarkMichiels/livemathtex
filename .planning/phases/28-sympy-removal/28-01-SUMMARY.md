# Phase 28-01: Remove SymPy from Evaluator - SUMMARY

**Status:** COMPLETED
**Execution Time:** 2026-01-15

## Tasks Completed

### Task 1: Remove latex2sympy Fallback
- **Commit:** `f30112b`
- Simplified `_compute_with_pint()` to directly call `_evaluate_with_custom_parser()`
- No fallback to latex2sympy - custom parser (v3.0) handles everything
- Removes ~60 lines of fallback code

### Task 2: Remove _compute() Function
- **Commit:** `e5d841c`
- Deleted the entire `_compute()` function (~295 lines)
- Deleted `_apply_conversion()` function (dead code after removing fallback paths)
- Updated handlers to use Pint exclusively:
  - `_handle_assignment()`: Pint for value computation and storage
  - `_handle_assignment_evaluation()`: Simplified to Pint only
  - `_handle_evaluation()`: No sympy fallback
  - `_handle_symbolic()`: Raises error (sympy-dependent, not supported in v3.0)
- Function definitions now store raw LaTeX instead of sympy.Lambda

### Task 3: Remove All SymPy Imports
- **Commit:** `5f7f9dc`
- Removed all sympy/latex2sympy imports and dead code (~700 lines)
- Dead code removed:
  - `_check_undefined_symbols`, `_check_dimensional_compatibility`
  - `_check_add_dimensional_compatibility`, `_extract_unit_from_value`
  - `_convert_to_si`, `_validate_round_trip`
  - `_extract_unit_string`, `_format_si_value`
  - `_get_numeric_in_unit`, `_parse_unit_expression`, `_parse_single_unit`
  - `_parse_unit_with_prefix`
  - `_normalize_latex`, `_format_result_with_display`, `_format_result`
  - `_format_unit_part`, `_make_katex_compatible`
- Simplified active functions to not use sympy:
  - `_get_numeric_in_unit_latex`: Pint conversion only
  - `_extract_numeric_value`: Simple float conversion
  - `_symbol_to_pint_quantity`: No sympy.N fallback
  - `_handle_evaluation`: Skip LHS normalization
- Removed TokenClassifier initialization

## Verification

All verification criteria passed:
```
$ grep -r "latex2sympy" src/livemathtex/engine/evaluator.py
(no output - 0 references)

$ grep -c "import sympy" src/livemathtex/engine/evaluator.py
0

$ python -c "from livemathtex import process_text"
Import OK
```

## Code Impact

**evaluator.py changes:**
- Lines removed: ~1000 (from ~2400 to ~1470)
- Sympy imports: Removed all
- latex2sympy imports: Removed all
- TokenClassifier: Removed usage (to be deleted in 28-03)

## Technical Notes

1. **Function Definitions:** Now stored as raw LaTeX with formula tracking metadata, not sympy.Lambda objects. Function evaluation will need alternative implementation.

2. **Symbolic Operations (`=>`):** Not supported in v3.0. Raises EvaluationError with clear message.

3. **Unit Conversion:** All unit operations now handled by Pint backend exclusively. No sympy fallback.

4. **Dead Code:** Large portions of the old sympy-based computation pipeline were dead code after switching to the custom parser. This phase cleaned them up.

## Root Cause Fix

This change addresses the root cause of:
- ISS-035: "Symbol not iterable" errors
- ISS-036: Global state corruption
- ISS-037: Dimensionless result errors
- ISS-038: Recursive parsing issues

All caused by latex2sympy corrupting global state. By removing latex2sympy entirely, these issues are eliminated.
