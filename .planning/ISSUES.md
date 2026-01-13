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

### ISS-018: Implicit multiplication of multi-letter identifiers causes misleading unit/variable errors

- **Discovered:** 2026-01-12 (during astaxanthin production analysis document processing)
- **Type:** Parser/UX
- **Description:** LiveMathTeX uses `latex2sympy` to parse expressions. In math-mode, **bare multi-letter identifiers** can be interpreted as **implicit multiplication** (e.g., `PPE` → `P·P·E`, `PAR` → `P·A·R`). This produces confusing errors such as:
  - `Undefined variable 'A' (A is also a unit: ampere)` when a user intended the symbol `PAR`
  - Similar confusion for other “word-like” symbols and for unit-like tokens inside expressions when not structured

  This is particularly confusing because:
  - The name is rendered “correctly” in Markdown, but the parser interprets it differently.
  - The internal symbol rewrite (`v_{n}` mapping) only protects **already-known** symbols; a bare multi-letter token used before it exists in the symbol table is vulnerable.

  **Expected behavior:** Multi-letter identifiers should either:
  - Be treated as a single symbol (preferred), or
  - Fail with a targeted, high-signal error explaining the implicit-multiplication interpretation and how to fix it.

  **Recommended user-side pattern (today):** prefer structured names like `X_{...}` (e.g., `PPE_{eff}`, `PAR_{rct}`) and define symbols before use.
- **Minimal reproduction (current behavior):**
  - **Works (defined above → protected by `v_{n}` rewrite):**
    - `$PPE := 1$`
    - `$x := PPE$`
  - **Fails (NOT defined yet → `latex2sympy` interprets as multiplication):**
    - `$x := PPE$`  → interpreted as `P·P·E` → error on `P`
    - `$x := PAR$`  → interpreted as `P·A·R` → error on `A` (ampere collision)
- **Impact:** Medium (hard-to-debug errors, especially when letters collide with units like `A` ampere)
- **Effort:** Medium
- **Suggested phase:** v1.4
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - In `_compute()`, improve handling of bare multi-letter identifiers:
    - Option A: pre-tokenize and wrap unknown multi-letter identifiers as `\text{...}` (or another safe representation) before `latex2sympy`, then map them to symbols.
    - Option B: detect the implicit-multiplication pattern in the parsed expression (e.g., `P*P*E`) and raise a specialized error message.
  - `src/livemathtex/engine/pint_backend.py` - Reuse/enhance the “conflicts with unit” messaging to also cover implicit-multiplication cases.
  - `livemathtex/.cursor/commands/livemathtex.md` - Document this pitfall clearly (already partially addressed; keep in sync with final behavior).
  - `tests/` - Add regression tests that demonstrate:
    - `$x := PPE$` raises a targeted error (or parses as one symbol if we implement Option A)
    - `$x := PAR$` same, and does not degrade into an `A`/ampere confusion

### ISS-022: Improve diagnostics when multi-letter identifiers are split as implicit multiplication (report intended unknown symbol)

- **Discovered:** 2026-01-13 (during `astaxanthin_production_analysis.md` debugging)
- **Type:** UX/Error Handling
- **Description:** When a user writes a bare multi-letter identifier as an expression (e.g., `PPE`, `PAR`) and it has not been defined yet, `latex2sympy` may parse it as implicit multiplication (`P*P*E`, `P*A*R`). Today, LiveMathTeX then reports misleading errors such as:
  - `Undefined variable 'P'` (or `Undefined variable 'A' (ampere)`)

  In most cases, the correct user intent is: **"unknown variable `PPE`"** (or `PAR`), not `P`/`A`.

  **Expected behavior:** Detect this failure mode and produce a targeted message like:
  - `Undefined variable 'PPE'. Note: 'PPE' was parsed as implicit multiplication (P*P*E). Define '$PPE := ...$' before use, or use a structured name like 'PPE_{...}'.`

  This is strictly a diagnostics improvement (no behavior change required).
- **Impact:** Medium (dramatically reduces confusion and speeds up debugging)
- **Effort:** Medium
- **Suggested phase:** v1.4
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - In `_check_undefined_symbols()` (or immediately after parsing in `_compute()`), detect patterns where:
    - the original expression contains a contiguous multi-letter token (e.g., `PPE`, `PAR`)
    - but the parsed SymPy expression contains only single-letter undefined symbols consistent with implicit multiplication
    - then raise a specialized `EvaluationError` with the intended multi-letter symbol name.
  - `src/livemathtex/engine/pint_backend.py` - Ensure the "conflicts with unit" helper messaging does not hide the more specific "intended multi-letter symbol" hint.
  - `tests/` - Add regression tests:
    - `$x := PPE$` should mention `PPE` in the error message (not only `P`)
    - `$x := PAR$` should mention `PAR` (not only `A`/ampere)

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

### ISS-023: `_format_si_value()` produces malformed LaTeX causing KaTeX parse errors

- **Discovered:** 2026-01-13 (during `astaxanthin_production_analysis.md` processing)
- **Type:** Bug
- **Description:** When unit conversion fails and `UnitConversionWarning` is raised, the system displays the SI value using `_format_si_value()`. This method attempts to clean up LaTeX output from SymPy by removing `\text{}` wrappers, but the implementation is too aggressive: it removes **all** closing braces `}`, not just the ones matching `\text{` openings. This breaks LaTeX syntax and causes KaTeX parse errors in rendered output.

  **Example of the bug:**
  - SymPy LaTeX output: `\frac{7.62969 \times 10^{7} \text{kg}}{\text{m}^{3}}`
  - After `.replace('\\text{', '')`: `\frac{7.62969 \times 10^{7} kg}{m^{3}}` (correct)
  - After `.replace('}', '')`: `\frac{7.62969 \times 10^{7} kg{m^{3` (MALFORMED - missing closing braces)
  - Result: KaTeX parse error `Expected '}', got 'EOF'`

  **Current code (line 1339):**
  ```python
  result = result.replace('\\cdot', '*').replace('\\text{', '').replace('}', '')
  ```

  **Expected behavior:** The SI value should be displayed in valid LaTeX that KaTeX can parse. The cleanup should only remove `\text{}` wrappers (matching pairs), not all closing braces.

  **Impact:** High (renders documents with KaTeX parse errors, making them unreadable in Markdown viewers)
- **Effort:** Quick (fix the cleanup logic)
- **Suggested phase:** v1.4 (hotfix)
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - Fix `_format_si_value()` method (line 1320-1343):
    - Option A: Use regex to match and remove only `\text{...}` pairs: `re.sub(r'\\text\{([^}]+)\}', r'\1', result)`
    - Option B: Keep SymPy's LaTeX output as-is (it's already valid LaTeX) and only replace `\cdot` with `*` if needed
    - Option C: Use a proper LaTeX parser/cleaner to safely remove `\text{}` wrappers
  - `tests/test_unit_conversion.py` - Add test that verifies SI fallback output is valid LaTeX (can be parsed by KaTeX or similar)
- **Example:**
  - Current: `$E == \frac{7.62969 * 10^{7 kg{m^{3\n\\ \color{orange}{\text{Warning: ...}}}$` (KaTeX parse error)
  - Expected: `$E == \frac{7.62969 \times 10^{7} \text{kg}}{\text{m}^{3}}\n\\ \color{orange}{\text{Warning: ...}}}$` (valid LaTeX)

### ISS-019: Adopt a parsing library and reduce regex-driven logic across the pipeline (variables vs units vs formulas)

- **Discovered:** 2026-01-13 (during `astaxanthin_production_analysis.md` debugging)
- **Type:** Architecture/Refactoring
- **Description:** A recurring theme is that we need to reliably answer questions like:
  - “Is this token a variable, a unit, or part of a formula?”
  - “Does this variable already exist in the symbol table?”
  - “Where is the exact boundary of a math block and its result/error markup?”

  Today, many of these decisions are made with **regex + heuristics**, which is fragile and hard to test. This fragility shows up across features (not only `clear`), e.g.:
  - accidental block merging / orphan fragments when cleaning (ISS-021)
  - ambiguous parsing of identifiers vs units (variable-name conflicts, implicit multiplication)
  - difficulty making idempotent edits safely

  **Proposal:** Introduce a dedicated parsing layer (library-backed or a significantly upgraded lexer) that provides a structural representation with spans/offsets, and migrate regex-heavy operations to that layer. Goal: keep documents **clean** (no extra visible markup), but make behavior deterministic and testable.

  **Candidate approach:**
  - Use a real Markdown parser library (e.g., `markdown-it-py` or `mistune`) to get an AST and robustly ignore code fences, lists, nested constructs, etc.
  - Extract math blocks as first-class nodes with exact source spans.
  - Within math blocks, parse calculations into an internal structure (operators, lhs/rhs/result spans).
  - Centralize “token classification” (unit vs variable vs function) so it is not duplicated across regexes.

  **Non-goal:** Adding heavy visible markup to documents. This is internal plumbing to reduce bug surface area.
- **Impact:** High (reduces bug surface area and makes future features safer)
- **Effort:** Substantial
- **Suggested phase:** Future / v1.5+
- **Files to change:**
  - `src/livemathtex/parser/*` - Integrate library-backed parsing (or upgrade current parsing to AST + spans).
  - `src/livemathtex/core.py` - Replace regex-driven logic with structural operations where possible (`clear`, idempotency checks, directive scanning).
  - `src/livemathtex/engine/*` - Consolidate unit/variable token classification paths.
  - `tests/` - Add golden tests for representative documents to validate parsing decisions and idempotency.

### ISS-020: Refactor to structural parsing for safe in-place editing (reduce regex fragility across the pipeline)

- **Discovered:** 2026-01-13 (during SEC/Cost corruption investigation)
- **Type:** Architecture/Refactoring
- **Description:** Several issues (notably ISS-021) stem from using regex-based text rewriting for operations that are inherently structural (math-block boundaries, multiline error insertions, adjacent expressions, etc.). We want to keep documents **clean** (no extra visible markup), but still make processing/clearing robust.

  **Proposal:** Move more of the pipeline from “string regex rewrite” to “structural parse + span-based editing”:
  - Parse the Markdown into nodes (text blocks + math blocks) **with exact source spans (start/end offsets)**.
  - Within each math block, parse into calculations and track the exact span of:
    - the operator (`:=`, `==`, `===`, `=>`)
    - the rendered “result part” that was inserted after `==`
    - any error markup that was injected by LiveMathTeX
  - Implement `clear` by operating on spans/nodes, not by regexing raw text. This preserves line boundaries and prevents accidental merges like `...$SEC_{27}...`.

  This does **not** require adding extra markup to the user document. It is an internal refactor to make edits deterministic and testable.

  **Optional extension:** Evaluate adopting a dedicated Markdown parser library (e.g., `markdown-it-py` or `mistune`) to reduce edge cases (code fences, nested constructs), while still extracting `$...$` and `$$...$$` math regions.

- **Impact:** High (reduces fragility across process/clear/idempotency and makes future features safer)
- **Effort:** Substantial
- **Suggested phase:** Future / v1.5+
- **Files to change:**
  - `src/livemathtex/parser/*` - Track spans/offsets for `MathBlock` and per-calculation segments.
  - `src/livemathtex/core.py` - Replace regex-based `clear_text()` with span-based clearing.
  - `src/livemathtex/render/markdown.py` - Optionally support “structured render” to attach results without losing boundaries.
  - `tests/` - Add high-signal golden tests: “process → clear → process is idempotent” on representative docs (including multiline errors).

## Closed Issues

### ISS-021: `livemathtex clear` can corrupt documents around multiline error blocks ✅ FIXED

- **Discovered:** 2026-01-13
- **Resolved:** 2026-01-13 (Phase 10)
- **Type:** Bug
- **Resolution:** Rewrote `clear_text()` to use span-based operations with Phase 8/9 parsers instead of regex-based structural matching. The new implementation properly identifies math block boundaries using AST parsing, eliminating document corruption around multiline error blocks.
- **See:** `.planning/phases/10-clear-refactor/10-01-SUMMARY.md`


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
