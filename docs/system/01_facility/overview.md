# Facility Overview

## Location and Layout

The axabio production facility is housed in a single industrial hall originally built for microalgae cultivation. The hall measures approximately **34 x 34 m** with a ridge height of approximately **7 m**, providing sufficient clearance for two-level reactor racks and overhead crane operations.

The facility is divided into four quadrants, each approximately **17 x 17 m**:

| Quadrant | Position | Function |
|----------|----------|----------|
| **Right-rear** | Back-right | Active production: MPC11-MPC16 reactor racks |
| **Left-rear** | Back-left | Expansion area: MPC21-MPC26 (new units) |
| **Right-front** | Front-right | Pre/post-processing: CFU and CHU in stacked 40 ft containers |
| **Left-front** | Front-left | Storage: raw materials, spare reactor foils, parts, tools |

Three structural columns run in a row through the hall, supporting the roof structure and dividing the space logistically.

![ProviAPT Facility Overview](../images/facility_overview.svg)
*Material flow through the ProviAPT production facility.*

## Production Units

The facility operates an automated photobioreactor system based on the Micro ProviAPT Controller (MPC) architecture. Each MPC controls up to 16 thin-film reactors arranged in two independent headers.

| Unit | Name | Function |
|------|------|----------|
| **MPC11-MPC16** | Production controllers (existing) | 6 MPCs, up to 96 reactors |
| **MPC21-MPC26** | Production controllers (expansion) | 6 MPCs, up to 96 reactors |
| **CFU** | Central Feed Unit | Nutrient preparation and sterilization |
| **CHU** | Central Harvest Unit | Centrifugation and biomass concentration |
| **HBU** | Harvest Biomass Unit | Buffer tanks (T1-T5) for harvested biomass |
| **CWU** | Cooling Water Unit | Temperature control via closed chiller circuit |
| **WWU** | Waste Water Unit | pH correction and waste disposal |
| **FDU** | Freeze Drying Unit | Biomass drying (LYO1, LYO2) before packaging |

### Total Capacity (12 MPCs at full build-out)

| Parameter | Value |
|-----------|-------|
| Total MPCs | 12 |
| Reactors per MPC | 16 (2 headers x 8 reactors) |
| Total reactors | 192 |
| Volume per reactor | 197 L |
| Total culture volume | 37,824 L |

## Pilot Plant

A smaller-scale facility with individual reactors (designated C1, C2, C3, etc.) used for R&D trials. Pilot reactors use 25-panel reactor foils (versus 35-panel for indoor production) and are used to test new process parameters, strains, or cascade configurations before scaling to the main production units.

## Laboratory

Flask-scale cultures maintained as backup inocula and for experimental work. The lab includes:

- Microscopy for visual inspection (contamination detection, cell stage identification)
- Sample refrigeration for batch analysis
- Connections to external analysis (ECCA) for fat, protein, ash, moisture, and microbiology

## Reactor Machine Area

A dedicated area within the facility housing the custom-designed reactor production machine and the tube welding station. The reactor machine produces the disposable thin-film photobioreactor foils used across all MPC units. See [Reactor Machine](../07_reactor_machine/machine.md) for details.

## Warehouse and Storage

The front-left quadrant serves as central storage for:

- Plastic film rolls (A, B, C, E) for reactor production
- IBC containers (1000 L) for feed medium
- Spare parts, tools, and maintenance equipment
- Chemical stocks (cleaning agents, nutrients)

Raw materials are received through the main entrance at the front of the hall. The logistics flow runs front-to-back: incoming materials and storage in the front quadrants, active production and cultivation in the rear quadrants.

## Workflow

```
Materials intake (front) → CFU: medium preparation (right-front containers)
                         → Reactor machine: foil production
                         → MPC racks: cultivation (rear quadrants)
                         → CHU: harvest and concentration (right-front containers)
                         → FDU: freeze drying
                         → Packaging and storage
```

## Gaps

- Exact building address and GPS coordinates
- Utility connections (water, power, gas supply ratings)
- HVAC system specifications for the production hall
- Fire safety and emergency systems documentation
- Outdoor equipment locations (cooling tower, waste water discharge point)
