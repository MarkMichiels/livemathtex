# Reactor Machine

## Overview

The reactor machine is a custom-designed, one-of-a-kind system that produces the disposable thin-film photobioreactor foils used in all MPC units. Originally designed by a carpet manufacturer, it is the only machine of its kind in the world. It produces three types of reactors:

| Type | Panels | Use |
|------|--------|-----|
| Single-panel | 1 | Laboratory testing |
| 25-panel | 25 | Pilot testing |
| 35-panel | 35 | Indoor production |

A 35-panel reactor takes approximately **80-100 minutes** to produce.

## Machine Components

![Reactor Machine Production Stations](../images/reactor_machine_stations.svg)
*Foil progression through the four machine stations.*

The machine consists of four main station groupings:

### 1. Laser Station

- CO2 laser for cutting holes in the reactor foil
- Adjustable focus via lens height adjustment (markings -10 to +10)
- Hole size verified by test shots on 5x5 cm white foil samples (2-4 second pulses)
- Laser cover ("laserkap") must be removed for maintenance
- **Laser safety glasses are mandatory** (stored on rack inside machine area)

### 2. Camera System

- **Camera 1:** Dual camera (left and right) for position detection
- **Camera 2:** Secondary camera for stamp alignment verification
- Software: wBS40 (on left desktop computer) for troubleshooting
- Camera positions must never be touched or moved — positioning is critical
- Camera 2 viewing angle may need adjustment for temperature-related foil drift

### 3. Stamp System

- **Stamp 1:** Creates panel welds (square block pattern)
- **Stamp 2:** Seals layers together (thin rod impression, must center on Stamp 1 block)
- Quality check: Stamp 2 weld pattern must be symmetrical relative to panel center fold

### 4. Cutting and Collection

After 39 positions (35 panels + 4 empty leader/trailer), the machine automatically cuts and rolls the finished reactor into a collection bin.

## Plastic Rolls

The machine uses 4 rolls of unique plastic film, each with different layers and melting points calculated for specific welding operations. **Incorrect roll placement makes all reactors unusable.**

| Roll | Code | Material | Function |
|------|------|----------|----------|
| **A** | CSMEO491 01 | Transparent | Forms reactor panels (highest consumption) |
| **B** | CSMEO264 01 | Non-transparent ("kettingfolie") | Top layer of reactor |
| **C** | CSMEO266 01 | Transparent | Feed and air/CO2 tubing (between top and middle layers) |
| **E** | CSMEO263 01 | Transparent | Pneumatic layer tubing (between middle and bottom layers) |

- Rolls can weigh **over 200 kg** when new — forklift required for handling
- Roll A is replaced most frequently (uses ~1 m extra per panel for panel formation)
- Two overhead cranes (yellow remote control) assist with roll changes
- Roll stock is stored in the indoor production area

### Roll Structure in the Reactor

The reactor consists of three layers creating two chambers:
1. **Top layer** (Roll B, non-transparent) + **Middle layer** = Feed/air chamber (Roll C tubing)
2. **Middle layer** + **Bottom layer** = Pneumatic chamber (Roll E tubing)
3. **Panels** (Roll A) = Reactor cultivation chambers

## Console and Controls

| Control | Function |
|---------|----------|
| Green "Start Cycle" | Starts single panel cycle |
| Red "Stop Cycle" | Emergency cycle stop — cancels current cycle, reactors become unusable |
| Black "Pause Cycle" | Pauses after current sub-task completes, cycle can be resumed safely |
| Blue "Set Safety Controls" | Must be pressed after gate has been opened/closed |
| "MAN AUTO" button | Switches between manual and automatic mode |
| Emergency button | Instantly stops all moving parts |
| White button (near gate) | Request access — wait until solid white before entering |

### Machine Access Protocol

1. Turn off automatic cycle or press "Pause Cycle"
2. Wait for current cycle to complete (2-3 minutes, machine beeps when safe)
3. Press white button near gate, wait until solid white
4. Enter through gate — do not close gate behind you
5. On exit: close gate securely, press blue "Set Safety Controls" button

## Production Speed

| Parameter | Value |
|-----------|-------|
| Cycle time per panel | ~2-3 minutes |
| 35-panel reactor production time | ~80-100 minutes |
| Positions per reactor | 39 (35 panels + 4 leader/trailer) |

## Post-Production: Tube Welding

After production, each reactor requires tube welding using a separate tube welding machine:

### Tube Welding Machine Specifications

| Parameter | Value |
|-----------|-------|
| Welding temperature | 160 degC (3 active heating zones) |
| Warm-up time | ~10 minutes |
| Pressure requirement | >1 bar (ideally 1.05-1.1 bar) |
| Active stamps | 3 (left, middle, right) out of 5 total |

### Welding Process

1. **Pneumatic side:** Insert 3 tubes between bottom and middle layers (both transparent)
2. **Feed side:** Insert 3 tubes between top layer (white) and middle layer (transparent)
3. Apply small amount of white PE powder between layers for insertion (too much weakens weld, none risks tearing)
4. Press and hold dual start buttons until stamps fully descend (~30 seconds)
5. Pull back metal rods immediately when stamps release (prevents deformation/sticking)
6. Wait for air blower cooling to complete
7. Insert red end caps on feed side tubes (contamination prevention + visual indicator)

### Materials

- Welding tubes
- White PE powder (lubrication)
- Red end caps (feed side identification)
- Sticker labels (reactor ID, placed on pneumatic side)

## Logging and Inventory

| System | Purpose |
|--------|---------|
| ReactorLasMachine-logging.xlsm | Real-time event logging (right desktop computer) |
| inventory reactors (Google Sheets) | Finished reactor tracking (panels, laser time, defects) |

All events, errors, and manual interventions must be logged. Defective reactors are marked "bad" in the inventory sheet immediately upon detection.

## Safety Notes

- Machine operates with high forces — exercise extreme caution
- Never touch foil surfaces where welding occurs (hand grease prevents proper seals)
- Always wear gloves when handling film and tubes
- Tube welding machine reaches 160 degC — severe burn hazard
- Incorrect tube placement between wrong layers makes entire reactor unusable
- Two-person operation required for laser focusing procedures

## Gaps

- Laser type and power (CO2 laser wattage)
- Laser beam diameter at focus point
- Machine overall dimensions (L x W x H)
- Machine weight
- Electrical supply requirements (voltage, phase, amperage)
- Stamp pressure and temperature specifications per station
- Film thickness per roll (A, B, C, E)
- Roll width and standard roll length
- Annual reactor production volume
- Preventive maintenance schedule
