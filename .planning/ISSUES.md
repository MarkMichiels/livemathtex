# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

### ISS-012: Process/clear cycle produces unstable results and incorrect errors

- **Discovered:** Post-Phase 4 (2026-01-12)
- **Type:** Bug
- **Description:** When processing an already-processed output file multiple times, or after clearing it, unexpected changes occur. The file should remain stable (only timestamp should change) but instead: (1) Additional errors appear on repeated processing (Scenario 4: F9 on output.md second time), (2) File content changes after clearing and re-processing (Scenario 6: F9 after clear), (3) Error markup is not fully cleaned, causing parsing issues. Root causes: (a) `clear_text()` function doesn't remove all error markup formats (incomplete math blocks `\\ }$`, multiline errors), (b) Parser misinterprets error artifacts as math content, (c) No stability check for in-place processing, (d) Clear function doesn't restore file to exact input state. See `.planning/BUG_INVESTIGATION.md` for detailed analysis and test scenarios.
- **Impact:** High (affects core workflow: process → clear → re-process)
- **Effort:** Substantial
- **Suggested phase:** Future (after v1.1 milestone)
- **Files to change:**
  - `src/livemathtex/core.py` - Improve `clear_text()` error markup patterns, add stability check for in-place processing
  - `src/livemathtex/parser/lexer.py` - Handle error artifacts in math block parsing
  - `tests/test_process_clear_cycle.py` - Regression tests (already created, currently failing as expected)

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

## Closed Enhancements

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

*Last reviewed: 2026-01-12*

**Note:** ISS-012 bug investigation documented in `.planning/BUG_INVESTIGATION.md` with detailed test scenarios and root cause analysis.
