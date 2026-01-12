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

#### Phase 2: Preserve Inline Unit Hints
**Goal**: Inline `[unit]` syntax survives processing and re-processing (ISS-013)
**Depends on**: Phase 1 (v1.2 complete)
**Research**: Unlikely (internal patterns, clear_text already handles some restoration)
**Plans**: TBD

**Sub-goals:**
1. Preserve inline unit hint `[kJ]` in processed output (convert to HTML comment or keep visible)
2. Ensure re-processing uses preserved hint
3. Update clear_text() to restore inline hints from processed output

**Files to change:**
- `src/livemathtex/core.py` - Preserve/restore inline unit hints
- `src/livemathtex/render/markdown.py` - Ensure hints survive rendering
- `tests/test_inline_unit_hints.py` - Add re-processing tests

Plans:
- [ ] 02-01: TBD (run /gsd:plan-phase 2 to break down)

#### Phase 3: Fix Evaluation Unit Lookup
**Goal**: Standalone `$var ==` evaluations find custom units defined with division (ISS-009)
**Depends on**: Phase 2
**Research**: Unlikely (unit registration works, just evaluation lookup missing)
**Plans**: TBD

**Sub-goals:**
1. Fix evaluator to look up custom units for standalone evaluations
2. Ensure `$ratio ==$ <!-- [SEC] -->` works when SEC is defined with division

**Files to change:**
- `src/livemathtex/engine/evaluator.py` - Fix custom unit lookup in evaluation
- `tests/test_pint_backend.py` - Add compound unit tests

Plans:
- [ ] 03-01: TBD (run /gsd:plan-phase 3 to break down)

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
- [ ] 04-01: TBD (run /gsd:plan-phase 4 to break down)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Fix Clear/Process Cycle | v1.2 | 2/2 | Complete | 2026-01-12 |
| 2. Preserve Inline Unit Hints | v1.3 | 0/? | Not started | - |
| 3. Fix Evaluation Unit Lookup | v1.3 | 0/? | Not started | - |
| 4. Re-processing Verification | v1.3 | 0/? | Not started | - |

**Milestone v1.3 Progress:** 0/3 phases complete
