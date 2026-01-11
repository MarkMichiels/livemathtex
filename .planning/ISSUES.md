# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

### ISS-007: Evaluation results show SI base units instead of requested output unit

- **Discovered:** Phase 2 (2026-01-11)
- **Type:** UX
- **Description:** When evaluating expressions with units, the result is displayed in SI base units (kg·m²/s²) instead of the user's preferred output unit specified in the `<!-- [unit] -->` comment. The evaluator computes in SI base units and formats the result directly. The `<!-- [unit] -->` comment is not parsed or used for unit conversion in the output.
- **Impact:** Medium (works correctly, but UX could be better)
- **Effort:** Medium
- **Suggested phase:** Phase 4 (Output Unit Conversion)
- **Files to change:**
  - `src/livemathtex/parser/lexer.py` - Parse output unit hints
  - `src/livemathtex/engine/evaluator.py` - Apply unit conversion before formatting
  - `src/livemathtex/engine/pint_backend.py` - Add conversion helper

### ISS-008: Output unit hint syntax requires HTML comment

- **Discovered:** Phase 2 (2026-01-11)
- **Type:** UX
- **Description:** The current syntax for specifying output units uses HTML comments (`<!-- [MWh] -->`), which is verbose, breaks reading flow, invisible in rendered Markdown, and easy to forget. Proposed: inline syntax like `$E == [MWh]$` where `[unit]` is parsed and replaced with the converted value.
- **Impact:** Low (works correctly, this would enhance)
- **Effort:** Quick
- **Suggested phase:** Phase 4 (after output unit conversion works)
- **Depends on:** ISS-007 (output unit conversion must work first)
- **Files to change:**
  - `src/livemathtex/parser/lexer.py` - Parse new syntax
  - `src/livemathtex/engine/evaluator.py` - Handle inline unit hints

### ISS-009: Compound unit definitions fail with division

- **Discovered:** Phase 2 (2026-01-11)
- **Type:** Refactoring
- **Description:** Unit definitions (`===`) with division fail to register correctly with Pint. Simple aliases work (`kWh === 1000\ Wh`), multiplied compounds work (`Wh === W \cdot hour`), but division compounds fail silently or produce errors (e.g., `PPE === umol/J`, `SEC === MWh/kg`). The `===` parser in `pint_backend.py` doesn't properly handle division (`/`) in unit expressions, compound units with multiple operators, or LaTeX-style parentheses.
- **Impact:** Medium (workaround exists: use dimensionless values)
- **Effort:** Substantial
- **Suggested phase:** Future
- **Files to change:**
  - `src/livemathtex/engine/pint_backend.py` - Extend `register_custom_unit()`
  - `tests/test_pint_backend.py` - Add compound unit definition tests

### ISS-010: Expose public Python API for library usage

- **Discovered:** Phase 2 (2026-01-08)
- **Type:** Refactoring
- **Description:** Currently, LiveMathTeX is primarily a CLI tool. The `__init__.py` only exports `main()`, making it difficult to use as a Python library in other projects. Should expose `process_text()`, `LivemathConfig`, and `LivemathIR` for programmatic usage.
- **Impact:** Medium (CLI works, library usage would enhance)
- **Effort:** Quick
- **Suggested phase:** Phase 3 (API Features)
- **Files to change:**
  - `src/livemathtex/__init__.py` - Add exports
  - `src/livemathtex/core.py` - Possibly simplify API
  - `README.md` - Document library usage
  - `docs/USAGE.md` - Add library examples

### ISS-011: `livemathtex clear` command to reset document calculations

- **Discovered:** Phase 2 (2026-01-08)
- **Type:** UX
- **Description:** After running `livemathtex process`, the document contains computed values and error messages. When errors occur or the document needs resetting, there is no command to clean it back to the original state. Should add `livemathtex clear` command that removes computed values after `==`, removes error markup, and preserves all definitions and structure.
- **Impact:** Medium (manual workaround exists)
- **Effort:** Medium
- **Suggested phase:** Phase 3 (API Features)
- **Files to change:**
  - `src/livemathtex/cli.py` - Add `clear` subcommand
  - `src/livemathtex/core.py` - Add `clear_text()` function
  - `.cursor/commands/livemathtex.md` - Document new command

## Closed Enhancements

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

*Last reviewed: 2026-01-11*
