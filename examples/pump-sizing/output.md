# Pump Sizing Calculation

This example demonstrates a complete engineering calculation with **SI units** for sizing a centrifugal pump.

## Problem Statement

Design a pump system to transfer water from a storage tank to an elevated process vessel.

**Given:**
- Flow rate required: 50 m³/h
- Suction head: 2 m (below pump)
- Discharge head: 15 m (above pump)
- Pipe length: 100 m
- Pipe diameter: 100 mm
- Water density: 1000 kg/m³
- Friction factor: 0.02

**Find:** Required pump head, hydraulic power, and motor size.

---

## Input Data

### Flow Requirements
Volume flow rate (m³/h):
$Q_{vol} := 50$

Convert to m³/s:
$Q_s := 0.0002777777778 Q_{vol} == 0.01388888889$

### Geometry
Suction head (m, negative = below pump):
$h_s := -2$

Discharge head (m):
$h_d := 15$

Pipe length (m):
$L_{pipe} := 100$

Pipe diameter (m):
$D_{pipe} := 0.1$

### Fluid Properties
Water density (kg/m³):
$rho := 1000$

Gravitational acceleration (m/s²):
$grav := 9.81$

### Friction Parameters
Darcy friction factor:
$f := 0.02$

---

## Step 1: Flow Velocity

Cross-sectional area (m²):
$A_{pipe} := 0.25 \pi \cdot D_{pipe}^{2} == 0.007853981634$

Flow velocity (m/s):
$vel := \frac{Q_s}{A_{pipe}} == 1.768388257$

---

## Step 2: Head Losses

### Static Head
Total static head (m):
$H_{static} := h_d - h_s == 17$

### Friction Head Loss
Using Darcy-Weisbach equation:

$$H_f := 0.5 \frac{L_{pipe} \cdot \text{vel}^{2} \cdot f}{D_{pipe} \cdot \text{grav}} == 3.187764552$$

### Minor Losses
K-factor for fittings:
$K_{fit} := 5$

$$H_m := 0.5 \frac{K_{fit} \cdot \text{vel}^{2}}{\text{grav}} == 0.7969411381$$

---

## Step 3: Total Dynamic Head (TDH)

$$TDH := H_f + H_m + H_{static} == 20.98470569$$

---

## Step 4: Hydraulic Power

Hydraulic power (W):
$$P_{hyd} := Q_s \cdot \text{TDH} \cdot \text{grav} \cdot \rho == 2859.16615$$

Convert to kW:
$P_{kW} := 0.001 P_{hyd} == 2.85916615$

---

## Step 5: Motor Sizing

Pump efficiency (assumed):
$eta_p := 0.75$

Motor efficiency (assumed):
$eta_m := 0.9$

Required motor power (W):
$$P_{motor} := \frac{P_{hyd}}{\eta_m \cdot \eta_p} == 4235.801704$$

In kW:
$P_{motor,kW} := 0.001 P_{motor} == 4.235801704$

---

## Results Summary

| Parameter | Symbol | Calculated | Unit |
|-----------|--------|------------|------|
| Flow rate | Q_vol | 50 | m³/h |
| Flow velocity | vel | see above | m/s |
| Static head | H_static | see above | m |
| Friction loss | H_f | see above | m |
| Total head | TDH | see above | m |
| Hydraulic power | P_hyd | see above | W |
| Motor power | P_motor,kW | see above | kW |

---

## Design Notes

1. **Safety margin**: Add 10-20% to calculated motor power
2. **NPSH**: Check Net Positive Suction Head requirements
3. **Pump curve**: Select pump with operating point on efficient part of curve

---

> *livemathtex: 2026-01-05 01:03:27 | 22 definitions, 11 evaluations | no errors | 0.53s* <!-- livemathtex-meta -->
