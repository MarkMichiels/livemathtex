# Roadmap: LiveMathTeX v1.2

## Overview

Fix ISS-012: Process/clear cycle instability. Small, focused milestone with single bug fix.

## Domain Expertise

None (regex patterns, Python)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (1.1, 1.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Fix Clear/Process Cycle** - Comprehensive error cleanup and idempotency

## Phase Details

### Phase 1: Fix Clear/Process Cycle
**Goal**: Make process/clear cycle stable and idempotent
**Depends on**: Nothing (first phase)
**Research**: Unlikely (root cause documented in BUG_INVESTIGATION.md)
**Plans**: 2 plans

**Sub-goals:**
1. Fix `clear_text()` to remove ALL error markup formats
2. Ensure processing is idempotent (F9 twice = same result)
3. Ensure clear→process = original process result

**Files to change:**
- `src/livemathtex/core.py` - Improve `clear_text()` error patterns
- `src/livemathtex/parser/lexer.py` - Handle error artifacts gracefully
- `tests/test_process_clear_cycle.py` - Existing failing tests should pass

Plans:
- [x] 01-01: Fix clear_text() error markup patterns
- [x] 01-02: Add idempotency check and verify full cycle

## Progress

**Execution Order:**
Phases execute in numeric order: 1

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fix Clear/Process Cycle | 2/2 | Complete | 2026-01-12 |

**Milestone v1.2 Complete:** 2/2 plans executed successfully.
