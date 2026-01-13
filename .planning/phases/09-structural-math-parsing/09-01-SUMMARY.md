# Summary: Parse calculations with character-level spans

**Plan:** 09-01
**Phase:** 09-structural-math-parsing
**Status:** Complete
**Duration:** ~12 min

## Objective

Parse calculations within math blocks into structured representation with character-level spans. Replace regex-based operator detection with span-aware parsing built on Phase 8's hybrid parser.

## Tasks Completed

### Task 1: Create ParsedCalculation dataclass with spans
- **Commit:** cb8698d
- Created `src/livemathtex/parser/calculation_parser.py` with:
  - `Span` dataclass with `start`, `end`, and `extract(text)` helper
  - `ParsedCalculation` dataclass with spans for all semantic parts
  - Operations: `===`, `:=`, `==`, `=>`, `:=_==`, `value`, `ERROR`

### Task 2: Implement parse_calculation_line function
- **Commit:** 3cdd324
- Added `parse_calculation_line(line, line_start_offset, unit_comment)` function:
  - Detects operators in priority order (=== before ==)
  - Calculates exact character spans for operator, lhs, rhs, result
  - Extracts inline unit hints `[unit]` with spans
  - Detects bare `=` as ERROR (when alongside valid operators)
  - Returns None for lines without operators (pure display LaTeX)

### Task 3: Implement parse_math_block_calculations
- **Commit:** 53ac64a
- Added `parse_math_block_calculations(block, unit_comment, value_comment)` function:
  - Handles `value_comment` for special value lookup operations
  - Splits `inner_content` by newlines with offset tracking
  - Calculates document-relative offsets for each line
  - Passes unit_comment through to line parsing

### Task 4: Add comprehensive tests for calculation parser
- **Commit:** c9859be
- Created `tests/test_calculation_parser.py` with 36 tests:
  - Span extraction tests
  - All 5 operator type tests
  - Position accuracy with offsets
  - Unit hint tests (inline and comment)
  - Edge cases (empty, whitespace, no operators)
  - Math block integration tests
  - Full document integration tests

**Fixes during testing:**
- Bare `=` regex updated to exclude `=>` pattern (`(?!>)`)
- Unit hint span calculation fixed to use position in original string

## Verification

- [x] `from livemathtex.parser.calculation_parser import ...` works
- [x] `parse_calculation_line()` returns correct spans for all operators
- [x] `parse_math_block_calculations()` handles multiline blocks
- [x] `text[span.start:span.end]` equals expected content for all spans
- [x] Unit hints extracted correctly (both inline and comment)
- [x] All 36 tests pass

## Issues

None encountered.

## Next Steps

Phase 9 complete. Ready for Phase 10: Clear Refactor - rewrite `clear_text()` to use span-based operations instead of regex.
