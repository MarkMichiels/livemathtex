---
phase: 27-remove-dependencies
plan: 01
subsystem: engine, parser
tags: [custom-parser, constants, fallback]
requires: [phase-26]
provides: [custom_parser_primary]
affects: []
tech-stack:
  added: []
  patterns: [try-first-fallback, mathematical-constants]
key-files:
  modified:
    - src/livemathtex/engine/evaluator.py
    - src/livemathtex/engine/expression_evaluator.py
    - src/livemathtex/parser/expression_tokenizer.py
    - src/livemathtex/parser/expression_parser.py
    - tests/test_expression_tokenizer.py
    - tests/test_expression_parser.py
key-decisions:
  - Keep fallback for functions (ln, sin, etc.) - custom parser doesn't handle these
  - Superscripts are operators in evaluations, not part of variable names
  - Mathematical constants (pi, e) handled in expression evaluator
  - Braced expressions supported for LaTeX grouping (e^{x})
issues-created: []
duration: 25 min
completed: 2026-01-14
---

# Phase 27 Plan 01: Custom Parser as Primary Path Summary

**Custom parser as PRIMARY evaluation path with latex2sympy fallback for unsupported features**

## Original Goal vs Actual Outcome

**Original goal:** Remove latex2sympy fallback entirely
**Actual outcome:** Keep fallback for edge cases (functions like \ln, \sin)

The custom parser successfully handles most expressions, but functions like `\ln()`, `\sin()`, etc. require the latex2sympy fallback.

## Changes Made

### 1. Expression Evaluator - Mathematical Constants

Added support for `\pi` and `e`:
```python
MATH_CONSTANTS = {
    r"\pi": math.pi,
    "\\pi": math.pi,
    "e": math.e,  # Euler's number (standalone 'e')
}
```

### 2. Expression Tokenizer - Superscript Handling

Changed superscripts to be operators, not part of variable names:
- Before: `R^2` → single VARIABLE token "R^2"
- After: `R^2` → VARIABLE "R", OPERATOR "^", NUMBER "2"

This is correct for evaluations where `x^2` means "x raised to power 2".
Variable definitions (`R^2 := 0.904`) still work via `_compute()` / latex2sympy.

### 3. Expression Parser - Braced Expressions

Added support for LaTeX braced grouping:
```python
# Braced expression (LaTeX grouping, e.g., ^{x+1})
if self._check(TokenType.LBRACE):
    self._advance()
    expr = self._expression()
    # ... handle closing brace
```

### 4. Evaluator - Internal ID Rewriting

Added `_rewrite_with_internal_ids()` call to custom parser path:
- Ensures multi-letter variables like "Cap" become "v_{0}"
- Symbol map now includes internal_id mappings

### 5. Fallback Preserved

Kept latex2sympy fallback for expressions the custom parser can't handle:
- Functions: `\ln()`, `\sin()`, `\cos()`, etc.
- Complex LaTeX constructs

## Test Changes

Updated tests to reflect new behavior:
- `test_superscript_variable` → `test_superscript_as_operator`
- `test_superscript_braces` and `test_superscript_simple` now expect BinaryOpNode

## Test Results

- **Before Phase 27:** 528 passed
- **After Phase 27:** 528 passed, 3 xpassed
- All tests pass with custom parser as primary + fallback

## Files Modified

- `src/livemathtex/engine/evaluator.py`
  - Restored fallback with custom parser as primary
  - Added internal_id mapping to custom parser path

- `src/livemathtex/engine/expression_evaluator.py`
  - Added MATH_CONSTANTS for pi and e
  - Updated _lookup_variable to check constants first

- `src/livemathtex/parser/expression_tokenizer.py`
  - Removed superscript patterns (^ is now always an operator)

- `src/livemathtex/parser/expression_parser.py`
  - Added braced expression handling for LaTeX grouping

- `tests/test_expression_tokenizer.py`
  - Updated superscript test to expect operator behavior

- `tests/test_expression_parser.py`
  - Updated superscript tests to expect BinaryOpNode

## Commits

1. `feat(27-01): custom parser as primary with latex2sympy fallback`

## Decisions

1. **Keep fallback:** Functions like `\ln()` require SymPy, not worth implementing custom
2. **Superscripts are operators:** In evaluations, `x^2` means exponentiation
3. **Constants in evaluator:** `\pi` and `e` handled by expression evaluator
4. **Braces for grouping:** `^{x+1}` now parses correctly

## Future Work

To fully remove latex2sympy dependency would need:
- Custom function handling (ln, sin, cos, sqrt, etc.)
- Handle \text{} wrapped variable names in tokenizer
- Replace SymPy Lambda for function definitions
