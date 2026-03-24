# Drying (Freeze Drying / Lyophilization)

## Overview

Freeze drying (lyophilization) is the final dewatering step, converting concentrated algae paste into a dry, shelf-stable powder. The facility operates two freeze dryers (LYO1 and LYO2) in the Freeze Drying Unit (FDU).

## Equipment

| Parameter | Value |
|-----------|-------|
| Units | 2 (LYO1, LYO2) |
| Type | Shelf-type freeze dryers with condenser |
| Control | Touchscreen with PIN-protected programs |
| Monitoring | OpenSCADA (FDU page) + local freeze dryer screens |
| Vacuum pump | With oil reservoir (requires oil level and water drainage checks) |

## Cycle Parameters

| Parameter | Value |
|-----------|-------|
| Cycle duration | 3-6 days (depending on algae type and paste wetness) |
| Loading program step | Step 1 (loading) — do not start from this step |
| Start step | **Step 2** (always) |
| Primary drying complete | Step 31 (secondary drying 1) |
| Temperature sensors | 3 per freeze dryer (top, center, back of central plate) |
| Tray preparation | Metal trays lined with plastic film, sprayed with alcohol |

### Process Stages

1. **Loading** (Step 1) — trays filled with paste, sensors placed
2. **Freezing** (Steps 2+) — product temperature drops to freezing point
3. **Primary drying** — sublimation under vacuum, ice removed
4. **Secondary drying** (Step 31+) — residual moisture removed at higher temperature
5. **Ready** — program complete, safe to unload

## Loading Procedure

1. Transport concentrated paste from CHU using forklift-moved transport container
2. Connect transport container to FDU connection point
3. Clean strainer and rinse pump (remove residual bleach)
4. Check condenser for ice (must be ice-free before loading)
5. Prepare metal trays with alcohol spray and plastic film lining
6. Place empty trays inside the freeze dryer
7. Pump paste into trays (~24 seconds per tray via programmable pump)
8. Take a sample in a sterile Falcon tube (after filling at least 2 trays), label with batch number
9. Insert 3 temperature sensors into the fullest tray (top, middle, front positions)
10. Close and lock the freeze dryer door
11. Check oil reservoir level and drain any water
12. Enter PIN, verify start step is **Step 2**, enter batch number
13. Start program

## Unloading

1. Verify completion in SCADA (FDU page — check PT11 pressure curve has stabilized)
2. Confirm freeze dryer screen shows step >= 31 ("Ready" or later)
3. If not ready and door was opened, restart from step 17
4. Follow unloading SOP for product removal and packaging

## Documentation

A physical form (green binder) must be completed for every batch. This form is subject to government audit. Required entries:

1. Algae type and LYO unit used
2. Batch number (format: AAA-YYYYMMDD-BBB) under "Pasta"
3. Insect buzzer functionality check (initials + signature)
4. Starting temperature (from sensor mean value) and liters of paste
5. Sample taken confirmation + freeze dryer cleanliness verification
6. Temperature sensor placement confirmation
7. Vacuum pump oil and water check
8. Start date and time
9. Post-loading cleaning confirmation

## Cleaning

After every cycle:
- Clean transport container and pump with water
- Add bleach vial to pump tubing; leave mixture inside
- Fill transport container with water + bleach for storage
- Clean unused trays, remove plastic, return cart and supplies
- Clean floor with water and squeegee
- Deliver sample to laboratory refrigerator

## PPE Requirements

- Safety glasses
- Work clothes and safety shoes
- Disposable CAT3 suit (Tyvek)
- Mouth mask, gloves, hairnet

## Gaps

- Freeze dryer manufacturer and model number
- Shelf area and number of shelves per unit
- Condenser temperature specification
- Vacuum level during primary/secondary drying (mbar)
- Maximum batch weight (kg paste per load)
- Product moisture content specification (target % final moisture)
- Energy consumption per cycle
- Condenser defrost procedure and duration
