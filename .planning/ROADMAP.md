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
- 🚧 **v1.6 Pint Evaluation Engine** - Phases 13-15 (in progress)

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

### 🚧 v1.6 Pint Evaluation Engine (In Progress)

**Milestone Goal:** Fix numerical calculation accuracy by replacing SymPy-based evaluation with Pint-based evaluation for numerical calculations.

**Issues to Resolve:** ISS-023, ISS-024

#### Phase 13: SI Value Fix ✅
**Goal**: Fix `_format_si_value()` LaTeX cleanup that produces malformed output (ISS-023)
**Depends on**: v1.5 complete
**Completed**: 2026-01-13
**Plans**: 1

Plans:
- [x] 13-01: Fix LaTeX cleanup regex in evaluator.py (lines 1314, 1342)

#### Phase 14: Pint Evaluator Core
**Goal**: Replace SymPy numerical evaluation with Pint-based evaluation (ISS-024 core fix)
**Depends on**: Phase 13
**Research**: ✅ COMPLETE - see `.planning/phases/14-pint-evaluator/RESEARCH.md`
**Key findings**: Previous migration (Phases 1-5) only migrated validation/conversion. Numerical evaluation still uses SymPy. Option B confirmed: Keep latex2sympy as parser, use Pint for numeric evaluation.
**Plans**: TBD

Plans:
- [ ] 14-01: TBD (run /gsd:plan-phase 14 to break down)

#### Phase 15: Verification & Docs
**Goal**: Comprehensive testing of rate×time calculations, update documentation for v1.6
**Depends on**: Phase 14
**Research**: Unlikely (testing patterns)
**Plans**: TBD

Plans:
- [ ] 15-01: TBD (run /gsd:plan-phase 15 to break down)
