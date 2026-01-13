# Summary 21-01: Fix Function Call Evaluation (ISS-032)

## Status: COMPLETE

## Problem

Functions defined with multi-letter names (like `PPE_{eff}`) could not be evaluated when called with arguments. The error was "Cannot convert expression to float" or "Undefined variable 'PPE'" (implicit multiplication).

## Root Causes Found

**Three interrelated issues discovered during investigation:**

1. **Function name lookup mismatch (subscripts)**
   - Functions stored with normalized key `f_test` (no braces)
   - latex2sympy produces `f_{test}` (with braces)
   - `_substitute_symbols` didn't normalize before lookup

2. **latex_name includes full signature**
   - Stored: `PPE_{eff}(r_{frac})` → `f_{0}`
   - Needed: `PPE_{eff}` → `f_{0}`
   - Expression has `PPE_{eff}(0.90)`, can't match full signature

3. **Internal ID reverse lookup missing**
   - After rewrite: `PPE_{eff}(0.90)` → `f_{0}(0.90)`
   - Lookup: `symbols.get('f_0')` → None
   - No reverse mapping from internal ID to original name

## Solution

**Three fixes in `evaluator.py`:**

1. **Fix function name normalization in `_substitute_symbols`** (line 2440)
   ```python
   func_name = self._normalize_symbol_name(func_name_raw)
   ```

2. **Extract just function name for latex_name** (lines 590-594)
   ```python
   func_latex_match = re.match(r'^([^(]+)\s*\(', original_target)
   func_latex_name = func_latex_match.group(1).strip() if func_latex_match else original_target
   ```

3. **Add internal ID reverse lookup** (lines 2451-2459)
   ```python
   if not known and func_name_raw.startswith('f_'):
       latex_name = self.symbols.get_latex_name(func_name_raw)
       if latex_name:
           orig_name = self._normalize_symbol_name(latex_name)
           known = self.symbols.get(orig_name)
   ```

## Test Results

- All 365 tests pass + 3 xpassed
- ISS-032 test file processes correctly
- `PPE_{eff}(0.90) == 3.765` ✓
- Both single-letter and multi-letter function names work

## Files Modified

- `src/livemathtex/engine/evaluator.py`:
  - Lines 590-594: Function latex_name extraction
  - Lines 2436-2463: Function lookup with normalization and reverse mapping

## Verification

```bash
livemathtex process tests/test_iss_032_function_evaluation.md
# Output: PPE_{eff}(0.90) == 3.765 ✓
```
