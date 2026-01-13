<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-030: Unit conversion bug - µmol not converted to mol in JSON output

This test reproduces the bug where calculations involving µmol units are stored in JSON with incorrect unit conversion.

## Unit Validation

**Purpose:** Validate that all units used in this document are correctly interpreted by Pint.

**Units to test (using assignments to verify unit parsing):**

$u_{d} := 1\ d$ <!-- [day] SI base: [time] -->
$u_{day} := 1\ day$ <!-- [day] SI base: [time] -->
$u_{mol_d} := 1\ \frac{mol}{d}$ <!-- [mol/day] SI base: [substance] / [time] -->
$u_{mol_day} := 1\ \frac{mol}{day}$ <!-- [mol/day] SI base: [substance] / [time] -->
$u_{umol} := 1\ µmol$ <!-- [micromol] SI base: [substance] -->
$u_{micromol} := 1\ micromol$ <!-- [micromol] SI base: [substance] -->
$u_{umol_J} := 1\ \frac{µmol}{J}$ <!-- [micromol/J] SI base: · ²/ / ² -->
$u_{W} := 1\ W$ <!-- [W] SI base: · ²/ ³ -->
$u_{J} := 1\ J$ <!-- [J] SI base: · ²/ ² -->
$u_{s} := 1\ s$ <!-- [s] SI base: [time] -->

**Expected:** All units should be correctly recognized and convertible. Check JSON output to verify units are stored correctly.

**Note:** SI base units are shown in comments to help identify unit conversion issues early. Check the JSON file (`test_iss_030_inplace_update.lmt.json`) to see how units are stored.

## Test Case

**Setup:** Document contains a calculation with an incorrect old value.

**Expected:** After `livemathtex clear` and `livemathtex process`, the value should be recalculated correctly.

**Actual:** The old incorrect value is retained.

### Calculation

**Setup with dependencies (like original document):**

$PPE_{red} := 4.29\ \frac{\text{µmol}}{\text{J}}$ <!-- [micromol/J] SI base: · ²/ / ² -->
$f_{geom} := 0.9143$ <!-- [dimensionless] -->
$PPE_{eff} := PPE_{red} \cdot f_{geom} == 3.922\ \text{micromol/J}$ <!-- [micromol/J] SI base: · ²/ / ² -->
$P_{LED,dc} := 1920\ W$ <!-- [W] SI base: · ²/ ³ -->
$PAR_{rct} := P_{LED,dc} \cdot PPE_{eff} == 7531\ \text{mol/d}$ <!-- [mol/d] -->

**Expected result:** `650.6127 mol/d` (or approximately `650.6 mol/day`)

**Actual result:** `7531 mol/d` (verkeerd - zou `650.6 mol/d` moeten zijn)

**Note:** De JSON toont `"value": 7530.906240000001, "unit": "mol/s"` (verkeerd - zou `0.0075309 mol/s` of `7530.9 µmol/s` moeten zijn). Wanneer dit wordt geconverteerd naar `mol/d`, zou het `650,670,299 mol/d` moeten geven, maar de output toont `7531 mol/d`, wat suggereert dat er mogelijk geen conversie wordt gedaan of dat er een andere bug is in de conversie.

### Steps to Reproduce

1. This file contains the calculation with dependencies
2. Run: `livemathtex clear test_iss_030_inplace_update.md`
3. Run: `livemathtex process test_iss_030_inplace_update.md`
4. Check line with `PAR_{rct}` - it should show `650.6127 mol/d` but shows `650,670,299.136 mol/d` (1,000,000x too large)

### Root Cause

**Unit conversion bug in JSON output:** When `PPE_{eff}` is calculated as `PPE_{red} \cdot f_{geom}`, it results in `3.9223 µmol/J`. When this is used in `PAR_{rct} := P_{LED,dc} \cdot PPE_{eff}`, the calculation correctly gives `7530.9 µmol/s`, but the JSON output stores this as `7530.9 mol/s` (missing µmol → mol conversion in the stored value).

**Manual calculation (correct):**
- `P_{LED,dc} = 1920 W = 1920 J/s`
- `PPE_{eff} = 3.9223 µmol/J`
- `PAR_{rct} = 1920 J/s × 3.9223 µmol/J = 7530.9 µmol/s`
- Convert µmol → mol: `7530.9 µmol/s = 0.0075309 mol/s`
- Convert to mol/day: `0.0075309 mol/s × 86400 s/day = 650.6 mol/day` ✓

**LiveMathTeX calculation (bug):**
- Calculates `7530.9 µmol/s` correctly
- Stores in JSON as `7530.9 mol/s` (WRONG - should be `0.0075309 mol/s`)
- When converting to `mol/day`, uses `7530.9 mol/s × 86400 s/day = 650,670,299 mol/day` (1,000,000x too large)

**The bug:** The JSON output does not convert µmol to mol when storing the value, so subsequent conversions use the wrong magnitude.

**JSON Analysis:**
- JSON shows: `"value": 7530.906240000001, "unit": "mol/s"` (WRONG)
- Should be: `"value": 0.007530906240000001, "unit": "mol/s"` OR `"value": 7530.906240000001, "unit": "micromol/s"`
- The magnitude is correct for `micromol/s`, but the unit is stored as `mol/s` without adjusting the magnitude
- SI base unit check: `mol/s` = `[substance] / [time]` ✓ (correct dimensionality, but wrong magnitude)

---

> *livemathtex: 2026-01-13 23:01:41 | 15 definitions, 2 evaluations | no errors | 0.25s* <!-- livemathtex-meta -->
