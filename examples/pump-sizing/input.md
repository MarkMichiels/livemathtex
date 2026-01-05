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
$Q_s := \frac{Q_{vol}}{3600} ==$

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
$A_{pipe} := \frac{\pi \cdot D_{pipe}^2}{4} ==$

Flow velocity (m/s):
$vel := \frac{Q_s}{A_{pipe}} ==$

---

## Step 2: Head Losses

### Static Head
Total static head (m):
$H_{static} := h_d - h_s ==$

### Friction Head Loss
Using Darcy-Weisbach equation:

$$H_f := f \cdot \frac{L_{pipe}}{D_{pipe}} \cdot \frac{vel^2}{2 \cdot grav} ==$$

### Minor Losses
K-factor for fittings:
$K_{fit} := 5$

$$H_m := K_{fit} \cdot \frac{vel^2}{2 \cdot grav} ==$$

---

## Step 3: Total Dynamic Head (TDH)

$$TDH := H_{static} + H_f + H_m ==$$

---

## Step 4: Hydraulic Power

Hydraulic power (W):
$$P_{hyd} := rho \cdot grav \cdot Q_s \cdot TDH ==$$

Convert to kW:
$P_{kW} := \frac{P_{hyd}}{1000} ==$

---

## Step 5: Motor Sizing

Pump efficiency (assumed):
$eta_p := 0.75$

Motor efficiency (assumed):
$eta_m := 0.90$

Required motor power (W):
$$P_{motor} := \frac{P_{hyd}}{eta_p \cdot eta_m} ==$$

In kW:
$P_{motor,kW} := \frac{P_{motor}}{1000} ==$

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
