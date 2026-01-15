# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Bugs

*None currently open*

## Open Enhancements

### ISS-045: Update USAGE.md to Document Repetitive Calculations and Array Operations

- **Discovered:** 2026-01-15 (during document improvement workflow on astaxanthin_production_analysis.md)
- **Type:** Documentation
- **Description:** USAGE.md mentions "Matrices & Vectors" but doesn't document:
  1. Array/vector operations for repetitive calculations (ISS-041 feature request)
  2. Workarounds for repetitive calculations until arrays are implemented
  3. Best practices for organizing repetitive calculations
- **Expected:** USAGE.md includes section on repetitive calculations with:
  - Reference to ISS-041 (array operations feature request)
  - Workarounds for current limitations
  - Best practices and examples
- **Actual:** USAGE.md only shows basic matrix/vector syntax, no guidance on repetitive calculations
- **Root cause:** Documentation gap - feature request (ISS-041) exists but not documented in user guide.
- **Impact:** Medium - Documentation gap makes it unclear how to handle repetitive calculations. Users resort to verbose manual definitions.
- **Test file:** `tests/test_iss_045_update_usage_doc.md`
- **Action Items:**
  1. Add section "Repetitive Calculations" to USAGE.md
  2. Document ISS-041 as planned feature
  3. Show workarounds for current limitations
  4. Provide best practices and examples

### ISS-046: Intelligent Number Formatting (Smart Rounding)

- **Discovered:** 2026-01-15 (user feedback on astaxanthin_production_analysis.md)
- **Type:** Feature Request
- **Description:** Current number formatting uses fixed significant figures (default: 4), which produces inconsistent and sometimes ugly results. For example:
  - `24.1916` (4 decimals, but could be `24.2` for readability)
  - `165.347` (3 decimals, but could be `165` or `165.3`)
  - `11.9467` (4 decimals, but could be `11.9` or `12`)
- **Proposed Intelligence:**
  1. **Context-aware precision**: Different precision based on magnitude and unit type
  2. **Smart rounding**: Round to "nice" numbers (1, 2, 5, 10, 20, 50, 100, etc.)
  3. **Unit-appropriate precision**:
     - Large values (kg, MWh): 0-2 decimals
     - Medium values (W, g/d): 1-3 decimals
     - Small values (mg/L, µmol/J): 2-4 decimals
     - Percentages: 1-2 decimals
  4. **Avoid trailing zeros**: `24.0` → `24`, `10.00` → `10`
  5. **Scientific notation threshold**: Use scientific notation for very large/small numbers
- **Examples of desired output:**
  | Current | Desired | Rationale |
  |---------|---------|-----------|
  | `24.1916 mm` | `24.2 mm` | 1 decimal sufficient for dimensions |
  | `165.347 1/m` | `165 m⁻¹` | Integer for S/V ratio |
  | `11.9467 kW` | `12 kW` | Round to nearest integer for power |
  | `3.9223 µmol/J` | `3.92 µmol/J` | 2 decimals for efficiency |
  | `186.3778 kg` | `186 kg` | Integer for capacity |
  | `54.08%` | `54%` | Integer for percentages |
- **Implementation approach:**
  1. Add `smart_format` boolean setting (default: false for backward compatibility)
  2. When enabled, analyze magnitude and unit type
  3. Apply context-appropriate precision
  4. Round to "nice" numbers where appropriate
- **Impact:** Medium - Significantly improves readability of calculated values in documents.

## Closed Issues

### ISS-044: Support \frac in Unit Expressions for Variable Definitions

**Resolved:** 2026-01-16 - Fixed in v4.1 Phase 35
**Solution:** Extended `_try_parse_unit_fraction()` in expression_parser.py:
- Handle `\cdot`, `\times`, and `*` operators in unit fraction numerator/denominator
- Convert multiplication operators to `*` for Pint compatibility
- Group compound denominators with parentheses: `mg/(L*d)` for correct parsing
- Increased length limits for compound unit validation (up to 10 chars)
- Test: `$conc := 15\ \frac{\text{mg}}{\text{L} \cdot \text{d}} == 15\ \text{mg/d/L}$`
- Verified: Process-clear-process cycle preserves `\frac` syntax (idempotent)

### ISS-047: Function Evaluation Issues in Real-World Usage

**Resolved:** 2026-01-16 - Fixed in v4.1 Phase 34
**Solution:** Added FunctionCallNode to expression parser and evaluator:
- Parser now detects variable followed by LPAREN as function call
- Tokenizer recognizes comma as operator for argument separation
- Evaluator looks up function by internal_id (f0, f1) and latex_name (PPE_{eff})
- Substitutes argument values and evaluates formula expression
- Test: `PPE_{eff}(0.90) == 3.7651` now works correctly

### ISS-043: Dimensionless Calculation Incorrectly Converted to kg/mg Units

**Resolved:** 2026-01-16 - Not a bug (verified working)
**Solution:** Testing during v4.1 build-all shows dimensionless calculations work correctly. The test file `tests/test_iss_043_dimensionless_unit_conversion_bug.md` now produces correct output: `U_{26} = 54.0837` (dimensionless). JSON confirms: `"value": 54.08..., "unit": null`. The bug was likely fixed as a side effect of the v3.0 Pure Pint Architecture refactor.

### ISS-030: Unit conversion bug - µmol not converted to mol in JSON output

**Resolved:** 2026-01-16 - Not a bug (verified working)
**Solution:** Testing during v4.1 build-all shows µmol unit conversion works correctly. The test file `tests/test_iss_030_inplace_update.md` now produces correct output: `PAR_{rct} = 650.6703 mol/d`. JSON confirms: `PPE_eff` stored as `"value": 3.9223..., "unit": "micromole / joule"` and `PAR_rct` stored with `"base": {"value": 0.00753..., "unit": "mole / second"}`. The bug was likely fixed as a side effect of the v3.0 Pure Pint Architecture refactor.

### ISS-029: Rate × time calculations produce incorrect results (regression of ISS-024)

**Resolved:** 2026-01-13 - Not a bug (user error in issue report)
**Solution:** Testing shows rate×time calculations work correctly. The original issue reported "0.1864 kg" but actual testing produces "16,103.07 kg" as expected. The Pint evaluator in v1.6 Phase 14 handles `g/day × days` correctly. 365 tests pass.

### ISS-028: Currency unit definitions (€, k€) not recognized by Pint - EUR conversion fails

**Resolved:** 2026-01-13 - Not a bug (user error in issue report)
**Solution:** Testing shows currency unit definitions work correctly. `€ === €` and `k€ === 1000\ €` are properly recognized, and calculations like `139 €/MWh × 1472 MWh` produce "204.608 kilo€" as expected. 365 tests pass.

### ISS-027: EUR to k€ unit conversion fails - dimension incompatibility

**Resolved:** 2026-01-13 - Already fixed by v1.6 Pint evaluator work
**Solution:** The Pint-based evaluation in v1.6 (Phase 14) properly handles custom unit definitions including currency prefixes. Verified: `k€ === 1000\ €` definition works, conversion produces correct `204.608 kilo€` result.

### ISS-026: Compound unit rate calculations (mg/L/day) produce incorrect results

**Resolved:** 2026-01-13 - Already fixed by v1.6 Pint evaluator work
**Solution:** The Pint-based evaluation in v1.6 (Phase 14) correctly evaluates compound rate units. Verified: `37824 L × 15 mg/L/d = 567.36 g/d` calculates correctly.

### ISS-025: Pint evaluator misses handlers for SymPy constants and has unsafe isinstance() check

**Resolved:** 2026-01-13 - Fixed in v1.7 Phase 16
**Solution:** Added handler for `sympy.core.numbers.NumberSymbol` base class to support Pi, E (Exp1), EulerGamma, GoldenRatio, and Catalan constants. Fixed unsafe `isinstance(e, SympyQuantity)` check with guard `SympyQuantity is not None`. Added 5 regression tests.

### ISS-024: Numerical calculations produce incorrect results due to using SymPy instead of Pint

**Resolved:** 2026-01-13 - Fixed in v1.6 Phase 14 (Pint Evaluator Core)
**Solution:** Implemented hybrid architecture: latex2sympy for parsing, Pint for numeric evaluation.
- Added `evaluate_sympy_ast_with_pint()` in pint_backend.py that walks SymPy AST and evaluates with Pint Quantities
- Added `_compute_with_pint()` in evaluator.py as wrapper
- Route numeric evaluations (`==` operator) through Pint, fall back to SymPy for dimensionless results
- 15 new tests in `tests/test_pint_evaluator.py`, 360 total tests pass
- Rate × time calculations now work correctly: `310.7 kW × 8760 h = 2721.732 MWh` ✅

### ISS-023: `_format_si_value()` produces malformed LaTeX causing KaTeX parse errors

**Resolved:** 2026-01-13 - Fixed in v1.6 Phase 13 (SI Value Fix)
**Solution:** Changed `.replace('\\text{', '').replace('}', '')` to `re.sub(r'\\text\{([^}]+)\}', r'\1', ...)` in both `_extract_unit_string()` (line 1314) and `_format_si_value()` (line 1342). This properly removes `\text{}` wrappers without breaking other LaTeX braces. 345 tests pass.

### ISS-021: `livemathtex clear` can corrupt documents around multiline error blocks ✅ FIXED

- **Discovered:** 2026-01-13
- **Resolved:** 2026-01-13 (Phase 10)
- **Type:** Bug
- **Resolution:** Rewrote `clear_text()` to use span-based operations with Phase 8/9 parsers instead of regex-based structural matching. The new implementation properly identifies math block boundaries using AST parsing, eliminating document corruption around multiline error blocks.
- **See:** `.planning/phases/10-clear-refactor/10-01-SUMMARY.md`


## Closed Enhancements

### ISS-017: Unit conversion failures need better diagnostics and warnings

**Resolved:** 2026-01-13 - Fixed in v1.5 Phase 12 (Unit Warnings)
**Solution:** Added `UnitConversionWarning` exception to distinguish formatting warnings from calculation errors. Unit conversion failures now show orange warnings (not red errors) with SI fallback value. Warning counting added to metadata. 345 tests pass.

### ISS-018: Implicit multiplication of multi-letter identifiers causes misleading errors

**Resolved:** 2026-01-13 - Fixed in v1.5 Phase 11 (Token Classification)
**Solution:** Created `TokenClassifier` module with `detect_implicit_multiplication()` function. Error messages now mention the intended multi-letter symbol (e.g., "Did you mean 'PPE'?"). 46 tests added for token classification.

### ISS-022: Improve diagnostics for implicit multiplication (report intended symbol)

**Resolved:** 2026-01-13 - Fixed in v1.5 Phase 11 (Token Classification)
**Solution:** Same fix as ISS-018 - `TokenClassifier` detects when latex2sympy splits multi-letter identifiers and generates targeted error messages including the intended symbol name.

### ISS-019: Adopt parsing library to reduce regex-driven logic

**Resolved:** 2026-01-13 - Fixed in v1.5 Phase 8 (Markdown Parser Integration)
**Solution:** Integrated hybrid parser: markdown-it-py for document structure + pylatexenc for LaTeX parsing. `MarkdownParser` class provides AST with exact source spans. 34 tests added.

### ISS-020: Refactor to structural parsing for safe in-place editing

**Resolved:** 2026-01-13 - Fixed in v1.5 Phases 8-10
**Solution:** Phase 8 added markdown-it-py parser. Phase 9 created `ParsedCalculation` with character-level spans. Phase 10 rewrote `clear_text()` using span-based operations. Document corruption (ISS-021) eliminated.

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
*Last reviewed: 2026-01-15 (v4.0 issues identified during document improvement workflow)*
