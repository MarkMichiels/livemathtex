# Phase 14 Research: Pint Evaluator Core

## Problem Statement

ISS-024: Numerical calculations produce incorrect results because LiveMathTeX uses SymPy for numerical evaluation, but SymPy doesn't automatically convert units.

**Example bug:**
- `m_{26} = 49,020 g/day` × `d_{op} = 365 d` → Expected: `16,103 kg`, Actual: `0.1864 kg` (86,400x too low)
- **Pint test:** `49020 g/day * 365 day * 0.9` → `16,103.07 kg` ✅ CORRECT
- **SymPy test:** Same calculation → `0.1864 kg` ❌ WRONG

**Root cause:** SymPy treats `365 * day` as symbolic expression, doesn't convert to `31,536,000 * second` automatically.

---

## Previous Migration Attempt (Phases 1-5)

The previous Pint migration (documented in `.planning/history/PINT_MIGRATION_ANALYSIS.md`) completed 5 phases:

### What WAS Completed

1. **Phase 1: Test Scaffold** ✅
   - Created 52 tests for examples and Pint backend

2. **Phase 2: Pint Integration** ✅
   - Created `engine/pint_backend.py`
   - `get_unit_registry()` - case-sensitive Pint registry
   - `is_unit_token(token)` - strict unit detection
   - `check_variable_name_conflict()` - prevents variable names matching units
   - `parse_value_with_unit()` - parses "value unit" strings

3. **Phase 3: The Swap** ✅
   - Integrated Pint for unit name validation
   - `_check_unit_name_conflict()` now uses `pint_backend.check_variable_name_conflict()`

4. **Phase 4: Cleanup** ✅
   - Removed `engine/units.py`
   - All unit handling consolidated into `pint_backend.py`
   - `value:` directive uses Pint `convert_value_to_unit()`

5. **Phase 5: IR v3.0** ✅
   - `LivemathIRV3`, `SymbolEntryV3`, `CustomUnitEntry` dataclasses
   - Pint-based unit conversion in IR

### What was NOT Completed

**Numerical evaluation still uses SymPy!**

The `evaluator.py` file uses:
- `_compute()` method that evaluates with SymPy
- `SymPyUnitRegistry` class for maintaining SymPy Quantity objects
- `sympy_strip_unit_from_value()` for parsing

**Current dual-registry architecture:**
```
pint_backend.py
├── Pint Registry (get_unit_registry())
│   ├── Unit validation (is_unit_token)
│   ├── Unit conversion (convert_value_to_unit)
│   └── Dimensionality checking
│
└── SymPy Registry (SymPyUnitRegistry)
    ├── Custom unit definitions for SymPy
    └── Used by evaluator._compute() for calculations ← THE PROBLEM
```

---

## Recommended Approach (Option B from PINT_MIGRATION_ANALYSIS.md)

**Hybrid approach:**
1. Keep `latex2sympy2` as **parser only** (LaTeX → expression tree)
2. Use **Pint Quantities for numerical evaluation** (not SymPy)
3. Keep SymPy only for `=>` **symbolic mode** (differentiation, integration)

This preserves:
- Existing LaTeX parsing (including `v_{n}` mapping for robustness)
- The operator semantics (`:=`, `==`, `=>`, `===`)
- Error model and preprocessor rules

---

## Implementation Analysis

### Current Evaluation Flow

```
Evaluator.evaluate(calc: Calculation)
  └── _handle_assignment() or _handle_evaluation()
        └── _compute(expression, propagate_units=bool)
              └── latex2sympy.latex2sympy(expression)  # SymPy expression
              └── sympy.N(result)                      # SymPy numeric eval
              └── SymPy unit propagation               # PROBLEM HERE
```

### Proposed New Flow

```
Evaluator.evaluate(calc: Calculation)
  └── _handle_assignment() or _handle_evaluation()
        └── _compute_with_pint(expression, propagate_units=bool)
              └── latex2sympy.latex2sympy(expression)  # Parse to SymPy AST
              └── _evaluate_ast_with_pint(ast, symbols) # Walk AST, use Pint
              └── Pint Quantity arithmetic             # Correct unit handling
```

### Key Components to Modify

1. **`evaluator.py`** - Major refactoring:
   - Add `_compute_with_pint()` method that:
     - Uses latex2sympy for parsing
     - Walks the SymPy AST
     - Evaluates with Pint Quantities
   - Route numeric evaluations (`==`) through Pint
   - Keep symbolic evaluations (`=>`) on SymPy

2. **`symbols.py`** - Update `SymbolValue`:
   - Store values as Pint Quantities
   - Update `value_with_unit` property

3. **`pint_backend.py`** - Add:
   - `evaluate_sympy_ast_with_pint(ast, symbol_map)` function
   - Handles arithmetic operations (+, -, *, /, **)
   - Handles function calls (sqrt, sin, cos, etc.)

### AST Walking Strategy

SymPy AST nodes to handle:
- `Mul`, `Add`, `Pow` - arithmetic
- `Symbol` - variable lookup (substitute with Pint Quantity)
- `Number`, `Float`, `Integer` - numeric literals
- `Function` - mathematical functions
- `Quantity` - SymPy units (convert to Pint)

Example implementation sketch:
```python
def evaluate_ast_with_pint(expr, symbols: dict[str, pint.Quantity]):
    """Walk SymPy AST and evaluate with Pint Quantities."""
    ureg = get_unit_registry()

    if isinstance(expr, (int, float)):
        return expr

    if isinstance(expr, sympy.Symbol):
        name = str(expr)
        if name in symbols:
            return symbols[name]  # Pint Quantity
        raise ValueError(f"Undefined symbol: {name}")

    if isinstance(expr, sympy.Mul):
        result = 1
        for arg in expr.args:
            result = result * evaluate_ast_with_pint(arg, symbols)
        return result

    if isinstance(expr, sympy.Add):
        result = 0
        for arg in expr.args:
            result = result + evaluate_ast_with_pint(arg, symbols)
        return result

    # ... more cases
```

---

## Risk Analysis

### Low Risk
- Phase 13 (ISS-023): Fix `_format_si_value()` LaTeX cleanup - isolated fix

### Medium Risk
- Maintaining backwards compatibility with existing documents
- Handling edge cases in AST walking

### Higher Risk (mitigated by tests)
- Large refactoring of evaluator.py
- Potential for subtle behavioral changes

---

## Test Strategy

**Required tests for Phase 14:**

1. **Rate × Time calculations:**
   ```markdown
   $m := 49020\ g/day$
   $d := 365\ d$
   $C := m \cdot d ==$ → should be ~17,892 kg (not 0.1864 kg)
   ```

2. **Energy calculations:**
   ```markdown
   $P := 310.7\ kW$
   $t := 8760\ h$
   $E := P \cdot t ==$ → should be correct MWh
   ```

3. **Compound unit calculations:**
   ```markdown
   $rate := 50\ m³/h$
   $time := 24\ h$
   $volume := rate \cdot time ==$ → should be 1200 m³
   ```

4. **All existing examples must pass** (regression)

---

## Execution Plan

### Phase 13: SI Value Fix (ISS-023) - Quick fix, no research needed
- Fix `_format_si_value()` regex in evaluator.py
- ~30 minutes effort

### Phase 14: Pint Evaluator Core (ISS-024) - This phase
1. Create `evaluate_ast_with_pint()` in pint_backend.py
2. Add `_compute_with_pint()` in evaluator.py
3. Route numeric evaluations through Pint
4. Add comprehensive tests
5. ~2-4 hours effort

### Phase 15: Verification & Docs
- Test with real documents (astaxanthin_production_analysis.md)
- Update documentation
- ~1 hour effort

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-13 | Research completed | Previous attempt documented in PINT_MIGRATION_ANALYSIS.md |
| 2026-01-13 | Option B (hybrid) confirmed | Keep latex2sympy as parser, use Pint for numeric evaluation |
| 2026-01-13 | Phase 13 first | Quick win, independent of Phase 14 |

---

*Research completed: 2026-01-13*
*Ready for planning: Phase 13 (quick), then Phase 14 (main work)*
