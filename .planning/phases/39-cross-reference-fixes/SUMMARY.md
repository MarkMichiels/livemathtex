---
phase: 39-cross-reference-fixes
plan: 01
status: complete
completed: 2026-01-16
---

# Phase 39 Summary: Cross-Reference Fixes

## Bugs Fixed

### ISS-049: Unit hint syntax parsed as array index

**Problem:** `{{flow [m³/h]}}` was being parsed by ExpressionParser which interpreted `[m³/h]` as array indexing syntax.

**Solution:**
1. Extended `Reference` dataclass with `unit_hint: Optional[str]` field
2. Updated regex pattern in `extract_references()` to capture `[unit]` syntax BEFORE expression parsing:
   ```python
   pattern = r'(?<!\\)\{\{((?:[^{}\[\]]|\{[^{}]*\})*?)(?:\s*\[([^\]]+)\])?\}\}'
   ```
3. Updated `evaluate_cross_references()` to apply unit conversion when `ref.unit_hint` is set
4. Updated `find_processed_references()` and `restore_references()` to preserve unit hints in HTML comments

**Files modified:**
- `src/livemathtex/parser/reference_parser.py`
- `src/livemathtex/core.py`
- `tests/test_reference_parser.py`

### ISS-050: Subscript and underscore variable lookup fails

**Problem:** Cross-references like `{{η_sys}}` and `{{P_motor}}` failed to find variables in the symbol table because:
- Symbol table stores `eta_sys` but cross-ref has `η_sys` (Unicode Greek)
- Tokenizer can't parse LaTeX-style names like `\eta_{sys}`

**Solution:**
1. Created `_normalize_variable_name()` helper function that generates lookup variations:
   - Unicode Greek → ASCII name (η → eta) - PRIORITIZED for tokenizer compatibility
   - Underscore variations (P_motor → P\_motor, P_{motor})
   - LaTeX Greek (η → \eta)
2. Try plain ASCII name FIRST (parseable by tokenizer), then LaTeX forms as fallback
3. Build symbol_dict with multiple name variations for lookup

**Greek letter mapping:**
- Unicode → ASCII (for symbol lookup): `η_sys` → `eta_sys`
- Unicode → LaTeX (for fallback): `η` → `\eta`

### ISS-051: Output uses SI base units instead of readable units

**Problem:** Cross-reference output showed verbose Pint unit strings like `kilogram * meter ** 2 / second ** 3` instead of readable `W`.

**Solution:**
1. Created `_format_unit_for_prose()` helper function that:
   - Maps verbose unit strings to common symbols (kilogram → kg, meter → m, etc.)
   - Handles exponents (** 2 → ², ** 3 → ³)
   - Converts operators (* → ·, ** → ^)
2. Fixed bug where `entry.display_unit` was used but `SymbolValue` has `original_unit`
   - Changed to `entry.original_unit` which broke the silent exception that was swallowing symbols

## Additional Fixes

### Space preservation in restore_references

When restoring processed references back to `{{ref}}` syntax, the leading space before the numeric value was being lost.

**Solution:** Added logic to preserve leading whitespace when the match captures it:
```python
if start > 0 and content[start] in ' \t':
    replacement = ' ' + replacement
```

## Test Results

- All 595 tests pass
- Cross-reference test suite: 13 tests pass
- Reference parser tests: 22 tests pass
- Example snapshot test updated to reflect working cross-references

## Known Remaining Issue

The `{{weight [kN]}}` cross-reference fails with unit conversion error because the underlying calculation produces `kg³` instead of `kg` (a bug in unit parsing for `kg/m³`, not a cross-reference bug). This is tracked separately.

## Files Modified

1. `src/livemathtex/parser/reference_parser.py`
   - Added `unit_hint` field to Reference dataclass
   - Updated regex patterns for unit hint support
   - Fixed space preservation in restore_references

2. `src/livemathtex/core.py`
   - Added `_normalize_variable_name()` function
   - Added `_format_unit_for_prose()` function
   - Rewrote `evaluate_cross_references()` to handle all three bugs
   - Fixed `display_unit` → `original_unit` attribute access

3. `tests/test_reference_parser.py`
   - Updated test to expect 4-tuple from `find_processed_references()`

4. `examples/cross-references/output.md`
   - Updated expected output to reflect working cross-references
