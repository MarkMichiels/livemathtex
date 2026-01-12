# Roadmap: LiveMathTeX

## Overview

LiveMathTeX is a CLI tool for evaluating LaTeX calculations in Markdown with unit support. Development progresses through focused milestones addressing stability, unit handling, and features.

## Domain Expertise

None (regex patterns, Python, Pint library)

## Milestones

- ✅ **v1.1 Foundation** - Phases 1-4 (shipped 2026-01-12)
- ✅ **v1.2 Process/Clear Stability** - Phase 1 (shipped 2026-01-12)
- ✅ **v1.3 Unit Hint Preservation** - Phases 2-4 (shipped 2026-01-12)
- 🚧 **v1.4 Cleanup & Docs** - Phases 5-7 (in progress)

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

### 🚧 v1.4 Cleanup & Docs (In Progress)

**Milestone Goal:** Address deferred issues - recursive unit conversion, error markup cleanup, and user documentation

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

#### Phase 7: User Documentation
**Goal**: Update and complete user documentation (ISS-015)
**Depends on**: Phase 6
**Research**: Unlikely (internal documentation work)
**Plans**: TBD

Plans:
- [ ] 07-01: TBD (run /gsd:plan-phase 7 to break down)

## Progress

**Execution Order:** Phases execute in numeric order: 5 → 6 → 7

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 5. Fix Recursive Units | v1.4 | 1/1 | Complete | 2026-01-12 |
| 6. Error Markup Cleanup | v1.4 | 1/1 | Complete | 2026-01-12 |
| 7. User Documentation | v1.4 | 0/? | Not started | - |
