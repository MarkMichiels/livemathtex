---
phase: 26-evaluator-integration
plan: 01
subsystem: engine
tags: [integration, evaluator, custom-parser]
requires: [phase-25]
provides: [custom_parser_integration]
affects: [phase-27]
tech-stack:
  added: []
  patterns: [fallback-pattern, try-except-fallback]
key-files:
  modified:
    - src/livemathtex/engine/evaluator.py
key-decisions:
  - Try custom parser first, fallback to latex2sympy on failure
  - Log debug messages when custom parser fails
  - Keep existing latex2sympy code intact as fallback
issues-created: []
duration: 5 min
completed: 2026-01-14
---

# Phase 26 Plan 01: Evaluator Integration Summary

**Integrate custom parser into evaluator.py with fallback to latex2sympy**

## Integration Approach

Used try-except-fallback pattern:
1. Try custom parser first via `_evaluate_with_custom_parser()`
2. Catch `ParseError` and `CustomEvaluationError`
3. Log debug message and fallback to existing latex2sympy path

## Accomplishments

- Added `_evaluate_with_custom_parser()` method:
  - Builds symbol map from symbol table
  - Tokenizes with ExpressionTokenizer
  - Parses with ExpressionParser
  - Evaluates with evaluate_expression_tree()
  - Returns Pint Quantity

- Modified `_compute_with_pint()`:
  - Tries custom parser first
  - Falls back to latex2sympy on failure
  - Logs debug message for failures

- Added logging infrastructure:
  - Added `import logging` and `logger = logging.getLogger(__name__)`

## Test Results

- **Pint evaluator tests:** 20/20 passed
- **Full test suite:** 528 passed, 3 xpassed
- **Real document:** Processed with 0 errors
  - 109 symbols
  - 118 definitions
  - 67 evaluations

## Files Modified

- `src/livemathtex/engine/evaluator.py`:
  - Added imports for custom parser modules
  - Added `_evaluate_with_custom_parser()` method
  - Modified `_compute_with_pint()` with try-except-fallback

## Commits

1. `feat(26-01): integrate custom parser into evaluator` - 5defbbb

## Key Code Changes

```python
# New method added
def _evaluate_with_custom_parser(self, expression_latex: str) -> 'pint.Quantity':
    """Evaluate using custom tokenizer/parser pipeline."""
    # Build symbol map
    # Tokenize → Parse → Evaluate
    return result

# Modified _compute_with_pint
def _compute_with_pint(self, expression_latex: str) -> 'pint.Quantity':
    # Try custom parser first (Phase 26 integration)
    try:
        return self._evaluate_with_custom_parser(expression_latex)
    except (ParseError, CustomEvaluationError) as e:
        logger.debug(f"Custom parser failed, falling back: {e}")

    # Fallback: Original latex2sympy path
    ...existing code...
```

## Next Step

Ready for Phase 27 (Remove Dependencies) - remove latex2sympy and sympy
