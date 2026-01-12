---
phase: 01-critical-bug-fix
plan: 01
subsystem: engine
tags: [evaluator, pint, units, error-handling, tdd]

# Dependency graph
requires:
  - phase: none
    provides: first phase
provides:
  - Strict undefined symbol handling in formulas
  - Unit fallback removal for formula contexts
  - Comprehensive error catalog example
affects: [02-medium-bugs, 03-api-features]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Units belong as suffixes to numbers (5\\ V), not standalone symbols"
    - "Always use subscripts to avoid unit conflicts (V_tot, m_1)"

key-files:
  created:
    - tests/test_definition_types.py
    - examples/error-handling/input.md
    - examples/error-handling/output.md
  modified:
    - src/livemathtex/engine/evaluator.py
    - examples/simple-units/input.md
    - examples/engineering/input.md
    - .planning/ISSUES.md
    - examples/README.md

key-decisions:
  - "Remove unit fallback entirely - undefined symbols always error"
  - "Breaking change: 10 \\cdot kg no longer works, use 10\\ kg"
  - "Update examples to use correct syntax rather than revert fix"

patterns-established:
  - "Backslash-space for unit attachment: $mass := 10\\ kg$"
  - "Subscripted variables avoid unit conflicts: V_tot, m_1, A_0"

issues-created: []

# Metrics
duration: 11min
completed: 2026-01-11
---

# Phase 1 Plan 1: ISS-003 Fix Summary

**Strict undefined symbol handling via TDD fix - units must be attached to numbers, not used as standalone symbols in formulas**

## Performance

- **Duration:** 11 min
- **Started:** 2026-01-11T15:50:43Z
- **Completed:** 2026-01-11T16:01:50Z
- **Tasks:** 5
- **Files modified:** 12

## TDD Cycle

### RED
- Test file: tests/test_definition_types.py
- Test cases:
  - `test_undefined_V_in_formula_raises_error` - V * 15 * 0.001 with decimal
  - `test_undefined_N_in_formula_raises_error` - N * 10.5 with decimal
  - Plus 11 additional tests for edge cases
- Why they failed: Code allowed unit fallback when `is_definition_with_units=True` (expression had decimals)

### GREEN
- Implementation in: src/livemathtex/engine/evaluator.py
- Changes: Removed `is_pure_formula` condition, always error for undefined symbols matching units
- 28 lines removed, 13 lines added - net simplification

### REFACTOR
- Updated examples to use correct syntax (`10\ kg` instead of `10 \cdot kg`)
- Renamed variables in engineering example (U→U_0, A→A_0) to avoid unit conflicts

## Task Commits

Each task was committed atomically:

1. **Task 1: Write failing tests (RED)** - `c288cc8` (test)
2. **Task 2: Implement fix (GREEN)** - `9b3610f` (fix)
3. **Task 3: Update examples for strict naming** - `5857a82` (refactor)
4. **Task 4: Add error-handling example** - `f2cc588` (docs)
5. **Task 5: Update documentation** - `512c3a4` (docs)

## Files Created/Modified

- `src/livemathtex/engine/evaluator.py` - Remove unit fallback in _compute()
- `tests/test_definition_types.py` - New: 13 tests for definition type handling
- `examples/error-handling/` - New: exhaustive error catalog (7 categories)
- `examples/simple-units/input.md` - Fix unit syntax (use `\ ` not `\cdot`)
- `examples/engineering/input.md` - Rename U→U_0, A→A_0
- `.planning/ISSUES.md` - Mark ISS-003 as resolved
- `examples/README.md` - Add error-handling, document correct syntax

## Accomplishments

- Fixed critical bug where undefined symbols silently became units
- 13 new tests covering definition type edge cases
- Error-handling example serves as user documentation and regression test
- Breaking change documented with clear migration path

## Decisions Made

1. **Remove unit fallback entirely** - simpler code, clearer semantics
2. **Breaking change acceptable** - existing syntax was incorrect, examples updated
3. **Examples updated rather than fix reverted** - correct syntax should be enforced

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Phase 1 complete (single plan)
- Ready for Phase 2: Medium Bugs (ISS-004 and ISS-005)
- All 115 tests passing

---
*Phase: 01-critical-bug-fix*
*Completed: 2026-01-11*
