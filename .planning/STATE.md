# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-12)

**Core value:** Processing must be idempotent - stable results on repeated runs
**Current focus:** v1.7 hotfixes - fixing Pint evaluator bugs (ISS-025, ISS-026, ISS-027)

## Current Position

Phase: 16 of 18 (Fix SymPy Constants Handling)
Plan: Not started
Status: 🔧 IN PROGRESS (v1.7 Hotfixes)
Last activity: 2026-01-13 — Created v1.7 milestone for ISS-025, ISS-026, ISS-027

**Milestone v1.7 Scope:**
- Phase 16 (ISS-025): ⏳ NOT STARTED - SymPy constants and isinstance fix
- Phase 17 (ISS-026): ⏳ NOT STARTED - Compound rate unit calculations
- Phase 18 (ISS-027): ⏳ NOT STARTED - Currency unit conversion

Progress: ██████████░░░░░░░░ 83% (15/18 phases, v1.7: 0/3)

## Performance Metrics

**Velocity:**
- Total plans completed: 14 (2 from v1.2 + 3 from v1.3 + 3 from v1.4 + 5 from v1.5 + 1 from v1.6)
- Average duration: ~11 min
- Total execution time: ~158 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Fix Clear/Process Cycle | 2/2 | ~16 min | ~8 min |
| 2. Preserve Inline Unit Hints | 1/1 | ~10 min | ~10 min |
| 3. Fix Evaluation Unit Lookup | 1/1 | ~12 min | ~12 min |
| 4. Re-processing Verification | 1/1 | ~12 min | ~12 min |
| 5. Fix Recursive Units | 1/1 | ~8 min | ~8 min |
| 6. Error Markup Cleanup | 1/1 | ~10 min | ~10 min |
| 7. User Documentation | 1/1 | ~12 min | ~12 min |
| 8. Markdown Parser Integration | 1/1 | ~15 min | ~15 min |
| 9. Structural Math Parsing | 1/1 | ~12 min | ~12 min |
| 10. Clear Refactor | 1/1 | ~15 min | ~15 min |
| 11. Token Classification | 1/1 | ~13 min | ~13 min |
| 12. Unit Warnings | 1/1 | ~13 min | ~13 min |
| 13. SI Value Fix | 1/1 | ~10 min | ~10 min |

## Completed Milestones

| Version | Tag | Completed | Archive |
|---------|-----|-----------|---------|
| v1.1 | v1.1.0 | 2026-01-12 | .planning/archive/v1.1/ |
| v1.2 | — | 2026-01-12 | — |
| v1.3 | v1.3.0 | 2026-01-12 | .planning/milestones/v1.3-ROADMAP.md |
| v1.4 | v1.4.0 | 2026-01-12 | — |
| v1.5 | v1.5.0 | 2026-01-13 | .planning/milestones/v1.5-ROADMAP.md |
| v1.6 | v1.6.0 | 2026-01-13 | — |

## Accumulated Context

### Decisions

- **01-01:** Pre-processing approach - clear already-processed content before parsing
- **01-01:** Fixed test assertions that incorrectly checked for "Error:" in section headings
- **01-01:** Use nested brace regex `\{(?:[^{}]|\{[^{}]*\})*\}` for proper matching
- **02-01:** Tuple format for results dict - pass inline unit hint as `(result, inline_unit_hint)` to avoid modifying frozen dataclass
- **03-01:** Unit propagation via `_compute(rhs, propagate_units=True)` for formula assignments
- **03-01:** Added check in `_handle_unit_definition` to prevent redefining existing Pint units
- **11-01:** Collect all undefined symbols before raising error to enable implicit multiplication detection
- **12-01:** Dimension mismatches are warnings (orange) not errors (red), with SI fallback

### Deferred Issues

v1.6 issues to address:
- ISS-023 → Phase 13 (SI Value Fix) ✅ FIXED
- ISS-024 → Phase 14 (Pint Evaluator Core) - SymPy→Pint numerical evaluation

All v1.5 issues resolved:
- ISS-017 → Phase 12 (Unit Warnings) ✓
- ISS-018 → Phase 11 (Token Classification) ✓
- ISS-019 → Phase 8 (Parser Integration) ✓
- ISS-020 → Phases 8-9 (Structural Parsing) ✓
- ISS-021 → Phase 10 (Clear Refactor) ✓
- ISS-022 → Phase 11 (Token Classification) ✓

### Blockers/Concerns

None.

### Roadmap Evolution

- Milestone v1.3 complete: All 3 phases (2-4) finished
- ISS-013 fixed: Inline unit hints survive processing
- ISS-009 fixed: Custom division units work in standalone evaluations
- Milestone v1.4 complete: All deferred issues addressed
- Milestone v1.5 complete: Parser Architecture, 5 phases (8-12)
- Milestone v1.6 created: Pint Evaluation Engine, 3 phases (13-15)

## Session Continuity

Last session: 2026-01-13
Stopped at: Milestone v1.6 initialization
Resume file: None
Next: Plan Phase 13 (SI Value Fix)

### Implementation Notes (Phase 12)

- **Warning exception:** `UnitConversionWarning` in `utils/errors.py`
- **Detection:** Dimension mismatch errors detected by keywords in exception message
- **Evaluator:** Added `_warning_count`, `get_warning_count()`, `_format_warning()`
- **SI fallback:** `_extract_unit_string()` and `_format_si_value()` helpers
- **Footer:** Shows "no errors, 1 warning" format
- **Clear patterns:** Added `\color{orange}` removal to `clear_text()`
- **ISS-017 fixed:** Unit conversion failures show warnings with SI value
- **Tests:** 345 tests pass (plus 2 xfailed for pre-existing bugs)

### Implementation Notes (Phase 11)

- **Module:** `src/livemathtex/engine/token_classifier.py`
- **Key classes:** `TokenClassifier`, `TokenType` enum, `ImplicitMultInfo` dataclass
- **Detection:** `detect_implicit_multiplication()` identifies when latex2sympy splits multi-letter identifiers
- **Unit conflicts:** Single-letter unit tracking (A=ampere, V=volt, etc.)
- **ISS-018 fixed:** Error messages now mention intended multi-letter symbol
- **ISS-022 fixed:** Diagnostics explain implicit multiplication pattern
- **Tests:** 46 tests in `tests/test_token_classifier.py`, 348 total tests pass

### Implementation Notes (Phase 10)

- **Refactored:** `clear_text()` now uses span-based operations
- **Old function:** Preserved as `_clear_text_regex()` for reference
- **Two-pass approach:** Remove error markup first, then re-parse for accurate spans
- **Unit preservation:** Properly extracts units from `\text{}` in results
- **ISS-021 fixed:** Document corruption around multiline errors eliminated
- **Tests:** 27 tests in `tests/test_clear_v2.py`, 302 total tests pass

### Implementation Notes (Phase 9)

- **Module:** `src/livemathtex/parser/calculation_parser.py`
- **Key dataclasses:** `Span` (start/end offsets), `ParsedCalculation` (operation, spans)
- **Operations:** `===`, `:=`, `==`, `=>`, `:=_==`, `value`, `ERROR`
- **All spans are document-relative** (not math-block-relative)
- **Tests:** 36 tests in `tests/test_calculation_parser.py`

### Implementation Notes (Phase 8)

- **Hybrid stack:** markdown-it-py + dollarmath (doc structure) + pylatexenc (LaTeX positions)
- **Key insight:** Inline math tokens are children of `inline` tokens, not top-level
- **Module:** `src/livemathtex/parser/markdown_parser.py`
- **Tests:** 34 tests in `tests/test_markdown_parser.py`
