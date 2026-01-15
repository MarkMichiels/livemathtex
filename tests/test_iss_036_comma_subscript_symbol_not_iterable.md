<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-036: Variables with commas in subscripts fail with "argument of type 'Symbol' is not iterable"

**IMPORTANT:** This test case reproduces the bug by including the full context from the original document (lines 1-490). The bug is **context-dependent** - simple test cases with just the failing expression work correctly, but when many variables (especially those with commas) are defined earlier in the document, the bug manifests.

**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md` (line 482)

**Expected:** Variables with commas in subscripts should parse and evaluate correctly (as ISS-034 claimed to fix).

**Actual:** Parsing fails with "argument of type 'Symbol' is not iterable" error when defining `PPE_{eff,9010}` using an expression containing `PPE_{red,raw}` and `PPE_{blue,raw}` (all have commas in subscripts).

---

![MPC System Overview](images/system_overview.svg)

The axabio production facility consists of 12 Multi-Panel Cascade (MPC) units:

$N_{MPC} := 12$
$N_{hdr} := 2$
$N_{rct} := 8$

**Total reactors:**

$N_{tot} := N_{MPC} \cdot N_{hdr} \cdot N_{rct} == 192$

### 1.3 Reactor Volume

After the 2027 upgrade, all reactors use the new panel design:

$V_{rct} := 197\ L$

**Total culture volume:**

$V_{tot} := N_{tot} \cdot V_{rct} == 37\,824\ \text{L}$ <!-- [L] -->

### 1.4 Reactor Geometry: Surface-to-Volume Ratio

The culture flows through cylindrical tube channels formed by welded PP foil:

$d_{weld} := 38\ mm$

When inflated, the channel forms a cylinder with circumference = 2 × weld spacing:

$d_{tube} := \frac{2 \cdot d_{weld}}{\pi} == 24.1916\ \text{mm}$ <!-- [mm] -->

**S/V ratio for cylindrical geometry** (S/V = 4/d for cylinder):

$SV := \frac{4}{d_{tube}} == 165.347\ \text{1/m}$ <!-- [1/m] -->

This is significantly higher than Algreen's pilot reactors (S/V = 40-80 m⁻¹), which is favorable for light distribution.

---

## 2. LED Power System

### 2.1 Power Supply Configuration

Each reactor is equipped with multiple Power Supply Units (PSU):

$N_{PSU} := 8$
$P_{PSU} := 240\ W$

**Driver efficiency (AC→DC conversion):**

$\eta_{drv} := 0.90$

### 2.2 Power per Reactor

LED output (DC - what LEDs receive):

$P_{LED,dc} := N_{PSU} \cdot P_{PSU} == 1\,920\ \text{W}$ <!-- [W] -->

Electricity consumption (AC - what we pay for):

$P_{LED,ac} := \frac{P_{LED,dc}}{\eta_{drv}} == 2\,133.3333\ \text{W}$ <!-- [W] -->

### 2.3 LED Efficiency

Based on KUL measurements of the production LED strips:

| LED Type | Efficiency (µmol/J) | Electrical→Light | Application |
|----------|---------------------|------------------|-------------|
| Red (660nm) | 4.29 | 78.0% | Primary (most efficient) |
| Blue (450nm) | 2.57 | 67.6% | Secondary (for Ax optimization) |

**Key insight:** Red LEDs are 67% more efficient than blue for the same photon output, making them the primary choice for energy efficiency.

**Geometric absorption factor** (fraction of light reaching culture):

$f_{geom} := 0.9143$

This factor accounts for optical losses (reflection, scattering) between LED output and reactor surface. Source: [LED light model reactor](https://docs.google.com/spreadsheets/d/1811bCfYQ_Mp5iv3A1ACBArBfRGujN4ZgyV9XCpuG5BY/) (KUL measurements).

**Photosynthetic Photon Efficacy (PPE) at panel surface:**

For 100% red LEDs (new system default):

$PPE_{red} := 4.29\ \frac{\text{µmol}}{\text{J}}$

**Effective PPE** (accounting for geometric losses):

$PPE_{eff} := PPE_{red} \cdot f_{geom} == 3.9223\ \text{µmol/J}$ <!-- [µmol/J] -->

This means 3.92 µmol photons reach the culture surface per joule of LED electrical input (PPE in µmol/J).

**Note:** The 240W per PSU is the **DC output** (what LEDs receive). For PAR/light calculations, we use DC output. For electricity costs, we use AC input (DC ÷ 0.90 for driver efficiency).

---

## 3. Cascade Operation

### 3.1 Flow Direction

The cascade moves culture through 8 reactors per header, from green phase to harvest:

```
R2 → R1 → [PUMP] → R8 → R7 → R6 → R5 → R4 → R3 (harvest)
└─ Green ─┘        └──────── Stress Phase ────────┘
```

![Cascade Flow Diagram](images/cascade_flow.svg)

### 3.2 LED Intensity Profile

Each reactor operates at a specific LED intensity based on its cascade position:

| Step | Reactor | Phase | Temperature | LED % |
|------|---------|-------|-------------|-------|
| 1 | R2 | Green | Cold (~20°C) | 20% |
| 2 | R1 | Green | Cold (~20°C) | 30% |
| 3 | R8 | Transition | Warming | 50% |
| 4 | R7 | Stress start | Warm (~30°C) | 70% |
| 5 | R6 | Stress | Warm | 90% |
| 6 | R5 | Stress | Warm | 100% |
| 7 | R4 | Stress | Warm | 100% |
| 8 | R3 | Harvest | Warm | 100% |

**Weighted average dimming:**

$d_{avg} := \frac{0.20 + 0.30 + 0.50 + 0.70 + 0.90 + 1.00 + 1.00 + 1.00}{8} == 0.7$

### 3.3 System Power Calculation

**Power per header (8 reactors at 70% average dimming):**

$P_{hdr} := N_{rct} \cdot P_{LED,ac} \cdot d_{avg} == 11.9467\ \text{kW}$ <!-- [kW] -->

**Blower power per MPC:**

$P_{blw} := 2000\ W$

**Total power per MPC (2 headers + blower):**

$P_{MPC} := 2 \cdot P_{hdr} + P_{blw} == 25.8933\ \text{kW}$ <!-- [kW] -->

**Total system power (12 MPCs):**

$P_{sys} := N_{MPC} \cdot P_{MPC} == 310.72\ \text{kW}$ <!-- [kW] -->

This equals **311 kW** total electrical consumption at 70% weighted LED dimming.

---

## 4. Productivity Analysis

### 4.1 Benchmark Data (Algreen)

The Algreen handbook provides reference data for astaxanthin productivity at different S/V ratios:

| System | S/V (m⁻¹) | Light Path | Productivity |
|--------|-----------|------------|--------------|
| Algreen 2L lab | 80 | 1.0 cm | 80 mg/L/day |
| Algreen 145L pilot | 40 | 2.5 cm | 52 mg/L/day |
| **axabio** | **165** | **0.4 cm** | **44 mg/L/day** (projected) |

**Key insight:** Higher S/V means better light distribution—more cells receive optimal light intensity.

### 4.2 Quantum Yield Analysis

From Algreen measurements, the best quantum yield achieved (S/V = 80, 50/50 R/B spectrum):

$Y_{ax} := 23.1\ \frac{\text{mg}}{\text{mol}}$

This represents 23.1 mg astaxanthin per mol PAR (photons absorbed).

### 4.3 Productivity Calculation

**PAR delivered per reactor per day (at 100% LED):**

PAR (mol/day) = Power (W) × PPE (µmol/J) × time (s) → automatically converts µmol to mol

$PPE_{eff} := PPE_{red} \cdot f_{geom} == 3.9223\ \text{µmol/J}$ <!-- [µmol/J] -->

$PAR_{rct} := P_{LED,dc} \cdot PPE_{eff} == 650.6703\ \text{mol/d}$ <!-- [mol/day] -->

**Astaxanthin production per reactor:**

Using quantum yield of 23.1 mg Ax/mol PAR:

$Y_{ax} := 23.1\ \frac{\text{mg}}{\text{mol}}$

$m_{ax,rct} := PAR_{rct} \cdot Y_{ax} == 15.0305\ \text{g/d}$ <!-- [g/day] -->

This equals approximately 15 g Ax/day per reactor at 100% LED intensity.

**Productivity per liter installed volume:**

$\gamma_{max} := \frac{m_{ax,rct}}{V_{rct}} == 76.2969\ \text{mg/d/L}$ <!-- [mg/L/day] -->

### 4.4 Cascade Efficiency Factor

The cascade operates at 70% average LED intensity, and not all phases produce astaxanthin equally:

$f_{cascade} := 0.58$

**Effective productivity:**

$\gamma_{eff} := \gamma_{max} \cdot f_{cascade} == 44.2522\ \text{mg/d/L}$ <!-- [mg/L/day] -->

This aligns with our 2030 target projection based on Algreen's best-in-class measurements.

---

## 5. Capacity Projections

### 5.1 Learning Curve

Productivity improves over time as we optimize the process:

| Year | Productivity (mg/L/day) | % of Maximum | Rationale |
|------|-------------------------|--------------|-----------|
| 2026 | 15 | 34% | Start-up phase, learning discount |
| 2027 | 30.5 | 69% | PSU upgrade complete, baseline |
| 2028 | 34 | 77% | Process optimization |
| 2029 | 38 | 86% | Continued improvement |
| 2030 | 44 | 100% | Algreen best-in-class |

**Productivity targets** (mg/L/day):

$\gamma_{26} := 15\ \frac{\text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Unexpected token after expression: frac '\textbackslash\{\}frac' at position 4}}$
$\gamma_{27} := 30.5\ \frac{\text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Unexpected token after expression: frac '\textbackslash\{\}frac' at position 6}}$
$\gamma_{28} := 34\ \frac{\text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Unexpected token after expression: frac '\textbackslash\{\}frac' at position 4}}$
$\gamma_{29} := 38\ \frac{\text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Unexpected token after expression: frac '\textbackslash\{\}frac' at position 4}}$
$\gamma_{30} := 44\ \frac{\text{mg}}{\text{L} \cdot \text{d}}
\\ \color{red}{\text{
    Error: Unexpected token after expression: frac '\textbackslash\{\}frac' at position 4}}$

### 5.2 Maximum Capacity Calculation

**Operating parameters:**

$d_{op} := 365\ d$
$u_{max} := 0.90$

**Volume in liters** (from section 1.3):

$V_L := 37824\ L$

**Daily production** (Volume × Productivity):

$m_{26} := V_L \cdot \gamma_{26} == [g/d]
\\ \color{red}{\text{
    Error: Unexpected token after expression: lbrace '\{' at position 13}}$ <!-- [g/day] -->
$m_{27} := V_L \cdot \gamma_{27} == [g/d]
\\ \color{red}{\text{
    Error: Unexpected token after expression: lbrace '\{' at position 13}}$ <!-- [g/day] -->
$m_{28} := V_L \cdot \gamma_{28} == [g/d]
\\ \color{red}{\text{
    Error: Unexpected token after expression: lbrace '\{' at position 13}}$ <!-- [g/day] -->
$m_{29} := V_L \cdot \gamma_{29} == [g/d]
\\ \color{red}{\text{
    Error: Unexpected token after expression: lbrace '\{' at position 13}}$ <!-- [g/day] -->
$m_{30} := V_L \cdot \gamma_{30} == [g/d]
\\ \color{red}{\text{
    Error: Unexpected token after expression: lbrace '\{' at position 13}}$ <!-- [g/day] -->

**Annual capacity at 90% uptime:**

$C_{26} := m_{26} \cdot d_{op} \cdot u_{max} == [kg]
\\ \color{red}{\text{
    Error: Undefined variable: m\_\{26\}}}$ <!-- [kg] -->
$C_{27} := m_{27} \cdot d_{op} \cdot u_{max} == [kg]
\\ \color{red}{\text{
    Error: Undefined variable: m\_\{27\}}}$ <!-- [kg] -->
$C_{28} := m_{28} \cdot d_{op} \cdot u_{max} == [kg]
\\ \color{red}{\text{
    Error: Undefined variable: m\_\{28\}}}$ <!-- [kg] -->
$C_{29} := m_{29} \cdot d_{op} \cdot u_{max} == [kg]
\\ \color{red}{\text{
    Error: Undefined variable: m\_\{29\}}}$ <!-- [kg] -->
$C_{30} := m_{30} \cdot d_{op} \cdot u_{max} == [kg]
\\ \color{red}{\text{
    Error: Undefined variable: m\_\{30\}}}$ <!-- [kg] -->

### 5.3 Business Plan Targets

**Targets from business plan (kg/year):**

$T_{26} := 112\ \text{kg}$
$T_{27} := 210\ \text{kg}$
$T_{28} := 334\ \text{kg}$
$T_{29} := 414\ \text{kg}$
$T_{30} := 516\ \text{kg}$

**Required uptime to meet targets** (%, where 90% uptime = full capacity):

$U_{26} := \frac{T_{26}}{C_{26}} \cdot 90 ==
\\ \color{red}{\text{
    Error: Undefined variable: C\_\{26\}}}$ <!-- Dimensionless (percentage) -->
$U_{27} := \frac{T_{27}}{C_{27}} \cdot 90 ==
\\ \color{red}{\text{
    Error: Undefined variable: C\_\{27\}}}$ <!-- Dimensionless (percentage) -->
$U_{28} := \frac{T_{28}}{C_{28}} \cdot 90 ==
\\ \color{red}{\text{
    Error: Undefined variable: C\_\{28\}}}$ <!-- Dimensionless (percentage) -->
$U_{29} := \frac{T_{29}}{C_{29}} \cdot 90 ==
\\ \color{red}{\text{
    Error: Undefined variable: C\_\{29\}}}$ <!-- Dimensionless (percentage) -->
$U_{30} := \frac{T_{30}}{C_{30}} \cdot 90 ==
\\ \color{red}{\text{
    Error: Undefined variable: C\_\{30\}}}$ <!-- Dimensionless (percentage) -->

| Year | Target (kg) | Capacity (kg) | Required Uptime | Status |
|------|-------------|---------------|-----------------|--------|
| 2026 | 112 | 186 | 54% | ✅ Feasible |
| 2027 | 210 | 379 | 50% | ✅ Feasible |
| 2028 | 334 | 423 | 71% | ✅ Feasible |
| 2029 | 414 | 472 | 79% | ✅ Feasible |
| 2030 | 516 | 547 | 85% | ✅ Feasible |

**Note:** All targets remain below the 90% maximum uptime, providing operational margin.

---

## 6. Energy Analysis

### 6.1 Electricity Price

Based on Proviron Industries Hemiksem pricing (November 2024):

$c_{elec} := 139\ \frac{€}{MWh}$

Components:
- Pure electricity: €93.50/MWh
- Certificates/transport: €42.37/MWh
- Green certificates: €3.00/MWh

### 6.2 Energy Consumption per Year

**Using `P_{sys}` from section 3.3:**

$t_{yr} := 1\ yr$

$E_{26} := P_{sys} \cdot t_{yr} \cdot \frac{U_{26}}{100} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{26\}}}$ <!-- [MWh] -->
$E_{27} := P_{sys} \cdot t_{yr} \cdot \frac{U_{27}}{100} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{27\}}}$ <!-- [MWh] -->
$E_{28} := P_{sys} \cdot t_{yr} \cdot \frac{U_{28}}{100} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{28\}}}$ <!-- [MWh] -->
$E_{29} := P_{sys} \cdot t_{yr} \cdot \frac{U_{29}}{100} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{29\}}}$ <!-- [MWh] -->
$E_{30} := P_{sys} \cdot t_{yr} \cdot \frac{U_{30}}{100} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{30\}}}$ <!-- [MWh] -->

### 6.3 Specific Energy Consumption (SEC)

**SEC = Energy / Production:**

$SEC_{26} := \frac{E_{26}}{T_{26}} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{26\}}}$ <!-- [MWh/kg] -->
$SEC_{27} := \frac{E_{27}}{T_{27}} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{27\}}}$ <!-- [MWh/kg] -->
$SEC_{28} := \frac{E_{28}}{T_{28}} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{28\}}}$ <!-- [MWh/kg] -->
$SEC_{29} := \frac{E_{29}}{T_{29}} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{29\}}}$ <!-- [MWh/kg] -->
$SEC_{30} := \frac{E_{30}}{T_{30}} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{30\}}}$ <!-- [MWh/kg] -->

**Cost = Energy × Price:**

$Cost_{26} := E_{26} \cdot c_{elec} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{26\}}}$ <!-- [k€] -->
$Cost_{27} := E_{27} \cdot c_{elec} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{27\}}}$ <!-- [k€] -->
$Cost_{28} := E_{28} \cdot c_{elec} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{28\}}}$ <!-- [k€] -->
$Cost_{29} := E_{29} \cdot c_{elec} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{29\}}}$ <!-- [k€] -->
$Cost_{30} := E_{30} \cdot c_{elec} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{30\}}}$ <!-- [k€] -->

**Summary table (calculated values):**

| Year | Uptime | Energy (MWh) | SEC (MWh/kg) | Cost (k€) |
|------|--------|--------------|--------------|-----------|
| 2026 | $U_{26} ==
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{26\}}}$ <!-- [dimensionless] --> | $E_{26} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{26\}}}$ <!-- [MWh] --> | $SEC_{26} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: SEC\_\{26\}}}$ <!-- [MWh/kg] --> | $Cost_{26} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: Cost\_\{26\}}}$ <!-- [k€] --> |
| 2027 | $U_{27} ==
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{27\}}}$ <!-- [dimensionless] --> | $E_{27} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{27\}}}$ <!-- [MWh] --> | $SEC_{27} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: SEC\_\{27\}}}$ <!-- [MWh/kg] --> | $Cost_{27} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: Cost\_\{27\}}}$ <!-- [k€] --> |
| 2028 | $U_{28} ==
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{28\}}}$ <!-- [dimensionless] --> | $E_{28} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{28\}}}$ <!-- [MWh] --> | $SEC_{28} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: SEC\_\{28\}}}$ <!-- [MWh/kg] --> | $Cost_{28} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: Cost\_\{28\}}}$ <!-- [k€] --> |
| 2029 | $U_{29} ==
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{29\}}}$ <!-- [dimensionless] --> | $E_{29} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{29\}}}$ <!-- [MWh] --> | $SEC_{29} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: SEC\_\{29\}}}$ <!-- [MWh/kg] --> | $Cost_{29} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: Cost\_\{29\}}}$ <!-- [k€] --> |
| 2030 | $U_{30} ==
\\ \color{red}{\text{
    Error: Undefined variable: U\_\{30\}}}$ <!-- [dimensionless] --> | $E_{30} == [MWh]
\\ \color{red}{\text{
    Error: Undefined variable: E\_\{30\}}}$ <!-- [MWh] --> | $SEC_{30} == [MWh/kg]
\\ \color{red}{\text{
    Error: Undefined variable: SEC\_\{30\}}}$ <!-- [MWh/kg] --> | $Cost_{30} == [kilo€]
\\ \color{red}{\text{
    Error: Undefined variable: Cost\_\{30\}}}$ <!-- [k€] --> |

### 6.5 Specific Energy Consumption (SEC) Trend

![SEC Evolution](images/sec_evolution.svg)

The SEC drops dramatically due to:

1. **2027 PSU upgrade:** +22% productivity with only +6.5% power → SEC −42%
2. **Learning curve:** Productivity improvements reduce SEC further
3. **2030 target:** 4.5 MWh/kg (65% below Algalif benchmark of 12.7 MWh/kg)

---

## 7. Conclusions

### 7.1 Key Findings

| Question | Answer |
|----------|--------|
| **Maximum capacity?** | 547 kg Ax/year (at 90% uptime, 44 mg/L/day) |
| **Are targets feasible?** | ✅ Yes—all years stay below 90% uptime |
| **SEC improvement?** | 13 → 4.5 MWh/kg (−65%), beats Algalif by 65% |
| **Critical milestone?** | 2027 PSU upgrade (7→8) drops SEC by 42% |

### 7.2 Technical Success Factors

1. **Complete 2027 upgrade** (8 PSU/reactor)
   - Increases light per reactor by 14%
   - Reduces volume per reactor by 6%
   - Net: +22% productivity per liter

2. **Reach Algreen productivity** (44 mg/L/day by 2030)
   - Requires optimized R/B spectrum profile
   - Focus on cascade temperature control
   - Consistent biomass density (8-10 g/L at harvest)

3. **Maintain >85% uptime**
   - Preventive maintenance schedule
   - Redundancy in critical components
   - Fast contamination response protocols

### 7.3 Geometry Advantage

axabio's cylindrical tube design provides significant advantages:

| Parameter | axabio | Algreen (145L) | Advantage |
|-----------|--------|----------------|-----------|
| S/V ratio | 165 m⁻¹ | 40 m⁻¹ | +313% |
| Light path | 0.4 cm | 2.5 cm | −84% |
| Light distribution | Radial | Bilateral | Better uniformity |

This geometry allows achieving Algreen-level productivity (44 mg/L/day) despite cascade operation inefficiencies.

---

## Appendix A: Photon Budget and Quantum Yield

### A.1 PAR per Header - Detailed Calculation

**System configuration:** New system (8 PSU per reactor, 1,920 W DC max per reactor)

**Helper variables:**

$PPE_{red,raw} := 4.29\ \frac{\text{µmol}}{\text{J}}$
$PPE_{blue,raw} := 2.57\ \frac{\text{µmol}}{\text{J}}$
$f_{geom} := 0.9143$
$P_{LED,dc} := 1920\ W$
$t_{day} := 86400\ \frac{s}{d}$

**Effective PPE for different R/B ratios:**
$PPE_{eff,9010} := (0.90 \cdot PPE_{red,raw} + 0.10 \cdot PPE_{blue,raw}) \cdot f_{geom} == 3.7651\ \text{µmol/J}$ <!-- [µmol/J] -->
$PPE_{eff,8020} := (0.80 \cdot PPE_{red,raw} + 0.20 \cdot PPE_{blue,raw}) \cdot f_{geom} == 3.6078\ \text{µmol/J}$ <!-- [µmol/J] -->
$PPE_{eff,7030} := (0.70 \cdot PPE_{red,raw} + 0.30 \cdot PPE_{blue,raw}) \cdot f_{geom} == 3.4506\ \text{µmol/J}$ <!-- [µmol/J] -->
$PPE_{eff,6040} := (0.60 \cdot PPE_{red,raw} + 0.40 \cdot PPE_{blue,raw}) \cdot f_{geom} == 3.2933\ \text{µmol/J}$ <!-- [µmol/J] -->
$PPE_{eff,5050} := (0.50 \cdot PPE_{red,raw} + 0.50 \cdot PPE_{blue,raw}) \cdot f_{geom} == 3.136\ \text{µmol/J}$ <!-- [µmol/J] -->

**Assign PPE to reactors:**
$PPE_{eff,R2} := PPE_{eff,9010}$
$PPE_{eff,R1} := PPE_{eff,9010}$

---

> *livemathtex: 2026-01-16 00:27:45 | 87 definitions, 71 evaluations | 55 errors | 0.16s* <!-- livemathtex-meta -->
