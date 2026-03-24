# Cooling Water Unit (CWU)

## Overview

The CWU provides temperature control for all photobioreactors in the facility. It uses a closed-circuit chiller system with propylene glycol coolant, distributing chilled water through a Tichelmann piping loop along the ceiling of the production hall walkway.

## Chiller Specifications

| Parameter | Value |
|-----------|-------|
| Chiller model | MTA TAEevo Tech 381 (DT110) |
| Cooling capacity | 100 kW (air-cooled) |
| Internal pump | P3 centrifugal, 4 kW |
| Buffer tank | 410 L |
| Coolant | 30% inhibited propylene glycol |
| Supply temperature | 7 degC (summer operation, adjustable 4-30 degC) |
| Anti-freeze setting | 4 degC (parameter AL26) |
| Minimum outlet (with 30% PG) | ~3 degC |
| Serial number | 2200312960 |

### Pump Characteristics (P3 - Standard)

| Parameter | Min flow | Max flow |
|-----------|----------|----------|
| Water flow rate | 7.2 m3/h | 36 m3/h |
| Pump pressure head | 3.5 bar | 1.9 bar |
| Rated power | 4 kW | 4 kW |

Centrifugal pump model: H = 3.57 - 0.001286 x Q2 (bar, m3/h)

An optional P5 pump upgrade (5.3-3.6 bar, 7.2-42 m3/h, 7.5 kW) is available if more head pressure is needed.

## Main Circulation Loop

| Parameter | Value |
|-----------|-------|
| Pipe material | Polyethylene (PE100 SDR11) |
| Nominal size | DN63 (OD 63 mm) |
| Wall thickness | 5.7 mm (SDR11) |
| Internal diameter | 51.6 mm |
| Supply run length | ~40 m (along ceiling) |
| Return run length | ~40 m (same route) |
| Total main loop | ~80 m |
| Bypass valve | DN25 PP pressure relief valve |
| Mounting | Against ceiling of walkway, above reactor row 4 |

The loop serves 48 lower green reactors (2 per header, 24 headers total across 12 MPCs). MPC 11-16 occupy ~17 m and MPC 21-26 (expansion) occupy ~17 m, totaling ~40 m with routing overhead.

## Branch Connections (Per Header)

Each header serves 2 reactors in parallel. Branches tap off the main DN63 loop via saddle clamps.

| Section | Length | Pipe | ID |
|---------|--------|------|-----|
| Saddle clamp to T-split (supply, vertical) | ~3 m | Push-in 12 mm nylon | ~10 mm |
| T-split to reactor (each) | ~0.5 m | Push-in 12 mm | ~10 mm |
| Reactor cooling channel | 7 m | Aluminum profile bore | 12 mm |
| Reactor back to merge point (return) | ~7 m + 0.5 m | Push-in 12 mm | ~10 mm |
| Merge to main loop return (vertical) | ~3 m | Push-in 12 mm | ~10 mm |
| **Total per header circuit** | **~28 m** | | |

## Control Components Per Reactor

| Component | Model | Specification |
|-----------|-------|--------------|
| Temperature sensor | DS18B20 | -55 to +125 degC, +/-0.5 degC, 1-Wire |
| Motorized ball valve | Acarps 2W 1/2" | 24 VDC, 3-wire, PTFE seal, 5-15 s |
| Flow sensor | Saier SEN-HZ21WA | 1-30 L/min, Hall effect |

### Control Strategy

Cascade PID control loop per reactor:

```
T_culture (setpoint) -> Temperature controller (outer loop)
                          -> Flow setpoint (L/min)
                               -> Flow controller (inner loop, SEN-HZ21WA feedback)
                                    -> Valve position (0-100%)
```

The motorized ball valve is proportional (not on/off) and holds position when de-energized.

## Temperature Setpoints

| Phase | Target Temperature |
|-------|--------------------|
| Green phase (growth) | 20-22 degC |
| Stress phase (astaxanthin) | 28-30 degC |

## Operating Points

| Scenario | Flow | Notes |
|----------|------|-------|
| Green phase demand | 8.3 m3/h | Lower cooling load |
| Full light demand | 16.4 m3/h | Maximum cooling required |
| Operating point (12 mm branches) | ~17 m3/h | Current configuration |
| Operating point (15 mm branches) | ~22 m3/h | Recommended upgrade (+30% flow) |

## Common Issues

- Top reactors tend to overheat due to LED heat rising
- Bottom reactors may overcool
- Temperature response has feedback lag (not immediate)
- Aluminum compatibility required for all wetted components (hence inhibited propylene glycol)

## Gaps

- Cooling tower specifications (if used for supplementary cooling)
- Glycol refill/maintenance schedule
- Total cooling load calculation at full 192-reactor operation
- Chiller placement location (indoor/outdoor)
- Expansion chiller plans for MPC21-MPC26
