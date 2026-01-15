<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-031: Unit propagation failure when multiplying unit by dimensionless value

This test reproduces the bug where multiplying a unit by a dimensionless value loses the unit, showing the result as "dimensionless" instead of preserving the original unit.

## Unit Validation

**Purpose:** Validate that all units used in this document are correctly interpreted by Pint.

**Units to test:**
$u_{umol_J} := 1\ \frac{µmol}{J}$ <!-- [micromol/J] SI base: [substance] / [energy] -->
$u_{dimensionless} := 1$ <!-- [dimensionless] -->

**Expected:** All units should be correctly recognized. When multiplying `µmol/J` by a dimensionless value, the result should still be `µmol/J`.

## Test Case

**Setup:** Multiply a unit by a dimensionless value.

**Expected:** The result should preserve the unit (e.g., `µmol/J × 0.9143 = 3.922 µmol/J`).

**Actual:** The result shows as "dimensionless" instead of preserving the unit.

### Calculation

**Setup:**
$PPE_{red} := 4.29\ \frac{\text{µmol}}{\text{J}}$ <!-- [micromol/J] -->
$f_{geom} := 0.9143$ <!-- [dimensionless] -->

**Test:**
$PPE_{eff} := PPE_{red} \cdot f_{geom} == 3.9223\ \text{µmol/J}$ <!-- [µmol/J] -->

**Expected result:** `3.922 µmol/J` (or `3.922 micromol/J`)

**Actual result:** Shows as `3.922` (dimensionless) with warning: "Cannot convert from 'dimensionless' to 'µmol/J' - dimensions incompatible"

### Steps to Reproduce

1. Run: `livemathtex clear test_iss_031_unit_propagation_dimensionless.md`
2. Run: `livemathtex process test_iss_031_unit_propagation_dimensionless.md`
3. Check line with `PPE_{eff}` - it should show `3.922 µmol/J` but shows `3.922` (dimensionless) with unit conversion warning

### Root Cause

**Unit propagation failure:** When multiplying a unit (`µmol/J`) by a dimensionless value (`0.9143`), LiveMathTeX loses the unit and treats the result as dimensionless. This is incorrect - the unit should be preserved.

**Manual calculation (correct):**
- `PPE_{red} = 4.29 µmol/J`
- `f_{geom} = 0.9143` (dimensionless)
- `PPE_{eff} = 4.29 µmol/J × 0.9143 = 3.922 µmol/J` ✓ (unit preserved)

**LiveMathTeX calculation (bug):**
- Calculates `3.922` correctly
- Loses the unit, treats result as dimensionless
- When trying to convert to `µmol/J` (via unit hint), fails with "dimensions incompatible" warning

**The bug:** Unit propagation fails when multiplying units by dimensionless values. The result should preserve the original unit.

**Impact:** High - prevents calculations that multiply units by dimensionless factors (common in physics/engineering calculations).

---

> *livemathtex: 2026-01-16 00:27:43 | 5 definitions, 1 evaluation | no errors | 0.07s* <!-- livemathtex-meta -->
