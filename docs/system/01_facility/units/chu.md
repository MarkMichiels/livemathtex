# Central Harvest Unit (CHU)

## Overview

The Central Harvest Unit manages the collection, concentration, and temporary storage of harvested algae biomass. It receives culture from the MPC reactors via harvest valves, buffers it in the HBU tanks, and processes it through a centrifuge (GEA separator) to produce concentrated paste.

## System Components

| ID | Component | Function |
|----|-----------|----------|
| **T1-T5** | HBU tanks | Harvest buffer — receive culture from reactor harvest valves (V8) |
| **T6** | Centrifuge feed tank | Level sensor controlled; common level sensor issues |
| **Centrifuge** | GEA separator | Concentrates biomass from liquid (centrate) |
| **T7-T9** | Cooled storage tanks | Store concentrated paste in cool room |

## Harvest Flow

```
Reactors (V8 harvest valve) -> HBU (T1-T5) -> T6 feed tank -> Centrifuge
                                                                  |
                                                    Centrate -> WWU
                                                    Paste -> T7/T8/T9 (cool room)
```

## Centrifuge (GEA Separator)

The centrifuge concentrates harvested culture from ~5-10 g/L to a paste of >100 g/L.

**Pre-operation checklist:**
- Check tubes are clean
- Verify storage tank (T7, T8, T9) cleanliness in cool room
- Run CIP on centrifuge
- Manually start buffer

## Slurry Transfer to Freeze Dryer

Concentrated paste is transferred from T7/T8/T9 to the FDU using a transport container and pump:

1. Forklift the transport container to the CHU connection point
2. Clean strainer and connection hardware
3. Run the "Slurry Empty" program for the selected tank
4. Record liters transferred
5. Update product type and batch number in the SCADA external menu
6. Press "Report and Adjust level now" to log the batch
7. Run CIP for the emptied tank

### Batch Numbering

Format: `AAA-YYYYMMDD-BBB`
- AAA = algae number (e.g., 092 for Haematococcus Lacustris/Pluvialis)
- YYYYMMDD = date
- BBB = sequential batch number

## Typical Metrics

| Metric | Value |
|--------|-------|
| Green phase culture density | 5-10 g/L |
| Stress phase culture density | >10 g/L target |
| Paste concentration (after centrifuge) | >100 g/L |

## Gaps

- GEA centrifuge model number and detailed specifications (RPM, bowl capacity, throughput)
- CIP procedure details for the centrifuge
- HBU tank capacities (T1-T5)
- T6 feed tank capacity and level sensor specifications
- Cool room temperature setpoint
- Centrate composition and disposal method
