# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

---

### ISS-042: Better Unit Display Formatting

**Status:** Open (Feature Request)
**Created:** 2026-01-15
**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

**Description:**
Compound units are displayed in Pint's default format (e.g., `mg/d/L`) which may not match preferred scientific notation (e.g., `mg/(L·d)` or `mg·L⁻¹·d⁻¹`). Users should be able to control unit display format.

**Test file:** `tests/test_iss_042_unit_display_formatting.md`

**Expected:** Can control unit display format via configuration (e.g., `<!-- unit-format:fraction -->`)
**Actual:** Units are displayed in Pint's default format only

**Root cause:** Unit formatting uses Pint's default string representation without formatting options.

**Impact:** Low-Medium - Improves readability and matches scientific conventions. Some journals prefer specific unit formats.

**Feature Request:**
Add unit formatting options:
- Prefer fraction notation: `mg/(L·d)` instead of `mg/d/L`
- Use negative exponents: `mg·L⁻¹·d⁻¹`
- Configurable via `<!-- unit-format:fraction -->` or document setting
- Preserve user's unit hint format when possible

**Preferred:** Configurable option with sensible defaults.

**⚠️ CRITICAL REQUIREMENT:** Settings must be preserved after `process` and `clear` cycles (idempotence requirement). Unit format settings must remain in comments after `clear`.

---

### ISS-041: Array/Vector Operations for Repetitive Calculations

**Status:** Open (Feature Request)
**Created:** 2026-01-15
**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

**Description:**
Many documents have repetitive calculations for different values (e.g., years 2026-2030, multiple reactors). Currently, each calculation must be defined manually, leading to verbose code.

**Test file:** `tests/test_iss_041_array_operations.md`

**Expected:** Can define arrays and iterate over them to calculate values
**Actual:** Must manually define each calculation (e.g., `gamma_26`, `gamma_27`, etc.)

**Root cause:** LiveMathTeX doesn't support array/vector operations.

**Impact:** Medium - Reduces code duplication for repetitive calculations. Improves maintainability when values change.

**Feature Request:**
Add array/vector support:
- Define arrays: `$gamma := [15, 30.5, 34, 38, 44]\ mg/L/d$`
- Element access: `$gamma[0]$` or `$gamma_26$` (if array indexed by year)
- Vectorized operations: `$m := V_L \cdot gamma$` (element-wise multiplication)
- Array indexing: Support for named indices (e.g., `gamma[2026]`)

**Preferred:** Start with basic array support, then add vectorized operations.

**⚠️ CRITICAL REQUIREMENT:** Settings must be preserved after `process` and `clear` cycles (idempotence requirement). Array definitions must remain after `clear`, only calculated results removed.

---

### ISS-040: Cross-References to Calculated Values in Text

**Status:** Open (Feature Request)
**Created:** 2026-01-15
**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

**Description:**
Documents often need to reference calculated values in prose text (e.g., executive summaries, conclusions). Currently, variables in text are not evaluated, requiring manual copy-paste of calculated values.

**Test file:** `tests/test_iss_040_cross_references.md`

**Expected:** Can reference variables like `{{C_max}}` in text to display calculated values
**Actual:** Variables in text are not evaluated (or require full math block syntax)

**Root cause:** LiveMathTeX only processes math blocks (`$...$`), not inline variable references in text.

**Impact:** High - Enables "single source of truth" documents where calculated values automatically appear in executive summaries, conclusions, and other prose sections. Reduces manual errors from copy-paste.

**Feature Request:**
Add syntax for inline variable references in text:
- Option 1: `{{variable}}` syntax (e.g., `{{C_max}}` → `550 kg`)
- Option 2: `$variable$` in text (outside math blocks) gets evaluated
- Option 3: Special syntax like `\ref{C_max}` or `@C_max`

**Preferred:** Option 1 (`{{variable}}`) to distinguish from math blocks and allow unit formatting.

**⚠️ CRITICAL REQUIREMENT:** Settings must be preserved after `process` and `clear` cycles (idempotence requirement). After `clear`, `{{variable}}` syntax must be restored, not the evaluated value.

**Example:**
```markdown
The maximum capacity is **{{C_max}} kg/year**.
The 2030 target is **{{T_2030}} kg/year**, which is **{{T_2030 / C_max * 100}}%** of maximum.
```

---

### ISS-039: Thousands Separator Formatting

**Status:** Open (Feature Request)
**Created:** 2026-01-15
**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

**Description:**
Large numbers (>= 1000) are displayed without thousands separators, making them harder to read. For example, `37824` should be displayed as `37,824` (or `37 824` in European format).

**Test file:** `tests/test_iss_039_thousands_separator.md`

**Expected:** Numbers >= 1000 should display with thousands separators (e.g., `37,824` instead of `37824`)
**Actual:** Numbers are displayed without separators (e.g., `37824`)

**Root cause:** The number formatting in `_format_si_value()` and related functions doesn't add thousands separators.

**Impact:** Medium - Improves readability of large numbers in documents, especially for engineering calculations with values in thousands/millions.

**Feature Request:**
Add automatic thousands separator formatting:
- Option 1: Always format numbers >= 1000 with separators
- Option 2: Configurable via `<!-- format:thousands -->` or document setting
- Option 3: Use locale-aware formatting (US: comma, EU: space or period)

**Preferred:** Option 2 (configurable) with default enabled for numbers >= 1000.

**⚠️ CRITICAL REQUIREMENT:** Settings must be preserved after `process` and `clear` cycles (idempotence requirement).

---

### ISS-036: Variables with commas in subscripts fail with "argument of type 'Symbol' is not iterable" (potential regression of ISS-034)

**Status:** Open (needs investigation)
**Created:** 2026-01-15
**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

**Description:**
Variables with commas in subscripts (e.g., `PPE_{eff,9010}`) fail to parse/evaluate with error "argument of type 'Symbol' is not iterable" in certain contexts. Simple test cases work correctly, but complex expressions in the source document fail.

**Test file:** `tests/test_iss_036_comma_subscript_symbol_not_iterable.md`

**Note:** Simple test case passes (no errors), suggesting the bug may be context-dependent or require complex expressions to trigger.

**Expected:** Variables with commas in subscripts should parse and evaluate correctly (as ISS-034 claimed to fix)
**Actual:** Error: "Failed to parse LaTeX 'PPE_{eff,9010}': argument of type 'Symbol' is not iterable" (in complex expressions)

**Root cause:** Unknown - may be related to how Symbol objects are handled during parsing of complex expressions with variables containing commas in subscripts.

**Impact:** Medium - prevents using descriptive variable names with multiple subscripts in complex expressions.

**Related Issues:**
- ISS-034: Variable parsing fails for variables with commas in subscript (marked RESOLVED, but bug still occurs with different error in complex contexts)

---

### ISS-035: Multi-letter variable names in tables parsed as implicit multiplication

**Status:** Open (updated)
**Created:** 2026-01-14
**Updated:** 2026-01-14
**Source:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`

**Description:**
Multi-letter variable names (like `Cost`) in markdown table cells are parsed as implicit multiplication (`C*o*s*t`). This is a latex2sympy limitation, not a table-specific bug. The originally reported "Symbol not iterable" error no longer reproduces - actual errors are:
1. `Cost` → "Undefined variable 'Cost'. Note: 'Cost' was parsed as implicit multiplication (C*o*s*t)"
2. `k€` → "Undefined variable 'k'" (k is not a prefix for custom unit €)

**Error:**
```
Error: Undefined variable 'Cost'. Note: 'Cost' was parsed as implicit multiplication (C*o*s*t).
```

**Test file:** `tests/test_iss_035_symbol_not_iterable_in_tables.md`

**Root cause:**
1. **Multi-letter variable names:** latex2sympy parses `Cost` as `C*o*s*t` (implicit multiplication) - same as ISS-018
2. **Custom unit prefix:** `k€` doesn't work because Pint's SI prefix `k` doesn't apply to custom units

**Impact:** Medium - use subscripts for variable names (`Cost_{26}` instead of `Cost`) and define custom units with prefixes explicitly.

**Workaround:** Use subscripts: `Cost_{26}` instead of `Cost`. For k€, define explicitly: `k€ === 1000\ €`

**Note:** This is the same root cause as ISS-018 (implicit multiplication). Consider closing as duplicate.

---

## Closed Issues

### ISS-033: Variable name with superscript (R^2) conflicts with unit (molar_gas_constant ** 2)

**Resolved:** 2026-01-14 - Fixed in v2.1 Phase 22
**Solution:** Updated `check_variable_name_conflict()` in `pint_backend.py` to treat superscripts (`^`) the same as subscripts (`_`) for disambiguation purposes. Variable names containing `^` are now explicitly allowed without unit conflict checking. This allows common mathematical notation like `R^2` (coefficient of determination) without conflicting with unit expressions like `R**2` (molar_gas_constant ** 2).

### ISS-034: Variable parsing fails for variables with commas in subscript

**Resolved:** 2026-01-14 - Already fixed (verified during v2.1 build cycle)
**Solution:** Variables with commas in subscripts (e.g., `PAR_{R2,umol}`) now parse and evaluate correctly. Test case `PAR_{R2,umol} := 1413 µmol/s` followed by `PAR_{R2} := PAR_{R2,umol} \cdot t_{day}` produces correct result `122.0832 mol/d`. The fix was likely a side effect of earlier parser improvements.

### ISS-032: Function evaluation fails - "Cannot convert expression to float"

**Resolved:** 2026-01-14 - Fixed in v2.0 Phase 21
**Solution:** Three interrelated bugs fixed in `evaluator.py`:
1. Function name normalization in `_substitute_symbols` - normalized lookup key to match stored key
2. Function latex_name extraction - stored just the function name (e.g., `PPE_{eff}`) instead of full signature (`PPE_{eff}(r_{frac})`)
3. Internal ID reverse lookup - when expression is rewritten to use internal IDs like `f_{0}`, added reverse mapping to find original symbol

All 365 tests pass + 3 xpassed. Function calls like `PPE_{eff}(0.90)` now correctly evaluate to `3.765`.

### ISS-031: Unit propagation failure when multiplying unit by dimensionless value

**Resolved:** 2026-01-14 - Fixed as side effect of ISS-030 fix in v1.8 Phase 20
**Solution:** The regex fix in `_compute_with_pint` that resolved ISS-030 also fixed this issue. Testing confirms `PPE_{eff} := PPE_{red} \cdot f_{geom}` now correctly produces `3.9223 micromol/J` instead of treating the result as dimensionless. The SymPy symbol format mismatch was preventing proper unit lookup, which caused Pint evaluation to fail and fall back to SymPy (which doesn't preserve units).

### ISS-030: Unit conversion bug - µmol not converted to mol in JSON output

**Resolved:** 2026-01-13 - Fixed in v1.8 Phase 20
**Solution:** The root cause was a regex mismatch in `_compute_with_pint`. SymPy parses internal IDs differently:
- Single digit: `v_0` (no braces)
- Multi digit: `v_{15}` (with braces)

But our internal ID format always uses braces: `v_{0}`, `v_{1}`, `v_{15}`. Fixed regex from `r'^v_\{(\d+)\}$'` to `r'^v_\{?(\d+)\}?$'` to handle both formats. Also added ISS-013 inline unit hint tracking to `process_text_v3`. All 365 tests pass.

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

*Last reviewed: 2026-01-14 (All issues resolved, v2.0 complete)*
