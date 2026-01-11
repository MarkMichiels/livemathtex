# Roadmap: LiveMathTeX v1.1

## Overview

Fix critical calculation bugs that undermine trust, then add quality-of-life features (public API, clear command). Small, focused milestone.

## Domain Expertise

None (standard Python CLI patterns)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Critical Bug Fix** - Fix ISSUE-003 (variable/unit fallback)
- [ ] **Phase 2: Bug Fixes** - Fix ISSUE-004, ISSUE-005, and ISSUE-006
- [ ] **Phase 3: API Features** - FEAT-001 (public API) and FEAT-002 (clear command)

## Phase Details

### Phase 1: Critical Bug Fix
**Goal**: Fix ISSUE-003 - failed variable definition must not silently fall back to unit interpretation
**Depends on**: Nothing (first phase)
**Research**: Unlikely (internal codebase, issue well-documented in BACKLOG.md)
**Plans**: 1 plan (TDD approach)

Plans:
- [x] 01-01: TDD fix for variable/unit fallback bug

### Phase 2: Bug Fixes
**Goal**: Fix ISSUE-004, ISSUE-005, and ISSUE-006 (directive parser, LaTeX units, dimensional analysis)
**Depends on**: Phase 1
**Research**: Unlikely (solutions documented in BACKLOG.md)
**Plans**: 3 plans

Plans:
- [ ] 02-01: Fix directive parser to skip code blocks (ISSUE-004)
- [ ] 02-02: Add LaTeX unit cleaning for Pint (ISSUE-005)
- [ ] 02-03: Add dimensional compatibility checking (ISSUE-006)

### Phase 3: API Features
**Goal**: Expose public Python API (FEAT-001) and add clear command (FEAT-002)
**Depends on**: Phase 2
**Research**: Unlikely (straightforward Python patterns)
**Plans**: 2 plans

Plans:
- [ ] 03-01: Expose public API in __init__.py
- [ ] 03-02: Add livemathtex clear command

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Critical Bug Fix | 1/1 | Complete | 2026-01-11 |
| 2. Bug Fixes | 0/3 | Not started | - |
| 3. API Features | 0/2 | Not started | - |
