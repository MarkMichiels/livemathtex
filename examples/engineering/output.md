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
$m_h := 2$
$m_c := 3$

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
$\Delta T_h := \frac{Q}{c_p \cdot m_h} == 17.91686574$

Outlet temperature:
$T_{h,out} := T_{h,in} - \text{Delta_T_h} == 72.08313426$

### Cold Fluid
Temperature rise:
$\Delta T_c := \frac{Q}{c_p \cdot m_c} == 11.94457716$

Outlet temperature:
$T_{c,out} := T_{c,in} + \text{Delta_T_c} == 31.94457716$

---

## Step 2: Log Mean Temperature Difference (LMTD)

For counter-flow arrangement, temperature differences at each end:

$\Delta T_1 := - T_{c,out} + T_{h,in} == 58.05542284$

$\Delta T_2 := - T_{c,in} + T_{h,out} == 52.08313426$

LMTD calculation (using natural log):
$ratio := \frac{\text{Delta_T_1}}{\text{Delta_T_2}} == 1.114668379$

$$LMTD := \frac{\text{Delta_T_1} - \text{Delta_T_2}}{\log{\left(\text{ratio} \right)}} == 55.01526137$$

---

## Step 3: Required Heat Transfer Area

From heat exchanger equation: $Q = U \cdot A \cdot LMTD$

$$A := \frac{Q}{U \cdot \text{LMTD}} == 5.45303235$$

---

## Step 4: Effectiveness-NTU Analysis

### Heat Capacity Rates (W/K)
$C_h := c_p \cdot m_h == 8372$

$C_c := c_p \cdot m_c == 12558$

Since $C_h < C_c$:
$Cmin := C_h$
$Cmax := C_c$

### Heat Capacity Ratio
$C_r := \frac{\text{Cmin}}{\text{Cmax}} == 0.6666666667$

### Maximum Possible Heat Transfer (W)
$Qmax := \text{Cmin} \cdot \left(- T_{c,in} + T_{h,in}\right) == 586040$

### Effectiveness
$$\varepsilon := \frac{Q}{\text{Qmax}} == 0.2559552249$$

### Number of Transfer Units (NTU)
$$NTU := \frac{A \cdot U}{\text{Cmin}} == 0.3256708283$$

---

## Results Summary

| Parameter | Value | Unit |
|-----------|-------|------|
| Heat transfer area (A) | see calculation | m² |
| Hot outlet temp | $T_{h,out}$ | °C |
| Cold outlet temp | $T_{c,out}$ | °C |
| LMTD | see calculation | K |
| Effectiveness (ε) | see calculation | - |
| NTU | see calculation | - |

---

## Design Verification

Tube length (m):
$length := 2$

Area per meter:
$A_m := \frac{A}{\text{length}} == 2.726516175$

**Conclusion:** The design meets thermal requirements with calculated effectiveness.

---

> *livemathtex: 2026-01-04 23:13:26 | 26 definitions, 16 evaluations | no errors | 0.50s* <!-- livemathtex-meta -->
