> *Updated: 2026-01-04 19:59:19 | Duration: 0.21s* <!-- livemathtex-meta -->

# Test Phase 2: Units and Symbolic

## Units

Define simple units:

$m_{obj} := 10 \text{kg}$
$a_{obj} := 9.8 \frac{\text{m}}{\text{s}^{2}}$

Calculate force (Default SI):

$F := a_{obj} \cdot m_{obj} == 98 \frac{\text{kg} \cdot \text{m}}{\text{s}^{2}}$

Calculate force (Forced Newtons using comment):

$F == 98 \text{N}$ <!-- [N] -->

## Partial Conversion

Energy:

$W := 100 \text{J}$

Convert Energy to Newtons (should be N * m):

$W == 100 \text{m} \cdot \text{N}$ <!-- [N] -->
