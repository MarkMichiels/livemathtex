# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

### ISS-016: Error markup in input document not detected or cleaned

- **Discovered:** 2026-01-12 (during document processing)
- **Type:** Bug
- **Description:** When a document contains error markup from a previous run (e.g., `\\ \color{red}{\text{Error: ...}}`), LiveMathTeX processes it without detecting or reporting these errors. The error count shows "0 errors" even though error markup is visible in the output. Additionally, incomplete expressions (e.g., `\ := m_{30} ...` or `$C_{26} := ... == \}$`) remain in the document after error cleanup, causing parsing issues. **Root cause:** Error detection only checks for `\\color{red}` in newly generated `result_latex` from `evaluator.evaluate()`, not in the input document itself. The `clear_text()` function attempts to remove error markup, but incomplete expressions and orphaned error fragments persist.
- **Impact:** High (misleading error reporting, broken LaTeX in documents, user confusion)
- **Effort:** Medium
- **Suggested phase:** v1.3
- **Files to change:**
  - `src/livemathtex/core.py` - Enhance `clear_text()` to better handle incomplete expressions and orphaned error fragments. Add detection for error markup in input before processing.
  - `src/livemathtex/core.py` - Add pre-processing step to detect and report existing error markup in input document (warn user or auto-clean).
  - `src/livemathtex/engine/evaluator.py` - Consider detecting error markup in input LaTeX and treating it as an error condition.
  - `tests/test_process_clear_cycle.py` - Add test for documents with existing error markup to verify cleanup and error detection.
- **Example:**
  - Input document contains: `$C_{26} := m_{26} \cdot d_{op} \cdot u_{max} == \}$ <!-- [kg/year] -->` and `\\ \color{red}{\text{Error: Undefined variable 'C\_26'}}`
  - LiveMathTeX reports: "no errors"
  - Output still contains: error markup and incomplete expressions
  - Expected: Either auto-clean error markup before processing, or detect and report it as an error condition

### ISS-014: Unit conversion fails for recursively defined units (MWh, mol/day, etc.)

- **Discovered:** 2026-01-12 (during document analysis)
- **Type:** Bug
- **Description:** Unit hints with HTML comment syntax `<!-- [MWh] -->` fail to convert results to the target unit. **Root cause:** `_apply_conversion()` receives a dimensionless value (already converted to base SI as a pure number), but divides by a SymPy unit expression (e.g., `1000000*hour*watt` for MWh). The ratio calculation `value / target_unit` produces a result that still has units (e.g., `168*second**2/(kilogram*meter**2)`), which cannot be converted to `float()`, causing the conversion to fail silently and fall back to SI base units. This affects recursively defined units like `MWh === 1000 kWh` (where `kWh === 1000 Wh`), as well as compound units like `mol/day` and `MWh/kg`. Simple units like `kW` work because they use a different code path (`_parse_unit_with_prefix`).
- **Impact:** High (breaks unit conversion for complex/recursive units, making documents hard to read)
- **Effort:** Medium
- **Suggested phase:** v1.3
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - Fix `_apply_conversion()` to properly handle dimensionless values vs. unit expressions. Either: (1) pass value as SymPy Quantity with units, or (2) convert target_unit to base SI first before ratio calculation, or (3) use Pint-based conversion instead of SymPy for unit hints.
  - `tests/test_unit_conversion.py` - Add tests for recursive unit definitions (MWh, mol/day, MWh/kg) to verify conversion works
- **Example:**
  - Input: `$E_{26} := P_{sys} \cdot t_{yr} \cdot \frac{U_{26}}{100} == $ <!-- [MWh] -->`
  - Expected: `$E_{26} := ... == 168\ \text{MWh}$`
  - Actual: `$E_{26} := ... == 168\,000\ \text{kg} \cdot \text{m}^{2}/\text{s}^{2}$ <!-- [MWh] -->`


### ISS-015: User documentation incomplete/outdated

- **Discovered:** 2026-01-12 (during Phase 3 planning)
- **Type:** Documentation
- **Description:** User-facing documentation may not cover all current features and error handling. Needs review and update to include:
  - Inline unit hint syntax `$E == [kJ]$` (added in v1.3)
  - HTML comment unit hints `<!-- [unit] -->`
  - Custom unit definitions with `===` syntax
  - Error messages for undefined units and redefinition attempts
  - Process/clear cycle behavior
  - Examples for all supported syntaxes
- **Impact:** Medium (users may not discover features or understand errors)
- **Effort:** Medium
- **Suggested phase:** v1.4 (after v1.3 stabilizes)
- **Files to review:**
  - `README.md` - Main documentation
  - `docs/` - If exists, all documentation files
  - `examples/` - Example files should demonstrate all features
- **Deliverables:**
  - Complete syntax reference
  - Feature overview with examples
  - Error message documentation
  - Migration guide if breaking changes

## Closed Enhancements

### ISS-009: Compound unit definitions with division - evaluation lookup fails

**Resolved:** 2026-01-12 - Fixed in v1.3 Phase 3
**Solution:** The root cause was that `_handle_assignment` didn't propagate units for formula assignments. Fixed by:
1. Calling `_compute(rhs, propagate_units=True)` when no explicit unit is given
2. Extracting the computed unit from the result with `_extract_unit_from_value`
3. Added check in `_handle_unit_definition` to prevent redefining existing Pint units
4. Changed `_apply_conversion` to raise errors instead of silently failing
5. Fixed `_parse_unit_expression` to resolve prefixed units via `pint_to_sympy_with_prefix`
Added 5 tests in `TestCustomUnitWithDivision` class.

### ISS-013: Inline unit hint syntax lost after processing, breaks re-processing

**Resolved:** 2026-01-12 - Fixed in v1.3 Phase 2
**Solution:** Inline unit hints `$E == [kJ]$` now automatically generate HTML comments in output: `$E == 1000\ \text{kJ}$ <!-- [kJ] -->`. The hint is tracked in `core.py` and passed to the renderer as a tuple `(result, inline_unit_hint)`. Re-processing uses the preserved hint. Added `TestInlineUnitHintReprocessing` test class with 3 tests.

### ISS-012: Process/clear cycle produces unstable results and incorrect errors

**Resolved:** 2026-01-12 - Fixed in v1.2 Phase 1
**Solution:** Fixed `clear_text()` to properly handle nested braces in error markup using pattern `\{(?:[^{}]|\{[^{}]*\})*\}`. Added cleanup patterns for orphaned artifacts (`\\ }$`, `\\ $`). Added pre-processing step in `process_file()` to clear already-processed content before parsing. All 8 cycle tests now pass.

### ISS-010: Expose public Python API for library usage

**Resolved:** 2026-01-11 - Fixed in Phase 3
**Solution:** Public API exported in `__init__.py`. Exports `process_text()` as primary API, along with both v2.0 and v3.0 IR types for flexibility.

### ISS-011: `livemathtex clear` command to reset document calculations

**Resolved:** 2026-01-12 - Fixed in Phase 3
**Solution:** Added `clear_text()` function to core.py and `livemathtex clear` CLI command. Removes evaluation results and error markup while preserving definitions, unit definitions, and unit hints.

### ISS-007: Evaluation results show SI base units instead of requested output unit

**Resolved:** 2026-01-11 - Verified working in Phase 4
**Solution:** Output unit conversion via `<!-- [unit] -->` syntax was already implemented and working. Tests and documentation added to formalize the feature.

### ISS-008: Output unit hint syntax requires HTML comment

**Resolved:** 2026-01-11 - Fixed in Phase 4
**Solution:** Inline unit hint syntax `$E == [kJ]$` implemented as alternative to HTML comments. Cleaner syntax, visible in rendered Markdown. Both syntaxes work; HTML comment takes precedence if both present.

### ISS-001: `value:` directive doesn't support complex/custom units

**Resolved:** 2026-01-08 - Fixed in Phase 1
**Solution:** Pint-based unit conversion implemented. All Pint-recognized units now work in value directives, including energy (MWh, kWh), currency (EUR, €), and compound units (MWh/kg, €/kWh).

### ISS-002: Remove all hardcoded unit lists - use Pint as single source of truth

**Resolved:** 2026-01-08 - Fixed in Phase 1
**Solution:** All 4 hardcoded unit lists removed (~230 definitions) and replaced with dynamic Pint queries. Pint is now the single source of truth for unit recognition.

### ISS-003: Failed variable definition still allows unit interpretation in subsequent formulas

**Resolved:** 2026-01-11 - Fixed in Phase 1
**Solution:** Removed unit fallback entirely. Undefined symbols that match unit names now ALWAYS produce an error. Breaking change: expressions like `$m_1 := 10 \cdot kg$` now require correct syntax `$m_1 := 10\ kg$`.

### ISS-004: Document directive parser does not ignore code blocks

**Resolved:** 2026-01-11 - Fixed in Phase 2
**Solution:** Added code block stripping before directive scanning. Fenced code blocks (``` and ~~~) are now completely ignored by the directive parser.

### ISS-005: LaTeX-wrapped units (`\text{...}`) not parsed by Pint

**Resolved:** 2026-01-11 - Fixed in Phase 2
**Solution:** Added `clean_latex_unit()` function that converts LaTeX unit notation to Pint-compatible strings. Handles wrapper removal, fraction conversion, exponent conversion, and multiplication symbols.

### ISS-006: Incompatible unit operations silently produce wrong results

**Resolved:** 2026-01-11 - Fixed in Phase 2
**Solution:** Added dimensional compatibility checking. Pre-checks dimensions before addition/subtraction operations. Incompatible unit operations now produce clear error messages.

---

*Last reviewed: 2026-01-12 (issues triaged for v1.3)*
