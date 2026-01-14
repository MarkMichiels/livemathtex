---
phase: 23-remove-latex2sympy
plan: 01
subsystem: parser
tags: [tokenizer, latex, parsing, tdd]
requires: []
provides: [expression_tokenizer]
affects: [phase-24, phase-25, phase-26]
tech-stack:
  added: []
  patterns: [priority-ordered-pattern-matching, dataclass-tokens]
key-files:
  created:
    - src/livemathtex/parser/expression_tokenizer.py
    - tests/test_expression_tokenizer.py
key-decisions:
  - Units (\text{}, \mathrm{}) matched before single letters to prevent splitting
  - Multi-letter variables with subscripts/superscripts matched as single tokens
  - Greek letters use backslash-preserved format (\alpha, not α)
  - Whitespace patterns (regular, LaTeX space, line breaks) return None to skip
issues-created: []
duration: 4 min
completed: 2026-01-14
---

# Phase 23 Plan 01: Expression Tokenizer Summary

**Custom LaTeX tokenizer with priority-ordered pattern matching - eliminates implicit multiplication issues**

## TDD Execution

### RED Phase
- Created 47 tests in `tests/test_expression_tokenizer.py`
- Tests covered: TokenType enum, Token dataclass, all token types, whitespace handling, complex expressions, priority ordering, span tracking
- All tests failed with `ModuleNotFoundError` (expected)
- Commit: `2ba47df`

### GREEN Phase
- Implemented `expression_tokenizer.py` with ExpressionTokenizer class
- Priority-ordered PATTERNS list ensures correct tokenization
- All 47 tests pass
- Commit: `f43b276`

### REFACTOR Phase
- Code review: No refactoring needed
- Implementation is clean, well-documented, and follows research patterns

## Accomplishments

- Created TokenType enum with 10 token types (NUMBER, VARIABLE, UNIT, OPERATOR, FRAC, LPAREN, RPAREN, LBRACE, RBRACE, EOF)
- Created Token dataclass with type, value, start, end fields
- Implemented ExpressionTokenizer with priority-ordered pattern matching:
  1. Units in `\text{}` and `\mathrm{}` - HIGHEST priority
  2. Numbers (int, decimal, scientific notation)
  3. Multi-letter variables with subscripts/superscripts
  4. Greek letters
  5. LaTeX commands (`\frac`, `\cdot`, `\times`)
  6. Basic operators (+, -, *, /, ^)
  7. Parentheses and braces
  8. Single letters - LOWEST priority (fallback)
- Pattern extracts unit value from braces (`\text{kg}` → "kg")
- Whitespace handling skips regular spaces, LaTeX spaces (`\ `), and line breaks (`\\`)
- All 47 new tests pass, 410 total tests pass (3 xpassed, 2 timing-flaky failures unrelated to this change)

## Files Created/Modified

- `src/livemathtex/parser/expression_tokenizer.py` - New tokenizer module (169 lines)
- `tests/test_expression_tokenizer.py` - Tokenizer tests (622 lines)

## Commits

1. `test(23-01): add failing tests for expression tokenizer` - 2ba47df
2. `feat(23-01): implement LaTeX expression tokenizer` - f43b276

## Decisions Made

1. **Pattern priority ordering** - Units and multi-letter variables MUST match before single letters
2. **Unit value extraction** - Extract content from braces (`\text{kg}` → value "kg", not "\text{kg}")
3. **Greek letter format** - Preserve backslash notation (`\alpha`) for later evaluation mapping
4. **Skip patterns** - Return None for whitespace to simplify token list

## Issues Encountered

- **Timing-sensitive test failures** - 2 pre-existing tests (`test_reprocess_cycle_is_stable`, `test_process_stability`) fail due to timing differences in metadata footer. Not related to this change, appears to be flaky tests comparing processing time.

## Next Step

Ready for Phase 24 (Expression Parser) - recursive descent parser that converts tokens into expression tree
