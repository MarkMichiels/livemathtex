# LiveMathTeX

## What This Is

LiveMathTeX is a CLI tool that processes Markdown documents containing LaTeX calculations, evaluating them with unit support via SymPy and Pint.

**Latest:** v1.5 (shipped 2026-01-13) - Parser architecture overhaul with span-based operations

## Core Value

Processing must be idempotent - running process on an already-processed file should produce stable results, and clear→process should restore the original output.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ CLI with `process`, `inspect`, `clear`, `copy` commands — v1.1
- ✓ LaTeX calculation evaluation (`:=`, `==`, `=>` operators) — existing
- ✓ Unit handling via Pint (dynamic, no hardcoded lists) — existing
- ✓ Public Python API (`process_text`, `clear_text`) — v1.1
- ✓ Error handling with color-coded markup — existing
- ✓ Process/clear cycle stability (ISS-012) — v1.2
- ✓ Inline unit hints survive processing/re-processing (ISS-013) — v1.3
- ✓ Custom unit evaluation lookup works for all syntaxes (ISS-009) — v1.3
- ✓ Recursive unit conversion (ISS-014) — v1.4
- ✓ Error markup cleanup in input documents (ISS-016) — v1.4
- ✓ Structural parsing replaces regex (ISS-019, ISS-020) — v1.5
- ✓ Span-based clear_text fixes document corruption (ISS-021) — v1.5
- ✓ Multi-letter identifier diagnostics (ISS-018, ISS-022) — v1.5
- ✓ Unit warnings with SI fallback (ISS-017) — v1.5

### Active

<!-- Current scope. Building toward these. -->

None currently. All known issues resolved.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Import system (cross-file symbols) — complex feature, defer
- Watch mode (auto-rebuild) — nice-to-have

## Context

**v1.5 Architecture:** The codebase now uses structural parsing (markdown-it-py + pylatexenc) instead of regex patterns. This provides:
- Character-level spans for all operations
- Proper handling of multiline constructs
- Better error diagnostics for multi-letter identifiers
- Warnings (orange) vs errors (red) distinction

## Constraints

- **Tech stack**: Python 3.10+, SymPy, Pint, Click — established
- **Testing**: TDD approach
- **Compatibility**: Don't break v1.2 functionality

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| TDD for ISS-012 | Failing tests already exist, fix implementation to pass them | ✓ Resolved v1.2 |
| Pre-processing approach | Clear already-processed content before parsing | ✓ Resolved v1.2 |

---
*Last updated: 2026-01-13 — v1.5 shipped*
