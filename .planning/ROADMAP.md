# Roadmap: LiveMathTeX

## Overview

LiveMathTeX is a CLI tool for evaluating LaTeX calculations in Markdown with unit support. Development progresses through focused milestones addressing stability, unit handling, and features.

## Domain Expertise

None (regex patterns, Python, Pint library)

## Milestones

- ✅ **v1.1 Foundation** - Phases 1-4 (shipped 2026-01-12)
- ✅ **v1.2 Process/Clear Stability** - Phase 1 (shipped 2026-01-12)
- ✅ **v1.3 Unit Hint Preservation** - Phases 2-4 (shipped 2026-01-12)
- ✅ **v1.4 Cleanup & Docs** - Phases 5-7 (shipped 2026-01-12)
- ✅ **v1.5 Parser Architecture** - Phases 8-12 (shipped 2026-01-13)
- ✅ **v1.6 Pint Evaluation Engine** - Phases 13-15 (shipped 2026-01-13)
- ✅ **v1.7 Pint Evaluator Hotfixes** - Phases 16-18 (shipped 2026-01-13)
- ✅ **v1.8 Pint Unit Handling Fixes** - Phase 19 (verified 2026-01-13 - issues not bugs)

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

<details>
<summary>✅ v1.3 Unit Hint Preservation (Phases 2-4) - SHIPPED 2026-01-12</summary>

**Milestone Goal:** Fix unit hint preservation (ISS-013) and custom unit evaluation lookup (ISS-009)

See: [v1.3 Archive](.planning/milestones/v1.3-ROADMAP.md)

**Summary:**
- Phase 2: Preserve Inline Unit Hints - HTML comment injection for unit hint persistence
- Phase 3: Fix Evaluation Unit Lookup - Unit propagation for formula assignments
- Phase 4: Re-processing Verification - Comprehensive cycle tests (190 total tests)

**Issues Resolved:** ISS-013, ISS-009

</details>

<details>
<summary>✅ v1.4 Cleanup & Docs (Phases 5-7) - SHIPPED 2026-01-12</summary>

**Milestone Goal:** Address deferred issues - recursive unit conversion, error markup cleanup, and user documentation

**Issues Resolved:** ISS-014, ISS-015, ISS-016

#### Phase 5: Fix Recursive Units ✅
**Goal**: Fix unit conversion for recursively defined units like MWh, mol/day (ISS-014)
**Depends on**: v1.3 complete
**Completed**: 2026-01-12
**Plans**: 1

Plans:
- [x] 05-01: Verify and test recursive unit conversion (ISS-014 already fixed)

#### Phase 6: Error Markup Cleanup ✅
**Goal**: Detect and clean error markup in input documents (ISS-016)
**Depends on**: Phase 5
**Completed**: 2026-01-12
**Plans**: 1

Plans:
- [x] 06-01: Error markup detection and auto-cleanup

#### Phase 7: User Documentation ✅
**Goal**: Update and complete user documentation (ISS-015)
**Depends on**: Phase 6
**Completed**: 2026-01-12
**Plans**: 1

Plans:
- [x] 07-01: Complete user documentation for v1.4 features

</details>

<details>
<summary>✅ v1.5 Parser Architecture (Phases 8-12) - SHIPPED 2026-01-13</summary>

**Milestone Goal:** Replace regex-driven processing with structural parsing for robustness and extensibility.

See: [v1.5 Archive](milestones/v1.5-ROADMAP.md)

**Summary:**
- Phase 8: Markdown Parser Integration - Hybrid parser (markdown-it-py + pylatexenc)
- Phase 9: Structural Math Parsing - ParsedCalculation with character-level spans
- Phase 10: Clear Refactor - Span-based clear_text implementation (ISS-021)
- Phase 11: Token Classification - Multi-letter identifier diagnostics (ISS-018, ISS-022)
- Phase 12: Unit Warnings - Orange warnings with SI fallback (ISS-017)

**Issues Resolved:** ISS-017, ISS-018, ISS-019, ISS-020, ISS-021, ISS-022

</details>

### ✅ v1.6 Pint Evaluation Engine (Shipped 2026-01-13)

**Milestone Goal:** Fix numerical calculation accuracy by replacing SymPy-based evaluation with Pint-based evaluation for numerical calculations.

**Issues to Resolve:** ISS-023, ISS-024

#### Phase 13: SI Value Fix ✅
**Goal**: Fix `_format_si_value()` LaTeX cleanup that produces malformed output (ISS-023)
**Depends on**: v1.5 complete
**Completed**: 2026-01-13
**Plans**: 1

Plans:
- [x] 13-01: Fix LaTeX cleanup regex in evaluator.py (lines 1314, 1342)

#### Phase 14: Pint Evaluator Core ✅
**Goal**: Replace SymPy numerical evaluation with Pint-based evaluation (ISS-024 core fix)
**Depends on**: Phase 13
**Completed**: 2026-01-13
**Research**: ✅ COMPLETE - see `.planning/phases/14-pint-evaluator/RESEARCH.md`
**Key findings**: Implemented hybrid architecture - latex2sympy for parsing, Pint for numeric evaluation.
**Plans**: 5

Plans:
- [x] 14-01: Create `evaluate_sympy_ast_with_pint()` in pint_backend.py
- [x] 14-02: Add `_compute_with_pint()` wrapper in evaluator.py
- [x] 14-03: Route numeric evaluations (`==` operator) through Pint
- [x] 14-04: Update tests and verify core calculation
- [x] 14-05: Comprehensive tests (15 tests in test_pint_evaluator.py)

#### Phase 15: Verification & Docs ✅
**Goal**: Comprehensive testing of rate×time calculations, update documentation for v1.6
**Depends on**: Phase 14
**Completed**: 2026-01-13
**Plans**: 5

Plans:
- [x] 15-01: Update docs/USAGE.md with rate×time documentation
- [x] 15-02: Create CHANGELOG.md for v1.6 release
- [x] 15-03: Verify edge cases (15 tests in test_pint_evaluator.py)
- [x] 15-04: Update README.md version to 1.6.0
- [x] 15-05: Tag v1.6.0 release

</details>

### ✅ v1.7 Pint Evaluator Hotfixes (Shipped 2026-01-13)

**Milestone Goal:** Fix critical bugs discovered during real-world usage of Pint evaluator with production documents.

**Issues to Resolve:** ISS-025, ISS-026, ISS-027

#### Phase 16: Fix SymPy Constants Handling (ISS-025) ✅
**Goal**: Fix `evaluate_sympy_ast_with_pint()` to handle SymPy mathematical constants (π, e) and fix unsafe isinstance() check
**Depends on**: v1.6 complete
**Status**: Complete
**Completed**: 2026-01-13
**Research**: Unlikely (bug fix with clear solution in ISSUES.md)
**Plans**: 1

Plans:
- [x] 16-01: Add handlers for SymPy constants and fix SympyQuantity isinstance check

#### Phase 17: Fix Compound Rate Units (ISS-026) ✅ (Already Fixed)
**Goal**: Fix calculations with compound rate units containing division (mg/L/day) that produce 86.4x wrong results
**Depends on**: Phase 16
**Status**: Already fixed by v1.6 Pint evaluator work
**Resolution**: Verified 2026-01-13 - compound rate unit calculations work correctly

Plans:
- [x] N/A - Already fixed in Phase 14 (ISS-024)

#### Phase 18: Fix Currency Unit Conversion (ISS-027) ✅ (Already Fixed)
**Goal**: Fix EUR to k€ conversion - ensure EUR/€ are recognized as equivalent and k€ definition works
**Depends on**: Phase 17
**Status**: Already fixed by v1.6 Pint evaluator work
**Resolution**: Verified 2026-01-13 - custom unit prefixes work correctly

Plans:
- [x] N/A - Already fixed in Phase 14 (ISS-024)

</details>

### ✅ v1.8 Pint Unit Handling Fixes (Verified 2026-01-13)

**Milestone Goal:** Verify rate×time calculation and currency unit aliasing reported in ISS-028, ISS-029.

**Issues to Resolve:** ISS-028, ISS-029

#### Phase 19: Verify Pint Unit Calculations (ISS-028, ISS-029) ✅
**Goal**: Verify rate×time calculations and currency unit aliasing work correctly
**Depends on**: v1.7 complete
**Status**: Complete - Issues were not bugs (user reporting error)
**Completed**: 2026-01-13
**Research**: N/A - verification only

**Verification Results:**
- ISS-029: `49,020 g/day × 365 d × 0.90` → Actual: `16,103.07 kg` ✅ (works correctly)
- ISS-028: `139 €/MWh × 1472 MWh` with `<!-- [k€] -->` → Actual: `204.608 kilo€` ✅ (works correctly)
- 365 tests pass, no code changes required

Plans:
- [x] 19-01: Verified - no code changes needed (issues were not bugs)
