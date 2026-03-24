# Micro ProviAPT Controller (MPC)

## Overview

The MPC is the core production unit of the axabio facility. Each MPC is a dual-header bioreactor system controlling up to 16 thin-film photobioreactors, organized as 2 independent headers of 8 reactors each.

## System Architecture

Each MPC contains:

- **Central U-shaped bioreactor** (main processing vessel)
- **Dual harvest/buffer tanks** (H1, H2) — separator vessel T1: 138 L (D 460 x 1040 mm, 155 mm lid)
- **Integrated gas management system** (CO2/O2 control via closed air loop)
- **Precision flow control** with extensive instrumentation
- **Siemens S7-1200 PLC** control system
- **PP Frame** as structural support

## Physical Specifications

| Parameter | Value |
|-----------|-------|
| Reactors per MPC | 16 (2 headers x 8) |
| Volume per reactor | ~197 L (35 panels x ~6 L/panel) |
| Reactor foil thickness | ~200-250 um |
| Reactor foil length | ~7 m |
| Reactor foil width | ~0.9 m |
| Inflated panel height | ~0.5 m |
| Panel spacing | 20 cm (for LED strips and accessories) |
| Rack arrangement | Two levels (floors), 4-8 reactors per level |
| Rack height | ~6 m total (two floors of ~3 m each) |

## Mounting and Frame

Reactors are mounted on two-level racks within the production hall. Each rack accommodates the two headers (H1, H2) with reactors arranged vertically. The PP (polypropylene) frame provides chemical-resistant structural support. Reactor foils hang vertically from the rack structure with panels inflated by the pneumatic system.

## Electrical Connections

| Connection | Specification |
|------------|--------------|
| Main electrical entry | 50 mm conduit |
| Compressed air | 8 mm push-in |
| PLC | Siemens S7-1200 CPU with expansion modules |
| Sensor power | 24 VDC |
| Blower K1 (membrane pump) | 166 L/min @ 120 mbar |
| Blower K2 (circulation) | 5 m3/min @ 85 mbar, with frequency drive (K2_FD) |
| Harvest pump P1 | Dedicated per MPC |

## Instrumentation Per MPC

| Sensor | ID | Type | Range |
|--------|----|------|-------|
| Reactor temperature | TT1 | RTD (LKM 224/1) | -30 to 70 degC |
| Cooling return temperature | TT2 | RTD (LKM 224/1) | -30 to 70 degC |
| Reactor outlet pressure | PT1 | Pressure transmitter | 0-250 mbar |
| Reactor inlet pressure | PT2 | Pressure transmitter | 0-500 mbar |
| Pneumatic pressure | PT4 | Pressure transmitter | 0-500 mbar |
| CO2 outlet | CO2out | Vaisala GMM220 (4-20 mA) | 0-10% |
| Harvest vessel level | LT1 | Pressure-based | 0-250 mbar |
| Level switch T1 max | LS1 | Float switch | 250 VAC / 120 VDC |

## Key Valves Per MPC

| Valve | Function | Specification |
|-------|----------|--------------|
| V1 | Bleed (O2 exhaust) | Solenoid, kv 1.52 m3/h, 10 mm orifice |
| V2 | CO2 dosing | Solenoid, kv 0.2 m3/h, 2 mm orifice |
| V4 | Cooling water control | Automatic, kv 28.9 m3/h, DN32 |
| V7 | Waste water outlet | Automatic, kv 28.9 m3/h, DN32 |
| V8 | Harvest outlet | Automatic, kv 28.9 m3/h, DN32 |
| V9 | Ozone inlet | Automatic, kv 7.5 m3/h, DN20 |
| H1V2/H2V2 | Feed pneumatic per header | Solenoid, kv 0.21 m3/h |
| H1V3/H2V3 | Aeration pneumatic per header | Solenoid, kv 0.32 m3/h |
| H1V4/H2V4 | Outlet pneumatic per header | Solenoid, kv 0.21 m3/h |
| H1V5/H2V5 | Maintenance per header | kv 2.85 m3/h, 12 mm orifice |

## Filtration

| Filter | Function | Specification |
|--------|----------|--------------|
| F1 | Air inlet filter | LT10-BV-RS, 2x NPTF 3/4" |
| F2 | Air inlet microfilter | Pall, 1500 cm2, 2x 13 mm hose barb |
| F3 | Feed inlet microfilter | Pall, 1500 cm2, 2x 13 mm hose barb |

Filtration chain: Cord filter -> Membrane filter -> Sterile filter (0.02 um)

## Reactor Addressing

Reactors are addressed as `MPC11:H1R3` = MPC 11, Header 1, Reactor 3.

## Production Units Assignment

| Unit | Species | Notes |
|------|---------|-------|
| MPC11-MPC12 | *Nannochloropsis* | Up to 16 reactors each |
| MPC13-MPC14 | *Haematococcus* cascade | Experimental setups |
| MPC15-MPC16 | Flexible | Either species |
| MPC21-MPC26 | Expansion | Under construction (contractor: Kuning) |

## Gaps

- Total weight per MPC unit (frame + equipment, dry/operational)
- Physical dimensions of the complete MPC assembly (L x W x H)
- Power consumption per MPC (total electrical load in kW)
- LED power supply (PSU) specifications per MPC (240W DC output per PSU mentioned in capacity model)
