# Pump Sizing Calculation (with Units)

This example demonstrates a complete engineering calculation **with SI units** for sizing a centrifugal pump.

![Centrifugal Pump System](images/pump_system.svg)

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

Volume flow rate:
$Q := 50 \frac{m^{3}}{h}$

Display in different units (no manual conversion needed!):
$Q == 50 \frac{\text{m}^{3}}{\text{hour}}$ <!-- [m³/h] -->
$Q == 0.01389 \frac{\text{m}^{3}}{\text{s}}$ <!-- [m³/s] -->
$Q == 13.89 \frac{\text{l}}{\text{s}}$ <!-- [L/s] -->

### Geometry

Suction head (negative = below pump):
$h_s := -2 m$

Discharge head:
$h_d := 15 m$

Pipe length:
$L_{pipe} := 100 m$

Pipe diameter:
$D_{pipe} := 100 \text{mm}$

### Fluid Properties

Water density:
$rho := 1000 \frac{\text{kg}}{m^{3}}$

Gravitational acceleration:
$grav := 9.81 \frac{m}{s^{2}}$

### Friction Parameters

Darcy friction factor (dimensionless):
$f_d := 0.02$

---

## Step 1: Flow Velocity

Cross-sectional area:
$A_{pipe} := 0.25 \pi \cdot D_{pipe}^{2} == 2500 \pi \cdot \text{mm}^{2}$

Flow velocity:
$vel := \frac{Q}{A_{pipe}} == 0.02 \frac{\text{m}^{3}}{\pi \cdot \text{hour} \cdot \text{mm}^{2}}$

---

## Step 2: Head Losses

### Static Head

Total static head:
$H_{static} := h_d - h_s == 17 \text{m}$

### Friction Head Loss

Using Darcy-Weisbach equation:

$$H_f := 0.5 \frac{L_{pipe} \cdot \text{vel}^{2} \cdot f_d}{D_{pipe} \cdot \text{grav}} == 4.077e-07 \frac{\text{m}^{6} \cdot \text{s}^{2}}{\pi^{2} \cdot \text{hour}^{2} \cdot \text{mm}^{5}}$$

### Minor Losses

K-factor for fittings (dimensionless):
$K_{fit} := 5$

$$H_m := 0.5 \frac{K_{fit} \cdot \text{vel}^{2}}{\text{grav}} == 0.0001019 \frac{\text{m}^{5} \cdot \text{s}^{2}}{\pi^{2} \cdot \text{hour}^{2} \cdot \text{mm}^{4}}$$

---

## Step 3: Total Dynamic Head (TDH)

$$TDH := H_f + H_m + H_{static} == 17 \cdot \text{m} + \frac{\text{m}^{6} \cdot \text{s}^{2}}{2452500 \cdot \pi^{2} \cdot \text{hour}^{2} \cdot \text{mm}^{5}} + \frac{\text{m}^{5} \cdot \text{s}^{2}}{9810 \cdot \pi^{2} \cdot \text{hour}^{2} \cdot \text{mm}^{4}}$$

---

## Step 4: Hydraulic Power

Hydraulic power:
$$P_{hyd} := Q \cdot \text{TDH} \cdot \text{grav} \cdot \rho == 136.2 \frac{\left(\frac{3125000 \cdot \text{m}}{79461 \cdot \pi^{2}} + 17 \cdot \text{m}\right) \cdot \text{kg} \cdot \text{m}^{2}}{\text{s}^{3}}$$ <!-- [kW] -->

---

## Step 5: Motor Sizing

Pump efficiency (assumed, dimensionless):
$eta_p := 0.75$

Motor efficiency (assumed, dimensionless):
$eta_m := 0.9$

Required motor power:
$$P_{motor} := \frac{P_{hyd}}{\eta_m \cdot \eta_p} == 201.9 \frac{\left(\frac{3125000 \cdot \text{m}}{79461 \cdot \pi^{2}} + 17 \cdot \text{m}\right) \cdot \text{kg} \cdot \text{m}^{2}}{\text{s}^{3}}$$ <!-- [kW] -->

---

## Results Summary

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Flow rate | $Q$ | 50 | m³/h |
| Flow velocity | $vel$ | calculated | m/s |
| Static head | $H_{static}$ | calculated | m |
| Friction loss | $H_f$ | calculated | m |
| Total head | $TDH$ | calculated | m |
| Hydraulic power | $P_{hyd}$ | calculated | W |
| Motor power | $P_{motor}$ | calculated | kW |

---

## Design Notes

1. **Safety margin**: Add 10-20% to calculated motor power
2. **NPSH**: Check Net Positive Suction Head requirements
3. **Pump curve**: Select pump with operating point on efficient part of curve

---

> *livemathtex: 2026-01-05 02:02:36 | 19 definitions, 11 evaluations | no errors | 0.64s* <!-- livemathtex-meta -->
