# Roadmap: LiveMathTeX

## Overview

LiveMathTeX is a CLI tool for evaluating LaTeX calculations in Markdown with unit support. Development progresses through focused milestones addressing stability, unit handling, and features.

## Domain Expertise

None (regex patterns, Python, Pint library)

## Milestones

- ✅ **v1.1 Foundation** - Phases 1-4 (shipped 2026-01-12)
- ✅ **v1.2 Process/Clear Stability** - Phase 1 (shipped 2026-01-12)
- 🚧 **v1.3 Unit Hint Preservation** - Phases 2-4 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (1.1, 1.2): Urgent insertions (marked with INSERTED)

<details>
<summary>✅ v1.2 Process/Clear Stability (Phase 1) - SHIPPED 2026-01-12</summary>

### Phase 1: Fix Clear/Process Cycle
**Goal**: Make process/clear cycle stable and idempotent
**Depends on**: Nothing (first phase)
**Research**: Unlikely (root cause documented in BUG_INVESTIGATION.md)
**Plans**: 2 plans

Plans:
- [x] 01-01: Fix clear_text() error markup patterns
- [x] 01-02: Add idempotency check and verify full cycle

</details>

### 🚧 v1.3 Unit Hint Preservation (In Progress)

**Milestone Goal:** Fix unit hint preservation (ISS-013) and custom unit evaluation lookup (ISS-009)

#### Phase 2: Preserve Inline Unit Hints ✅
**Goal**: Inline `[unit]` syntax survives processing and re-processing (ISS-013)
**Depends on**: Phase 1 (v1.2 complete)
**Research**: Unlikely (internal patterns, clear_text already handles some restoration)
**Plans**: 1 plan

**Sub-goals:**
1. ✅ Preserve inline unit hint `[kJ]` in processed output (convert to HTML comment)
2. ✅ Ensure re-processing uses preserved hint
3. ✅ Tests verify inline hints survive processing cycle

**Files changed:**
- `src/livemathtex/core.py` - Track inline unit hint from calculations, pass to renderer
- `src/livemathtex/render/markdown.py` - Support tuple format, inject HTML comment
- `tests/test_inline_unit_hints.py` - Added `TestInlineUnitHintReprocessing` class

Plans:
- [x] 02-01: Preserve inline hints via HTML comment injection

#### Phase 3: Fix Evaluation Unit Lookup ✅
**Goal**: Standalone `$var ==` evaluations find custom units defined with division (ISS-009)
**Depends on**: Phase 2
**Research**: No - root cause identified (see 03-01-PLAN.md)
**Plans**: 1 plan

**Actual Root Cause:** `_handle_assignment` didn't propagate units for formula assignments (like `ratio := E_1 / m_1`). The variable was stored with `unit=None`.

**Solution Applied:**
1. Fixed `_handle_assignment` to call `_compute(rhs, propagate_units=True)` for formula assignments
2. Extract computed unit with `_extract_unit_from_value`
3. Fixed `_parse_unit_expression` to resolve prefixed units via `pint_to_sympy_with_prefix`
4. Added check in `_handle_unit_definition` to prevent redefining existing Pint units
5. Changed `_apply_conversion` to raise errors instead of silently failing

**Files changed:**
- `src/livemathtex/engine/evaluator.py` - Fixed `_handle_assignment` and `_handle_unit_definition`
- `src/livemathtex/engine/pint_backend.py` - Fixed `_parse_unit_expression`
- `tests/test_pint_backend.py` - Added `TestCustomUnitWithDivision` class with 5 tests
- `examples/custom-units/input.md` - Updated to remove unnecessary unit definitions

Plans:
- [x] 03-01: Fix unit propagation and error handling

#### Phase 4: Re-processing Verification
**Goal**: End-to-end verification of unit hint preservation through process→clear→process cycle
**Depends on**: Phase 3
**Research**: Unlikely (testing)
**Plans**: TBD

**Sub-goals:**
1. Add comprehensive tests for inline unit hints through full cycle
2. Add tests for custom division units through full cycle
3. Verify no regressions in existing functionality

**Files to change:**
- `tests/test_process_clear_cycle.py` - Extend with unit hint scenarios
- `tests/test_inline_unit_hints.py` - Add cycle tests

Plans:
- [x] 04-01: Add cycle tests for unit hints and custom units

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Fix Clear/Process Cycle | v1.2 | 2/2 | Complete | 2026-01-12 |
| 2. Preserve Inline Unit Hints | v1.3 | 1/1 | Complete | 2026-01-12 |
| 3. Fix Evaluation Unit Lookup | v1.3 | 1/1 | Complete | 2026-01-12 |
| 4. Re-processing Verification | v1.3 | 1/1 | Complete | 2026-01-12 |

**Milestone v1.3 Progress:** 3/3 phases complete ✅
