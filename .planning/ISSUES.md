# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

### ISS-024: Numerical calculations produce incorrect results due to using SymPy instead of Pint

- **Discovered:** 2026-01-13 (during `astaxanthin_production_analysis.md` processing)
- **Type:** Architecture/Bug (Major Refactoring Required)
- **Description:** All calculation problems stem from a fundamental architectural issue: **LiveMathTeX uses SymPy for numerical calculations, but SymPy is designed for symbolic mathematics, not numerical computation**. This causes incorrect results, especially with unit propagation (rate × time calculations fail).

  **Core Problem:**
  - SymPy is designed for symbolic math (differentiation, integration, simplification)
  - SymPy is NOT designed for numerical calculations with units
  - Unit propagation in SymPy is symbolic and doesn't automatically convert (e.g., `day` stays `day`, doesn't become `seconds`)
  - Pint is already present in the codebase and handles numerical calculations with units correctly

  **Evidence:**
  - **Example bug:** `m_{26} = 49,020 g/day` × `d_{op} = 365 d` → Expected: `16,103 kg`, Actual: `0.1864 kg` (86,400x too low)
  - **Pint test:** `49020 g/day * 365 day * 0.9` → `16,103.07 kg` ✅ CORRECT
  - **SymPy test:** Same calculation → `0.1864 kg` ❌ WRONG
  - **Root cause:** SymPy treats `365 * day` as symbolic expression, doesn't convert to `31,536,000 * second` automatically

  **All problems are symptoms of this architectural choice:**
  - Unit conversion failures (ISS-014, ISS-017)
  - Incorrect numerical results (this issue)
  - Unit propagation bugs (rate × time calculations)
  - Performance issues (SymPy is slow for numerical calculations)

  **Solution (from PINT_MIGRATION_ANALYSIS.md - Option B):**
  - **Keep `latex2sympy2` as parser only** (LaTeX → expression tree)
  - **Use Pint Quantities for numerical evaluation** (not SymPy)
  - **Keep SymPy only for symbolic operations** (`=>` mode: differentiation, integration)

  **Impact:** Critical (all numerical calculations are potentially incorrect, making documents unreliable for engineering use)
- **Effort:** Substantial (major refactoring of evaluation engine)
- **Suggested phase:** v2.0 (major architectural change)
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - Major refactoring:
    - Replace SymPy numerical evaluation with Pint-based evaluation
    - Keep `latex2sympy2` for parsing LaTeX → expression tree
    - Build evaluator that walks SymPy AST and evaluates with Pint Quantities
    - Keep SymPy only for `=>` symbolic mode (separate pipeline)
  - `src/livemathtex/engine/symbols.py` - Update `SymbolValue`:
    - Store values as Pint Quantities (not SymPy Quantities)
    - Update `value_with_unit` to return Pint Quantity
  - `src/livemathtex/engine/pint_backend.py` - Enhance:
    - Add `evaluate_expression_with_pint()` function that takes SymPy AST and evaluates with Pint
    - Ensure all unit conversions use Pint (already mostly done)
  - `tests/test_numerical_calculations.py` - Comprehensive tests:
    - Rate × time: `$m := 49020\ g/day$` then `$C := m \cdot 365\ d ==$` → `16,103 kg`
    - Energy calculations: `$P := 310.7\ kW$` then `$E := P \cdot 8760\ h ==$` → correct MWh
    - All existing examples must pass with Pint evaluation
  - Update all documentation to reflect Pint-based numerical evaluation
- **References:**
  - `.planning/history/PINT_MIGRATION_ANALYSIS.md` - Option B (recommended approach)
  - Current architecture uses SymPy for everything (needs to change)
- **Example:**
  - Current (SymPy): `$C_{26} := m_{26} \cdot d_{op} \cdot u_{max} == 0.1864\ \text{kg}$` ❌ WRONG
  - Expected (Pint): `$C_{26} := m_{26} \cdot d_{op} \cdot u_{max} == 16\,103\ \text{kg}$` ✅ CORRECT

## Closed Issues

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

*Last reviewed: 2026-01-13 (v1.5 issues closed, v1.6 issues scheduled)*
