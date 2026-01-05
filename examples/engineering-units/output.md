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
$Q_{vol} := 50 \frac{m^{3}}{h}$

Convert to m³/s:
$Q_s := 0.0002777777778 Q_{vol} == 0.01388888889 \frac{\text{m}^{3}}{\text{hour}}$

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
$vel := \frac{Q_s}{A_{pipe}} == 5.555555556e-06 \frac{\text{m}^{3}}{\pi \cdot \text{hour} \cdot \text{mm}^{2}}$

---

## Step 2: Head Losses

### Static Head

Total static head:
$H_{static} := h_d - h_s == 17 \text{m}$

### Friction Head Loss

Using Darcy-Weisbach equation:

$$H_f := f_d \cdot \frac{L_{pipe}}{D_{pipe}} \cdot \frac{vel^2}{2 \cdot grav} ==
\\ \color{red}{\text{
    Error: Undefined variable(s): f\_\{d \textbackslash\{\}cdot\}}}$$

### Minor Losses

K-factor for fittings (dimensionless):
$K_{fit} := 5$

$$H_m := 0.5 \frac{K_{fit} \cdot \text{vel}^{2}}{\text{grav}} == 7.865493764e-12 \frac{\text{m}^{5} \cdot \text{s}^{2}}{\pi^{2} \cdot \text{hour}^{2} \cdot \text{mm}^{4}}$$

---

## Step 3: Total Dynamic Head (TDH)

$$TDH := H_{static} + H_f + H_m ==
\\ \color{red}{\text{
    Error: Undefined variable(s): H\_f}}$$

---

## Step 4: Hydraulic Power

Hydraulic power:
$$P_{hyd} := D \cdot H \cdot Q_s \cdot T \cdot \text{grav} \cdot \rho == 136.25 \frac{\text{dioptre} \cdot \text{H} \cdot \text{kg} \cdot \text{m} \cdot \text{T}}{\text{hour} \cdot \text{s}^{2}}$$

---

## Step 5: Motor Sizing

Pump efficiency (assumed, dimensionless):
$eta_p := 0.75$

Motor efficiency (assumed, dimensionless):
$eta_m := 0.9$

Required motor power:
$$P_{motor} := \frac{P_{hyd}}{\eta_m \cdot \eta_p} == 201.8518519 \frac{\text{dioptre} \cdot \text{H} \cdot \text{kg} \cdot \text{m} \cdot \text{T}}{\text{hour} \cdot \text{s}^{2}}$$

---

## Results Summary

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Flow rate | $Q_{vol}$ | 50 | m³/h |
| Flow velocity | $vel$ | calculated | m/s |
| Static head | $H_{static}$ | calculated | m |
| Friction loss | $H_f$ | calculated | m |
| Total head | $TDH$ | calculated | m |
| Hydraulic power | $P_{hyd}$ | calculated | W |
| Motor power | $P_{motor}$ | calculated | W |

---

## Design Notes

1. **Safety margin**: Add 10-20% to calculated motor power
2. **NPSH**: Check Net Positive Suction Head requirements
3. **Pump curve**: Select pump with operating point on efficient part of curve

---

> *livemathtex: 2026-01-05 01:17:04 | 20 definitions, 9 evaluations | 2 errors | 0.53s* <!-- livemathtex-meta -->
