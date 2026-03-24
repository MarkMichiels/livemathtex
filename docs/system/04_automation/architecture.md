# Automation Architecture

## Overview

The facility automation is built on a three-layer architecture connecting field-level sensors and actuators through local controllers to a central SCADA system.

## Three-Layer Model

| Layer | Function | Components |
|-------|----------|------------|
| **Field level** | Sensing and actuation | Sensors, valves, pumps, LEDs |
| **Control level** | Local logic and regulation | MPC controllers (Arduino-based) |
| **Supervision level** | Monitoring and orchestration | OpenSCADA server |

## Controller Hierarchy

![Control System Hierarchy](../images/controller_hierarchy.svg)
*Hardware hierarchy from SCADA server to field-level controllers.*

The control system follows a hierarchical structure from the central SCADA server down to individual field devices:

- **SCADA Server** — Central OpenSCADA instance managing all controllers
- **MPC Controllers** — Arduino-based units each managing up to 16 reactors
- **Support Units** — CFU, CHU, CWU, WWU controllers for shared infrastructure
- **Field Devices** — Individual sensors and actuators connected to controller I/O

## Communication

| Link | Protocol | Medium |
|------|----------|--------|
| SCADA to MPC | Modbus TCP | Ethernet |
| MPC to sensors | Analog/Digital I/O | Wired |
| MPC to actuators | Digital I/O / PWM | Wired |

## Gaps

- Network topology diagram
- IP address allocation scheme
- Failover and redundancy provisions
- Data logging and historian configuration
- Remote access and VPN setup
