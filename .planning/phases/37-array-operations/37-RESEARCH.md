# Phase 37: Array Operations Research

## Summary

This document analyzes the design requirements for array operations in LiveMathTeX (ISS-041).

## Problem Statement

Users need to perform repetitive calculations (e.g., yearly projections 2026-2030, multiple reactors) without defining each value individually. Current approach requires:

```latex
$gamma_{26} := 15\ mg/L/d$
$gamma_{27} := 30.5\ mg/L/d$
$gamma_{28} := 34\ mg/L/d$
$gamma_{29} := 38\ mg/L/d$
$gamma_{30} := 44\ mg/L/d$
```

Desired approach:

```latex
$gamma := [15, 30.5, 34, 38, 44]\ \text{mg/L/d}$
```

## Requirements

### Core Requirements

1. **Array definition**: Define arrays of values with optional units
2. **Element access**: Access individual elements by index
3. **Vectorized operations**: Apply scalar operations to all elements
4. **Idempotence**: Process-clear-process cycles must be stable

### Optional Requirements (Future)

- Named indices (e.g., `gamma[2026]` instead of `gamma[0]`)
- Array slicing
- Array reduction functions (sum, mean, etc.)

## Syntax Design

### Array Definition

```latex
# Basic array (dimensionless)
$values := [1, 2, 3, 4, 5]$

# Array with unit (unit applies to all elements)
$gamma := [15, 30.5, 34, 38, 44]\ \text{mg/L/d}$

# Evaluated array (shows all values)
$gamma := [15, 30.5, 34]\ \text{mg/L/d} == [15, 30.5, 34]\ \text{mg/L/d}$
```

### Element Access

```latex
# Zero-indexed access
$gamma_0 == 15\ \text{mg/L/d}$

# Using bracket notation
$gamma[0] == 15\ \text{mg/L/d}$

# Access in expressions
$first := gamma[0] == 15\ \text{mg/L/d}$
```

### Vectorized Operations

```latex
# Scalar * array = array
$V_L := 37824\ L$
$m := V_L \cdot gamma == [567.36, 1153.63, 1286.02, 1437.31, 1664.26]\ \text{g/d}$

# Array * scalar
$gamma_doubled := gamma \cdot 2 == [30, 61, 68, 76, 88]\ \text{mg/L/d}$

# Array + array (element-wise)
$total := a + b == [...]$
```

## Parser Changes

### TokenType Additions

```python
# New token types
LBRACKET = "lbracket"  # [
RBRACKET = "rbracket"  # ]
```

### ExprNode Additions

```python
@dataclass
class ArrayNode(ExprNode):
    """Array literal node."""
    elements: List[ExprNode]

@dataclass
class IndexNode(ExprNode):
    """Array index access node."""
    array: ExprNode
    index: ExprNode
```

### Grammar Extension

```
primary -> ... | '[' expression_list ']' | primary '[' expression ']'
expression_list -> expression (',' expression)*
```

## Evaluator Changes

### Value Storage

Arrays are stored as lists of Pint Quantities:

```python
# In symbol table
symbols["gamma"] = [
    15 * ureg("mg/L/d"),
    30.5 * ureg("mg/L/d"),
    34 * ureg("mg/L/d"),
    38 * ureg("mg/L/d"),
    44 * ureg("mg/L/d"),
]
```

### JSON Storage

```json
{
  "gamma": {
    "type": "array",
    "value": [15, 30.5, 34, 38, 44],
    "unit": "mg/L/d",
    "length": 5
  }
}
```

### Vectorized Operations

When a binary operation involves an array and a scalar:

```python
def _apply_binary_op(op, left, right, ureg):
    # Check if either operand is an array
    if isinstance(left, list):
        if isinstance(right, list):
            # Element-wise operation
            return [_apply_binary_op(op, l, r, ureg) for l, r in zip(left, right)]
        else:
            # Broadcast scalar to array
            return [_apply_binary_op(op, l, right, ureg) for l in left]
    elif isinstance(right, list):
        # Broadcast scalar to array
        return [_apply_binary_op(op, left, r, ureg) for r in right]
    # ... existing scalar operations
```

## Output Format

### Single-line (compact)

```latex
$gamma == [15, 30.5, 34, 38, 44]\ \text{mg/L/d}$
```

### Multi-line (readable for long arrays)

```latex
$m == \begin{bmatrix} 567.36 \\ 1153.63 \\ 1286.02 \\ 1437.31 \\ 1664.26 \end{bmatrix}\ \text{g/d}$
```

### Threshold

- Use single-line format for arrays with <= 5 elements
- Use multi-line format for arrays with > 5 elements

## Clear Behavior

When clearing:
- Preserve array definition syntax: `$gamma := [15, 30.5, 34]\ \text{mg/L/d}$`
- Remove computed results: `$gamma == [...]$` -> `$gamma == $`

## Implementation Plan

### Phase 37-01: Tokenizer Extension
- Add LBRACKET and RBRACKET token types
- Add pattern matching for `[` and `]`

### Phase 37-02: Parser Extension
- Add ArrayNode and IndexNode to expression_parser.py
- Parse array literals `[expr, expr, ...]`
- Parse index access `expr[expr]`

### Phase 37-03: Evaluator Extension
- Evaluate ArrayNode to list of Pint Quantities
- Evaluate IndexNode to single Pint Quantity
- Handle array storage in symbol table

### Phase 37-04: Vectorized Operations
- Modify `_apply_binary_op` to handle arrays
- Implement broadcasting (scalar * array)
- Format array output in LaTeX

## Risks and Mitigations

### Risk: Ambiguity with existing bracket syntax
- Mitigation: LaTeX math rarely uses `[...]` for grouping; use `(...)` instead

### Risk: Large arrays break line rendering
- Mitigation: Use `\begin{bmatrix}` for multi-line display

### Risk: Performance with large arrays
- Mitigation: Set reasonable array size limit (e.g., 100 elements)

## Decision

Recommend implementing basic array operations with:
1. Array literal syntax using `[...]`
2. Zero-indexed element access using `arr[i]`
3. Scalar-array broadcasting
4. Single-line output format (compact)

This covers the primary use case (yearly/reactor calculations) with minimal parser changes.

## Estimated Effort

- Phase 37-01: ~30 min (tokenizer)
- Phase 37-02: ~60 min (parser)
- Phase 37-03: ~45 min (evaluator basics)
- Phase 37-04: ~60 min (vectorized ops + output)

Total: ~3-4 hours
