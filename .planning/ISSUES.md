# Project Issues Log

Enhancements discovered during execution. Not critical - address in future phases.

## Open Enhancements

### ISS-013: Inline unit hint syntax lost after processing, breaks re-processing

- **Discovered:** 2026-01-12 (during testing)
- **Type:** Bug
- **Description:** When using inline unit hint syntax `$E == [kJ]$`, the hint is extracted during processing and removed from the output. When re-processing the output file, the unit hint is missing, causing the result to fall back to SI base units instead of the requested unit. HTML comment syntax `<!-- [kJ] -->` works correctly because it remains in the output. The inline syntax should either: (1) be preserved in the output as HTML comment (auto-convert), or (2) be restored when clearing processed output, or (3) be preserved in some other way that survives re-processing.
- **Impact:** High (inline syntax is recommended but breaks re-processing workflow)
- **Effort:** Medium
- **Suggested phase:** v1.3
- **Files to change:**
  - `src/livemathtex/core.py` - Preserve inline unit hints in processed output (convert to HTML comment or restore inline syntax)
  - `src/livemathtex/render/markdown.py` - Ensure unit hints are preserved in rendered output
  - `tests/test_inline_unit_hints.py` - Add test for re-processing with inline hints
- **Example:**
  - Input: `$F_2N_inline := F_2 == [N]$`
  - After processing: `$F_2N_inline := F_2 == 245.2\ \text{N}$` (hint lost)
  - After re-processing: Falls back to SI base units (kg·m/s²) instead of N

### ISS-009: Compound unit definitions with division - evaluation lookup fails

- **Discovered:** Phase 2 (2026-01-11)
- **Updated:** 2026-01-12 (partially resolved)
- **Type:** Bug
- **Description:** Unit definitions (`===`) with division **now register correctly** with Pint. The issue has narrowed: division-based custom units work in combined `:= ==` syntax but fail in separate `$var ==` evaluation. The unit is registered (`is_known_unit('SEC') = True`), but the evaluator doesn't look it up correctly during standalone evaluation.
- **Impact:** Medium (workaround: use combined `:= ==` syntax)
- **Effort:** Medium (unit registration fixed, just need to fix evaluation lookup)
- **Suggested phase:** v1.3
- **Files to change:**
  - `src/livemathtex/engine/evaluator.py` - Fix custom unit lookup in evaluation
  - `tests/test_pint_backend.py` - Add compound unit definition tests
- **Example:**
  - Works: `$SEC_result := E / m ==$ <!-- [SEC] -->` → `5\ \text{SEC}`
  - Fails: `$ratio := E / m$` then `$ratio ==$ <!-- [SEC] -->` → `1.800e+10` (no unit)

## Closed Enhancements

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
