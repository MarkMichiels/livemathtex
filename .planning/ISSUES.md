# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

### ISS-017: Unit conversion failures need better diagnostics and should be warnings, not errors

- **Discovered:** 2026-01-12 (during document processing)
- **Type:** UX/Error Handling
- **Description:** Unit conversion failures currently show generic error messages that don't indicate the current unit of the value. For example, when converting `mol` to `mol/day` fails, the error only says "Unit conversion failed for 'mol/day'" without mentioning that the value is currently in `mol`. Additionally, unit conversion failures are treated as errors (red) even when the calculation itself succeeds (value can be converted to SI base units) - these are formatting/display issues, not calculation failures. **Solution approach:** Instead of attempting automatic unit manipulation (like MadCraft/S-MAD does), show a clear warning with the current unit and display the value in SI units. The system should:
  1. Extract and show the current unit from the value before attempting conversion (e.g., "Cannot convert from 'mol' to 'mol/day'")
  2. Distinguish between calculation errors (value cannot be computed) and formatting warnings (value computed but display conversion fails)
  3. For formatting failures, show the value in SI base units with a warning (different color than red, e.g., orange/yellow) instead of an error
  4. Update error counting to distinguish errors from warnings
- **Impact:** Medium (user confusion, difficulty debugging unit issues, misleading error reporting)
- **Effort:** Medium
- **Suggested phase:** v1.4
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - Enhance `_apply_conversion()` to extract and report current unit from `value` before attempting conversion. Add logic to distinguish calculation errors vs formatting failures. Use warning color (orange/yellow) instead of error color (red) for formatting failures.
  - `src/livemathtex/engine/evaluator.py` - When formatting conversion fails, return value in SI base units with warning message instead of raising error.
  - `src/livemathtex/core.py` - Update error counting to distinguish errors from warnings (separate counters or metadata).
  - `tests/test_unit_conversion.py` - Add tests for improved warning messages and warning behavior (non-red color, SI unit display).
- **Example:**
  - Current: `Error: Unit conversion failed for 'mol/day': Cannot convert expression to float.`
  - Expected: `Warning: Cannot convert from 'mol' (total) to 'mol/day' (rate) - dimensions incompatible. Showing value in SI: 650.67 mol` (in orange/yellow, not red)

## Closed Enhancements

### ISS-015: User documentation incomplete/outdated

**Resolved:** 2026-01-12 - Fixed in v1.4 Phase 7
**Solution:** Updated docs/USAGE.md with comprehensive documentation for v1.2-v1.4 features:
- Added `clear_text()` and `detect_error_markup()` to Python API documentation
- Documented auto-cleanup behavior for idempotent processing
- Added Unit redefinition and Variable name conflict to error types table
- Verified all 8 examples process successfully
- All existing syntax (inline unit hints, HTML comments, custom units) was already documented

### ISS-016: Error markup in input document not detected or cleaned

**Resolved:** 2026-01-12 - Fixed in v1.4 Phase 6
**Solution:** Added pre-processing to `process_text()` that matches existing `process_file()` behavior - checks for `\color{red}` or `livemathtex-meta` and calls `clear_text()` before parsing. Added `detect_error_markup()` function for programmatic inspection of documents. 9 tests added in `tests/test_error_markup.py`.

### ISS-014: Unit conversion fails for recursively defined units (MWh, mol/day, etc.)

**Resolved:** 2026-01-12 - Verified fixed in v1.4 Phase 5
**Solution:** Investigation during Phase 5 revealed that ISS-014 was already fixed as a side effect of the ISS-009 fix in v1.3. The `_parse_unit_expression` fix to resolve prefixed units via `pint_to_sympy_with_prefix` also enables proper handling of recursive units like MWh and compound units like mol/day. Added 6 tests in `TestRecursiveUnitConversion` and `TestUnitConversionEdgeCases` classes to verify and prevent regression.

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
