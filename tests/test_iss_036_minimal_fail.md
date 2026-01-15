<!-- livemathtex: output=inplace, json=true, digits=4 -->

# Test ISS-036 Minimal - Must Fail

**Define variables with commas:**
$PPE_{red,raw} := 4.29\ \frac{\text{µmol}}{\text{J}}$
$PPE_{blue,raw} := 2.57\ \frac{\text{µmol}}{\text{J}}$
$f_{geom} := 0.9143$

**This should FAIL (from original document line 482):**
$PPE_{eff,9010} := (0.90 \cdot PPE_{red,raw} + 0.10 \cdot PPE_{blue,raw}) \cdot f_{geom} == 3.7651\ \text{µmol/J}$ <!-- [µmol/J] -->

**This should also FAIL (from original document line 489):**
$PPE_{eff,R2} := PPE_{eff,9010} == 3.7651\ \text{µmol/J}$ <!-- [µmol/J] -->

---

> *livemathtex: 2026-01-16 00:27:45 | 5 definitions, 2 evaluations | no errors | 0.06s* <!-- livemathtex-meta -->
