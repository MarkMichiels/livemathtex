# Roadmap: LiveMathTeX v1.1

## Overview

Fix critical calculation bugs that undermine trust, add quality-of-life features (public API, clear command), and improve output formatting (unit conversion). Small, focused milestone.

## Domain Expertise

None (standard Python CLI patterns)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Critical Bug Fix** - Fix ISS-003 (variable/unit fallback)
- [x] **Phase 2: Bug Fixes** - Fix ISS-004, ISS-005, and ISS-006
- [x] **Phase 3: API Features** - ISS-010 (public API) and ISS-011 (clear command)
- [x] **Phase 4: Output Unit Conversion** - Verify ISS-007 (already working), add ISS-008 (inline unit hint syntax)

## Phase Details

### Phase 1: Critical Bug Fix
**Goal**: Fix ISS-003 - failed variable definition must not silently fall back to unit interpretation
**Depends on**: Nothing (first phase)
**Research**: Unlikely (internal codebase, issue well-documented in ISSUES.md)
**Plans**: 1 plan (TDD approach)

Plans:
- [x] 01-01: TDD fix for variable/unit fallback bug

### Phase 2: Bug Fixes
**Goal**: Fix ISS-004, ISS-005, and ISS-006 (directive parser, LaTeX units, dimensional analysis)
**Depends on**: Phase 1
**Research**: Unlikely (solutions documented in ISSUES.md)
**Plans**: 3 plans

Plans:
- [x] 02-01: Fix directive parser to skip code blocks (ISS-004)
- [x] 02-02: Add LaTeX unit cleaning for Pint (ISS-005)
- [x] 02-03: Add dimensional compatibility checking (ISS-006)

### Phase 3: API Features
**Goal**: Expose public Python API (ISS-010) and add clear command (ISS-011)
**Depends on**: Phase 2
**Research**: Unlikely (straightforward Python patterns)
**Plans**: 2 plans

Plans:
- [x] 03-01: Expose public API in __init__.py
- [x] 03-02: Add livemathtex clear command

### Phase 4: Output Unit Conversion
**Goal**: Verify and document ISS-007 (already working), implement ISS-008 (inline unit hint syntax)
**Depends on**: Phase 2 (uses Pint infrastructure)
**Research**: Unlikely (Pint conversion well-understood)
**Plans**: 2 plans

**Note**: ISS-007 (`<!-- [unit] -->` syntax) was found to be already implemented and working during planning. Phase 4 Plan 1 focuses on adding tests and documentation. Plan 2 implements the new inline syntax.

Plans:
- [x] 04-01: Add tests and documentation for unit conversion (verify ISS-007)
- [x] 04-02: Add inline unit hint syntax `$E == [MWh]$` (ISS-008)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Critical Bug Fix | 1/1 | Complete | 2026-01-11 |
| 2. Bug Fixes | 3/3 | Complete | 2026-01-11 |
| 3. API Features | 2/2 | Complete | 2026-01-12 |
| 4. Output Unit Conversion | 2/2 | Complete | 2026-01-11 |

**Milestone v1.1 Complete:** 8/8 plans executed successfully.
