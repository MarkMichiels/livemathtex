# Heat Exchanger Design Calculation

This example demonstrates a complete engineering calculation for sizing a **shell-and-tube heat exchanger** using the LMTD (Log Mean Temperature Difference) method.

![Shell-and-Tube Heat Exchanger](images/heat_exchanger.svg)

## Problem Statement

Design a counter-flow heat exchanger to cool hot process water using cold utility water.

**Given:**
- Hot fluid inlet temperature: 90°C
- Cold fluid inlet temperature: 20°C
- Hot fluid mass flow rate: 2.0 kg/s
- Cold fluid mass flow rate: 3.0 kg/s
- Required heat duty: 150 kW
- Overall heat transfer coefficient: 500 W/(m²·K)

**Find:** Heat transfer area, outlet temperatures, and effectiveness.

---

## Given Data

### Temperatures (°C)
$T_{h,in} := 90$
$T_{c,in} := 20$

### Mass Flow Rates (kg/s)
$m_h := 2.0$
$m_c := 3.0$

### Fluid Properties - Water
Specific heat capacity (J/kg·K):
$c_p := 4186$

### Heat Transfer Parameters
Heat duty (W):
$Q := 150000$

Overall heat transfer coefficient (W/m²·K):
$U := 500$

---

## Step 1: Outlet Temperatures

From energy balance: $Q = m \cdot c_p \cdot \Delta T$

### Hot Fluid
Temperature drop:
$\Delta T_h := \frac{Q}{m_h \cdot c_p} == 17.92$

Outlet temperature:
$T_{h,out} := T_{h,in} - \Delta T_h == 72.08$

### Cold Fluid
Temperature rise:
$\Delta T_c := \frac{Q}{m_c \cdot c_p} == 11.94$

Outlet temperature:
$T_{c,out} := T_{c,in} + \Delta T_c == 31.94$

---

## Step 2: Log Mean Temperature Difference (LMTD)

For counter-flow arrangement, temperature differences at each end:

$\Delta T_1 := T_{h,in} - T_{c,out} == 58.06$

$\Delta T_2 := T_{h,out} - T_{c,in} == 52.08$

LMTD calculation (using natural log):
$ratio := \frac{\Delta T_1}{\Delta T_2} == 1.115$

$$LMTD := \frac{\Delta T_1 - \Delta T_2}{\ln(ratio)} == 55.02$$

---

## Step 3: Required Heat Transfer Area

From heat exchanger equation: $Q = U \cdot A \cdot LMTD$

$$A := \frac{Q}{U \cdot LMTD} == 5.453$$

---

## Step 4: Effectiveness-NTU Analysis

### Heat Capacity Rates (W/K)
$C_h := m_h \cdot c_p == 8.372e3$

$C_c := m_c \cdot c_p == 12.56e3$

Since $C_h < C_c$:
$Cmin := C_h$
$Cmax := C_c$

### Heat Capacity Ratio
$C_r := \frac{Cmin}{Cmax} == 666.7e-3$

### Maximum Possible Heat Transfer (W)
$Qmax := Cmin \cdot (T_{h,in} - T_{c,in}) == 586.0e3$

### Effectiveness
$$\varepsilon := \frac{Q}{Qmax} == 256.0e-3$$

### Number of Transfer Units (NTU)
$$NTU := \frac{U \cdot A}{Cmin} == 325.7e-3$$

---

## Results Summary

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Heat transfer area | $A$ | $5.5$ <!-- value:A :2 --> | m² |
| Hot outlet temp | $T_{h,out}$ | $72$ <!-- value:T_{h,out} :1 --> | °C |
| Cold outlet temp | $T_{c,out}$ | $32$ <!-- value:T_{c,out} :1 --> | °C |
| LMTD | $LMTD$ | $55$ <!-- value:LMTD :2 --> | K |
| Effectiveness | $\varepsilon$ | $256e-3$ <!-- value:\varepsilon :3 --> | - |
| NTU | $NTU$ | $326e-3$ <!-- value:NTU :3 --> | - |

---

## Design Verification

Tube length (m):
$length := 2$

Area per meter:
$A_m := \frac{A}{length} == 2.727$

**Conclusion:** The design meets thermal requirements with calculated effectiveness.

---

> *livemathtex: 2026-01-07 01:51:01 | 26 definitions, 16 evaluations, 6 value refs | no errors | 0.41s* <!-- livemathtex-meta -->
