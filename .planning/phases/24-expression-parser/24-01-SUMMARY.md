---
phase: 24-expression-parser
plan: 01
subsystem: parser
tags: [parser, latex, recursive-descent, tdd]
requires: [phase-23]
provides: [expression_parser, expr_tree]
affects: [phase-25, phase-26]
tech-stack:
  added: []
  patterns: [recursive-descent, operator-precedence, dataclass-ast]
key-files:
  created:
    - src/livemathtex/parser/expression_parser.py
    - tests/test_expression_parser.py
key-decisions:
  - FracNode as separate type (not BinaryOpNode) for semantic clarity
  - UnitAttachNode wraps any expression with unit
  - Right associativity for ^ via recursive call
  - Normalize \cdot and \times to * operator
issues-created: []
duration: 5 min
completed: 2026-01-14
---

# Phase 24 Plan 01: Expression Parser Summary

**Recursive descent parser converting tokens to expression tree - proper precedence handling**

## TDD Execution

### RED Phase
- Created 69 tests in `tests/test_expression_parser.py`
- Tests covered: ExprNode classes, numbers, variables, units, operators, precedence, parentheses, fractions, unary minus, complex expressions, error handling, edge cases
- All tests failed with `ModuleNotFoundError` (expected)
- Commit: `ef55886`

### GREEN Phase
- Implemented `expression_parser.py` with ExpressionParser class
- Recursive descent with 5 precedence levels
- All 69 tests pass
- Full suite: 481 passed, 3 xpassed
- Commit: `4d7b614`

### REFACTOR Phase
- Code review: No refactoring needed
- Implementation is clean, well-documented

## Accomplishments

- Created ExprNode hierarchy:
  - `NumberNode` - numeric literals
  - `VariableNode` - variable references (keeps LaTeX names as-is)
  - `BinaryOpNode` - binary operations (+, -, *, /, ^)
  - `UnaryOpNode` - unary negation
  - `FracNode` - LaTeX fractions
  - `UnitAttachNode` - expression with unit attached

- Implemented ExpressionParser with precedence:
  1. `_additive()` → +, -
  2. `_multiplicative()` → *, /, \cdot, \times
  3. `_power()` → ^ (right associative!)
  4. `_unary()` → unary -
  5. `_primary()` → atoms (numbers, variables, parens, fractions)

- Error handling with position information
- Unit attachment after any primary expression
- All 481 tests pass (+ 3 xpassed)

## Files Created/Modified

- `src/livemathtex/parser/expression_parser.py` - Parser module (225 lines)
- `tests/test_expression_parser.py` - Parser tests (485 lines)

## Commits

1. `test(24-01): add failing tests for expression parser` - ef55886
2. `feat(24-01): implement expression parser` - 4d7b614

## Decisions Made

1. **FracNode vs BinaryOpNode** - Keep FracNode separate for semantic clarity (fractions render differently)
2. **Variable name preservation** - Keep LaTeX names as-is (E_{26}, \alpha) for later evaluation mapping
3. **Unit attachment** - UnitAttachNode wraps expression, not vice versa
4. **Operator normalization** - \cdot and \times both become "*" internally

## Next Step

Ready for Phase 25 (Direct Pint Evaluator) - evaluate expression tree with Pint directly
