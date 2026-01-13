---
phase: 11-token-classification
plan: 01
type: execute
status: complete
---

# Summary: Token Classification for Multi-Letter Identifiers

## Objective

Improve multi-letter identifier handling with better diagnostics for implicit multiplication detection. When `latex2sympy` interprets multi-letter identifiers (like `PPE`, `PAR`) as implicit multiplication, provide clear error messages mentioning the intended symbol.

## Outcome

**Success** - All tasks completed, ISS-018 and ISS-022 addressed. 348 tests pass (346 passed + 2 xfailed for known evaluator bugs).

## Changes Made

### Task 1: Create token_classifier module

**Commit:** `9e69b9f` feat(11-01): create token_classifier module with multi-letter detection

- Created `src/livemathtex/engine/token_classifier.py`
- `TokenType` enum: UNIT, VARIABLE, FUNCTION, UNKNOWN
- `ImplicitMultInfo` dataclass: intended_symbol, split_as, undefined_letters, unit_conflicts
- `TokenClassifier` class with:
  - `classify()` - Classify tokens by type
  - `is_multi_letter_identifier()` - Detect PPE, PAR, ABC patterns
  - `has_unit_conflict()` - Check if letter conflicts with unit (A=ampere, V=volt, etc.)
  - `detect_implicit_multiplication()` - Identify when latex2sympy split an identifier

### Task 2: Integrate classifier into evaluator

**Commit:** `b22c110` feat(11-01): integrate token_classifier into evaluator

- Added `TokenClassifier` instance to `Evaluator.__init__()`
- Refactored `_compute()` to:
  - Collect ALL undefined symbols first (instead of raising immediately)
  - Check for implicit multiplication pattern
  - Generate specialized error message if pattern detected
  - Fall back to generic error otherwise
- Updated `_check_undefined_symbols()` to also use classifier
- Updated `examples/error-handling/output.md` with new error messages

### Task 3: Add regression tests

**Commit:** `8c46583` test(11-01): add comprehensive tests for token classifier

- Created `tests/test_token_classifier.py` with 46 tests:
  - TokenClassifier.classify() tests (units, variables, functions)
  - is_multi_letter_identifier() tests
  - has_unit_conflict() tests
  - detect_implicit_multiplication() tests
  - End-to-end error message tests (PPE, PAR)
  - Regression tests for existing functionality

## Key Technical Details

### Error Message Improvement

**Before:**
```
Error: Undefined variable 'P'. ('P' is also a unit: unit. Use a subscript...)
```

**After:**
```
Error: Undefined variable 'PPE'. Note: 'PPE' was parsed as implicit
multiplication (P*P*E). Define '$PPE := ...$' before use, or use a
structured name like 'PPE_{...}'. ('A' is also a unit (ampere))
```

### Detection Algorithm

1. Scan original LaTeX for contiguous multi-letter sequences (e.g., `PPE`, `PAR`)
2. Skip known functions (`sin`, `cos`), known units (`kg`, `MWh`)
3. Check if sequence's letters appear as separate symbols in parsed expression
4. If match found, generate specialized error with intended symbol name

### Single-Letter Unit Conflicts

Tracks common single-letter unit conflicts:
- A = ampere, V = volt, W = watt, J = joule, N = newton
- C = coulomb, F = farad, H = henry, K = kelvin, T = tesla
- m = meter, s = second, g = gram, L = liter

## Issues Resolved

- **ISS-018**: Implicit multiplication of multi-letter identifiers causes misleading errors - **FIXED**
- **ISS-022**: Improve diagnostics when multi-letter identifiers are split - **FIXED**

## Verification

- [x] `from livemathtex.engine.token_classifier import TokenClassifier` works
- [x] `$x := PPE$` error mentions 'PPE' and 'implicit multiplication'
- [x] `$x := PAR$` error mentions 'PAR' and 'ampere' conflict
- [x] `$PPE := 1$\n$x := PPE$` works correctly (existing behavior)
- [x] All 348 tests pass (346 passed + 2 xfailed)
- [x] New tests in test_token_classifier.py pass (46 tests)

## Test Results

```
346 passed, 2 xfailed, 11 warnings in 75.38s
```

## Next Steps

- Phase 12: Unit Warnings (distinguish calculation errors from formatting warnings)
