# Phase 15: Verification & Docs

**Goal**: Comprehensive testing of rate×time calculations, update documentation for v1.6
**Status**: PLANNING

## Context

Phase 14 (Pint Evaluator Core) is complete:
- ISS-024 fixed: rate × time calculations work correctly
- 360 tests pass (including 15 new Pint evaluator tests)
- Astaxanthin production analysis processes with 0 errors
- Key calculation verified: 310.7 kW × 8760 h = 2721.732 MWh

## Tasks

### 15-01: Update User Documentation
Update docs/USAGE.md with v1.6 features:
- Document the improved numerical calculation accuracy
- Note that rate × time calculations now work correctly
- Add examples of unit cancellation (power × time → energy)

**Files**: docs/USAGE.md

### 15-02: Update CHANGELOG for v1.6
Create CHANGELOG entry for v1.6 release:
- ISS-023: Fixed LaTeX cleanup regex
- ISS-024: Fixed numerical calculations with Pint evaluator

**Files**: CHANGELOG.md

### 15-03: Verify Edge Cases
Run verification on edge cases identified in ISS-024:
- Mass rate × time → mass (g/day × days = kg)
- Volume flow × time → volume (m³/h × h = m³)
- Energy cost calculations (kW × h × €/kWh)

**Files**: tests/test_pint_evaluator.py (already done in Phase 14)

### 15-04: Update README
Update main README with v1.6 highlights if needed.

**Files**: README.md

### 15-05: Tag Release
Create v1.6.0 git tag after all verification passes.

**Files**: None (git operation)

## Verification

- [ ] All 360+ tests pass
- [ ] docs/USAGE.md updated
- [ ] CHANGELOG.md updated
- [ ] README.md reviewed
- [ ] v1.6.0 tag created

## Estimated Time

~15 minutes (mostly documentation updates)
