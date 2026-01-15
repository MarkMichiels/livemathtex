---
phase: 28-sympy-removal
plan: 04
status: complete
---

# 28-04 Summary: Simplify Internal IDs

## Objective
Simplify internal IDs from LaTeX format (`v_{0}`) to simple Python format (`v0`).

## Changes Made

### Task 1: Update NameGenerator in symbols.py
**Commit:** `323cafc`

- Changed ID format from `v_{0}`, `f_{0}`, `x_{0}` to `v0`, `f0`, `x0`
- Removed `use_clean_ids` parameter (now always uses simple format)
- Updated module docstring to document new convention
- IDs are now 0-indexed: v0, v1, v2, ...

### Task 2: Update evaluator.py
**Commit:** `0ff9749`

- Updated docstrings and comments to reference v0/f0/x0 format
- Removed `_use_clean_ids` conditional checks (always enabled now)
- Formula dependency tracking now always active
- Updated `_rewrite_with_internal_ids` documentation

### Task 3: Update expression_evaluator.py
**Commit:** `89cd69c`

- Updated `_lookup_variable` docstring to document internal ID handling
- Function already handled both formats correctly via exact match

### Additional Changes: Tokenizer and Documentation
**Commit:** `0078a20`

- Added tokenizer pattern `[vfx]\d+` to recognize simple internal IDs
- Without this, `v0` was tokenized as `v` + `0` (variable + number)
- Updated documentation in:
  - `core.py`: `_populate_ir_symbols` docstring
  - `ir/__init__.py`: Module docstring (v2.0 -> v3.0)
  - `ir/schema.py`: `SymbolEntry.id` docstring
  - `ir/builder.py`: Library format example

## Verification Results

### ID Generation
```python
>>> from livemathtex.engine.symbols import NameGenerator
>>> ng = NameGenerator()
>>> [ng.next_value_id() for _ in range(3)]
['v0', 'v1', 'v2']
>>> [ng.next_formula_id() for _ in range(3)]
['f0', 'f1', 'f2']
```

### Tokenizer
```python
>>> from livemathtex.parser.expression_tokenizer import ExpressionTokenizer
>>> ExpressionTokenizer('v0').tokenize()
[Token(VARIABLE, 'v0'), Token(EOF, '')]  # Correct!
```

### Tests
- All tests that depend on internal ID format pass
- 52 pre-existing failures remain (unit handling, unrelated to this plan)
- 423 tests pass

## Files Modified

| File | Changes |
|------|---------|
| `engine/symbols.py` | ID generation simplified, removed use_clean_ids |
| `engine/evaluator.py` | Comments and conditional checks updated |
| `engine/expression_evaluator.py` | Docstring updated |
| `parser/expression_tokenizer.py` | Added `[vfx]\d+` pattern |
| `core.py` | Documentation comments updated |
| `ir/__init__.py` | Version bump, ID format docs |
| `ir/schema.py` | SymbolEntry docstring |
| `ir/builder.py` | Library format example |

## Commit Hashes

1. `323cafc` - refactor(28-04): simplify internal IDs from v_{0} to v0 format
2. `0ff9749` - refactor(28-04): update evaluator.py for simple internal ID format
3. `89cd69c` - refactor(28-04): update expression_evaluator docstring for simple IDs
4. `0078a20` - refactor(28-04): add tokenizer support for simple internal IDs

## Success Criteria Met

- [x] All internal IDs use simple format (v0, f0, x0)
- [x] No LaTeX braces in internal representations
- [x] Symbol table and evaluator work correctly
- [x] Tokenizer recognizes simple ID format
