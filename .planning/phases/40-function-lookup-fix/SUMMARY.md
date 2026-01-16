---
phase: 40-function-lookup-fix
plan: 01
status: complete
completed: 2026-01-16
---

# Phase 40 Summary: Function Lookup Bug Fix

## Bug Fixed

### ISS-048: Function Call Lookup Bug with Multiple Functions

**Problem:** When multiple user-defined functions are defined in a document, calling any function after the first one fails with an incorrect internal ID.

**Example:**
```latex
$f(x) := x^2$           % assigned internal_id f0
$PPE_{eff}(r) := r * 4.29$  % assigned internal_id f1
$result := PPE_{eff}(0.70) ==$  % ERROR: looks for f01 instead of f1
```

**Root Cause:** The `_rewrite_with_internal_ids()` function replaces LaTeX names with internal IDs in sorted order (longest first). However, after replacing `PPE_{eff}` with `f1`, the subsequent replacement of single letter `f` with `f0` was matching the `f` in `f1`, producing `f01`.

**Solution:** Added `[0-9]` to the negative lookahead for single-letter variable replacements:

```python
# Before (buggy):
pattern = rf'(?<!\\)(?<![a-zA-Z]){escaped}(?![a-zA-Z])'

# After (fixed):
pattern = rf'(?<!\\)(?<![a-zA-Z]){escaped}(?![a-zA-Z0-9])'
```

This ensures that `f` is NOT replaced when followed by a digit (like in `f1`, `f2`, etc.) which are already-substituted internal IDs.

## Files Modified

1. `src/livemathtex/engine/evaluator.py`
   - Modified `_rewrite_with_internal_ids()` method
   - Added digit check to prevent replacing letters within internal IDs

## Test Results

- All 595 tests pass
- All 6 function-related tests pass
- Manual testing with 4+ functions confirmed working

## Verification

```python
# Multiple functions now work correctly
$f(x) := x^2$
$g(y) := y * 2$
$h(z) := z + 10$
$PPE_{eff}(r) := r * 4.29$

$result_f := f(3) == 9$       # Works!
$result_g := g(5) == 10$      # Works!
$result_h := h(7) == 17$      # Works!
$result_PPE := PPE_{eff}(0.70) == 3.003$  # Works!
```
