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
- 🚧 **v1.5 Parser Architecture** - Phases 8-12 (in progress)

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

### 🚧 v1.5 Parser Architecture (In Progress)

**Milestone Goal:** Replace regex-driven processing with structural parsing for robustness and extensibility. Addresses ISS-017, ISS-018, ISS-019, ISS-020, ISS-021.

**Constraints:**
- Keep documents clean - no extra visible markup for users
- Maintain backward compatibility - existing documents should process identically
- Idempotency is non-negotiable - processing must remain stable on repeated runs

#### Phase 8: Markdown Parser Integration ✅
**Goal**: Integrate markdown parser library (markdown-it-py or mistune) for AST with exact source spans. Extract math blocks as first-class nodes.
**Depends on**: v1.4 complete
**Research**: Complete (hybrid approach: markdown-it-py + pylatexenc)
**Completed**: 2026-01-13
**Plans**: 1

Plans:
- [x] 08-01: Integrate hybrid parser (markdown-it-py + pylatexenc)

#### Phase 9: Structural Math Parsing
**Goal**: Within math blocks, parse calculations into internal structure with spans/offsets for operators (:=, ==, ===, =>), lhs/rhs, rendered result parts, error markup.
**Depends on**: Phase 8
**Research**: Unlikely (internal patterns, builds on Phase 8)
**Plans**: TBD

Plans:
- [ ] 09-01: TBD (run /gsd:plan-phase 9 to break down)

#### Phase 10: Clear Refactor
**Goal**: Rewrite `clear_text()` to use span-based operations instead of regex. Fixes ISS-021 (document corruption around multiline error blocks).
**Depends on**: Phase 9
**Research**: Unlikely (internal refactoring)
**Plans**: TBD

Plans:
- [ ] 10-01: TBD (run /gsd:plan-phase 10 to break down)

#### Phase 11: Token Classification
**Goal**: Centralize "is this a unit, variable, or function?" logic. Handle multi-letter identifiers properly (ISS-018). Either treat as single symbol or provide clear error.
**Depends on**: Phase 10
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Plans:
- [ ] 11-01: TBD (run /gsd:plan-phase 11 to break down)

#### Phase 12: Unit Warnings
**Goal**: Distinguish calculation errors from formatting warnings. Unit conversion failures show warnings (orange) with SI fallback, not red errors (ISS-017).
**Depends on**: Phase 11
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Plans:
- [ ] 12-01: TBD (run /gsd:plan-phase 12 to break down)

## Progress

**Execution Order:** Phases execute in numeric order: 8 → 9 → 10 → 11 → 12

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 8. Markdown Parser Integration | v1.5 | 1/1 | Complete | 2026-01-13 |
| 9. Structural Math Parsing | v1.5 | 0/? | Not started | - |
| 10. Clear Refactor | v1.5 | 0/? | Not started | - |
| 11. Token Classification | v1.5 | 0/? | Not started | - |
| 12. Unit Warnings | v1.5 | 0/? | Not started | - |
