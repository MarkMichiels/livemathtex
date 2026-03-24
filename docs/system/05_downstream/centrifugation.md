# Centrifugation

## Overview

Centrifugation is the primary biomass concentration step in the downstream process. A GEA disc stack separator concentrates harvested culture from ~5-10 g/L to a paste exceeding 100 g/L, separating the biomass from the liquid centrate.

![Downstream Processing Flow](../images/downstream_flow.svg)
*Post-harvest processing: separation, drying, and packaging.*

## Equipment

The facility uses a GEA disc stack centrifuge (separator) as the core concentration device.

| Parameter | Value |
|-----------|-------|
| Manufacturer | GEA |
| Type | Disc stack separator |
| Input concentration | 5-10 g/L (typical harvest density) |
| Output concentration | >100 g/L (concentrated paste) |

**Note:** Detailed GEA model number, RPM, bowl capacity, and throughput specifications are not yet documented (see Gaps).

## Process Flow

```
HBU tanks (T1-T5) -> T6 centrifuge feed tank -> GEA Separator
                                                     |
                                       Paste -> T7/T8/T9 (cooled storage)
                                       Centrate -> WWU (waste water)
```

### Feed System

The centrifuge is fed from tank T6, which receives culture from the HBU buffer tanks (T1-T5). T6 is equipped with a level sensor for automated feed control, though level sensor issues are a known recurring problem.

### Output Handling

- **Paste:** Concentrated biomass is collected in cooled storage tanks T7, T8, or T9 located in the cool room
- **Centrate:** The clarified liquid (supernatant) is routed to the WWU for pH correction and disposal

## CIP Procedure

Clean-In-Place is performed on the centrifuge before and between batches:

1. Check tubes are clean
2. Verify storage tank cleanliness (T7, T8, T9) in the cool room
3. Run CIP program on the centrifuge
4. Manually start buffer system

The CIP uses standard cleaning agents (P3 Oxonia, Javel/bleach). Detailed CIP steps and chemical concentrations for the centrifuge are documented in the operational SOP.

## Quality Targets

| Metric | Target |
|--------|--------|
| Paste concentration | >100 g/L |
| Astaxanthin content (Haematococcus) | 5% of dry weight |
| Visual inspection | No contamination, correct cell stage |

## Common Issues

| Issue | Description |
|-------|-------------|
| T6 level sensor malfunction | Feed tank level reading errors; causes under/overfeed |
| Incomplete separation | Paste too dilute; may indicate worn discs or incorrect feed rate |
| Foaming | Excess foam from reactor harvest can affect separator performance |

## Gaps

- GEA separator model number (e.g., GEA Westfalia CSE/CSI series)
- Bowl capacity (liters)
- Operating RPM
- Maximum throughput (L/h)
- G-force specification
- Disc count and material
- Motor power (kW)
- CIP chemical concentrations and cycle duration
- Maintenance intervals (disc cleaning, gasket replacement)
- Centrate quality specifications (target turbidity/OD)
