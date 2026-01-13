# Changelog

All notable changes to LiveMathTeX are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-01-13

### Fixed

- **ISS-024: Numerical calculations now use Pint for evaluation** - Rate x time calculations (e.g., kW x h = MWh) now produce correct results. Previously, SymPy-based evaluation didn't properly handle unit cancellation, leading to incorrect values (e.g., 86,400x errors for day-based calculations).

- **ISS-023: Fixed LaTeX cleanup in `_format_si_value()`** - Replaced naive string replacement with regex to properly remove `\text{}` wrappers without breaking other LaTeX braces.

### Changed

- Numerical evaluation now uses a hybrid architecture: latex2sympy for parsing LaTeX to SymPy AST, then Pint for numeric evaluation with proper unit handling.
- Dimensionless results fall back to SymPy formatting to preserve format settings (scientific/engineering notation).

### Added

- New `evaluate_sympy_ast_with_pint()` function in pint_backend.py for walking SymPy AST and evaluating with Pint Quantities.
- 15 new tests in `tests/test_pint_evaluator.py` covering rate x time calculations, unit conversions, and compound expressions.
- Documentation for rate x time calculations in docs/USAGE.md.

## [1.5.0] - 2026-01-13

### Added

- **Markdown Parser Integration** - Hybrid parser using markdown-it-py for document structure and pylatexenc for LaTeX parsing.
- **Structural Math Parsing** - `ParsedCalculation` dataclass with character-level spans for precise document editing.
- **Token Classification** - `TokenClassifier` module for detecting implicit multiplication of multi-letter identifiers.
- **Unit Warnings** - Dimension mismatches now show orange warnings with SI fallback values.

### Fixed

- **ISS-021: Document corruption around multiline error blocks** - Rewrote `clear_text()` to use span-based operations.
- **ISS-018/ISS-022: Implicit multiplication diagnostics** - Error messages now mention the intended multi-letter symbol.
- **ISS-017: Unit conversion failures** - Now show warnings (orange) instead of errors (red) with SI fallback.

## [1.4.0] - 2026-01-12

### Fixed

- **ISS-016: Error markup in input not detected** - Added pre-processing to detect and clean error markup.
- **ISS-015: User documentation incomplete** - Updated docs/USAGE.md for v1.4 features.
- **ISS-014: Recursive unit conversion** - Verified working (fixed as side effect of ISS-009).

### Added

- `detect_error_markup()` function for programmatic inspection of documents.

## [1.3.0] - 2026-01-12

### Fixed

- **ISS-013: Inline unit hints lost after processing** - Unit hints now generate HTML comments in output.
- **ISS-009: Custom units with division fail** - Unit propagation for formula assignments.

### Added

- HTML comment injection for unit hint persistence.
- Check to prevent redefining existing Pint units.

## [1.2.0] - 2026-01-12

### Fixed

- **ISS-012: Process/clear cycle instability** - Fixed nested brace handling in `clear_text()`.

### Added

- Pre-processing step to clear already-processed content before parsing.
- Idempotent processing - stable results on repeated runs.

## [1.1.0] - 2026-01-12

### Added

- Pint-based unit conversion for all unit operations.
- Custom unit definitions via `===` operator.
- Value placeholders for tables: `<!-- value:VAR [unit] :precision -->`.
- IR JSON output for debugging.

### Changed

- Removed all hardcoded unit lists (~230 definitions) - Pint is now single source of truth.
- Removed unit fallback for undefined symbols.

## [1.0.0] - 2026-01-08

### Added

- Initial release with core calculation features.
- `:=` (define), `==` (evaluate), `=>` (symbolic) operators.
- Unit support via SymPy.
- CLI: `livemathtex process`, `livemathtex clear`, `livemathtex inspect`.

---

[1.6.0]: https://github.com/axabio/livemathtex/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/axabio/livemathtex/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/axabio/livemathtex/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/axabio/livemathtex/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/axabio/livemathtex/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/axabio/livemathtex/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/axabio/livemathtex/releases/tag/v1.0.0
