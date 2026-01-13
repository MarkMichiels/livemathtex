# Phase 14 Plan: Pint Evaluator Core (ISS-024)

## Goal

Replace SymPy numerical evaluation with Pint-based evaluation for numerical calculations. Keep latex2sympy as the LaTeX parser, but evaluate the resulting expression tree using Pint Quantities.

## Background

See: `RESEARCH.md` in this directory for full analysis.

**Current problem:** SymPy treats `365 * day` symbolically and doesn't convert to seconds automatically, causing 86,400x calculation errors in rate×time calculations.

**Solution:** Walk the SymPy AST after parsing and evaluate with Pint Quantities instead of SymPy numeric evaluation.

## Architecture Change

```
BEFORE (current):
  latex2sympy → SymPy expression → sympy.N() → SymPy unit propagation → result

AFTER (new):
  latex2sympy → SymPy expression → walk AST → Pint Quantities → result
                                   ↑ NEW CODE HERE
```

## Implementation Tasks

### 14-01: Create Pint AST evaluator in pint_backend.py

Add `evaluate_sympy_ast_with_pint()` function that:
- Takes a SymPy expression (AST) and a symbol map
- Walks the AST nodes: `Mul`, `Add`, `Pow`, `Symbol`, `Number`, etc.
- Substitutes symbols with Pint Quantities from the symbol map
- Returns a Pint Quantity result

Key AST node handlers:
- `sympy.Symbol` → lookup in symbol map, return Pint Quantity
- `sympy.Number/Float/Integer` → convert to float
- `sympy.Mul` → multiply all args (Pint handles unit multiplication)
- `sympy.Add` → add all args (Pint handles unit addition with compatibility check)
- `sympy.Pow` → raise to power
- `sympy.physics.units.Quantity` → convert to Pint unit
- Function calls (sqrt, sin, cos, exp, log) → apply to magnitude or use Pint

### 14-02: Update SymbolValue to store Pint Quantities

In `symbols.py`:
- Add `pint_quantity: Optional[pint.Quantity]` field to `SymbolValue`
- Update `value_with_unit` property to return Pint Quantity
- Update `store()` to create Pint Quantity from value + unit

### 14-03: Add `_compute_with_pint()` in evaluator.py

New method that:
1. Parses LaTeX with latex2sympy (existing code)
2. Builds symbol map with Pint Quantities from self.symbols
3. Calls `evaluate_sympy_ast_with_pint(ast, symbol_map)`
4. Returns result as Pint Quantity

### 14-04: Route numeric evaluations through Pint

Update `_handle_evaluation()` and `_handle_define_eval()`:
- For `==` operator: use `_compute_with_pint()` instead of `_compute()`
- Keep `=>` (symbolic) operator on existing SymPy path
- Keep `:=` (assignment) on existing path (may use Pint for RHS evaluation)

### 14-05: Add comprehensive tests

Create `tests/test_pint_evaluator.py`:
- Rate × time: `49020 g/day * 365 d` → ~17,892 kg
- Energy: `310.7 kW * 8760 h` → correct MWh
- Volume: `50 m³/h * 24 h` → 1200 m³
- Currency: `100 kWh * 0.10 €/kWh` → 10 €
- Verify all existing examples still pass

## Risk Mitigation

1. **Feature flag:** Add `use_pint_eval=True` parameter to evaluator
2. **Fallback:** On Pint evaluation error, fall back to SymPy with warning
3. **Incremental:** Test each handler individually before integrating

## Verification

1. All 345 existing tests pass
2. New rate×time tests pass
3. Example documents produce correct numerical results
4. `astaxanthin_production_analysis.md` processes correctly

## Effort Estimate

- 14-01: ~45 min (AST evaluator)
- 14-02: ~15 min (SymbolValue update)
- 14-03: ~30 min (compute_with_pint)
- 14-04: ~30 min (routing changes)
- 14-05: ~30 min (tests)

Total: ~2.5 hours

---

*Plan created: 2026-01-13*
