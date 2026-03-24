# Reactor Machine Quality Control

## Overview

Quality control for reactor production encompasses hourly in-process inspections during machine operation, post-production visual checks, and tube welding verification. Defective reactors are immediately flagged to prevent use in production.

## Hourly Quality Checks (During Production)

These checks are performed approximately every hour per SOP-TEC-07:

1. Turn off automatic cycle, wait for machine to stop (2-3 minutes)
2. Enter machine area following safety protocol
3. Perform inspections at three locations:

### At the Balancing Roller

| Check | Criteria |
|-------|----------|
| Panel opening gap | ~2 mm open (not >1 cm, not welded shut) |
| Laser hole placement | All holes within the non-welded "eye" of the panel, not in the stamped/sealed area |
| Trident alignment (regulated side) | Large opening correctly positioned on panel |
| Trident alignment (unregulated side) | Main hole falls within the non-welded "eye" (alignment may be imperfect) |

### At Stamp 2

| Check | Criteria |
|-------|----------|
| Stamp alignment | Stamp 2 rod impression centered in the Stamp 1 square block |
| Layer sealing (left) | All plastic layers sealed within side weld, 2-3 mm margin, no layers askew |
| Layer sealing (right) | Same as left side |

### On the Inspection Table (Rear of Machine)

| Check | Criteria |
|-------|----------|
| Stamp 2 symmetry | Weld pattern symmetrical relative to panel center fold, equal spacing on both sides |

## Stamp 2 Symmetry Correction

If the Stamp 2 pattern is not symmetrical, the root cause is typically Camera 2 positional drift due to temperature effects on the foil. Correction involves adjusting Camera 2's viewing angle to compensate for the changed foil position.

## Tube Welding Quality

Quality checks during and after the tube welding process (SOP-TEC-08):

### Pre-Weld Checks

| Check | Criteria |
|-------|----------|
| Machine temperature | All 3 active zones at 160 degC |
| Stamp pressure | >1 bar on all manometers (ideally 1.05-1.1 bar) |
| Metal rods | Pushed fully forward, visible from front of stamp |

### During Welding

| Check | Criteria |
|-------|----------|
| Layer identification | Pneumatic: tubes between bottom + middle (both transparent). Feed: tubes between top (white) + middle (transparent) |
| Tube insertion depth | Past the circular weld "eyes", approximately "two fingers" visible outside |
| PE powder usage | Minimal amount — too much weakens weld, none risks tearing |
| Button hold duration | Held until stamps fully descend |
| Rod retraction | Rods pulled back immediately when stamps release |

### Post-Weld Checks

| Check | Criteria |
|-------|----------|
| Weld integrity | No visible gaps, tears, or deformation around tube entry points |
| Red end caps | Installed on all 3 feed-side tubes |
| Sticker label | Reactor ID sticker on pneumatic side |

## Common Defects and Causes

| Defect | Cause | Severity |
|--------|-------|----------|
| Weld leaks at tube | Pressure too low (<1 bar) during welding | Reactor may be unusable |
| Failed weld (stamps retract) | Start buttons released before stamps fully descended | Retry possible |
| Deformed weld / stuck rods | Metal rods not retracted quickly enough after stamp release | Reactor may be unusable |
| Weak weld | Excessive PE powder used | Reactor may leak in operation |
| Torn reactor plastic | Too much force during tube insertion without PE powder | Reactor unusable |
| Wrong layer placement | Tubes between incorrect plastic layers | **Reactor unusable (critical error)** |
| Panel opening too large (>1 cm) | Stamping misalignment or foil tension issue | Reactor unusable |
| Laser holes outside "eye" | Laser positioning drift | Reactor unusable |
| Asymmetric Stamp 2 pattern | Camera 2 drift due to temperature | Correct camera, check affected reactors |
| Layers unsealed in side weld | Stamp wear or misalignment | Reactor may leak |

## Documentation

| Record | Location | Content |
|--------|----------|---------|
| Event log | ReactorLasMachine-logging.xlsm (right desktop) | All events, errors, interventions |
| Reactor inventory | Google Sheets (inventory reactors) | Panel count, laser time, defect flags |
| Defective reactor marking | Google Sheets | Marked "bad" immediately upon detection |

**Rule:** If a reactor is identified as defective during inspection, let the machine finish producing it to maintain operational rhythm. Mark it "bad" in the inventory immediately.

## Inspection Frequency

| Inspection Type | Frequency |
|-----------------|-----------|
| In-process quality checks | Every ~1 hour |
| Tube welding verification | Every reactor |
| Laser focus optimization | After alignment changes or maintenance |

## Gaps

- Acceptance criteria tolerances (exact mm specifications for panel gap, margin widths)
- Leak test procedure for finished reactors (if any — pre-installation pressure test)
- Statistical quality tracking (defect rate, yield percentage)
- Corrective action procedures for recurring defects
- Incoming material inspection for plastic rolls (thickness verification, surface quality)
- Finished reactor storage conditions and shelf life before use
