# LiveMathTeX

## What This Is

LiveMathTeX is a CLI tool that processes Markdown documents containing LaTeX calculations, evaluating them with unit support via Pint.

**Latest:** v3.1 (shipped 2026-01-15) - Complete SymPy removal, Pure Pint architecture

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

**v3.1 Architecture (Pure Pint):** The codebase uses a custom LaTeX expression parser feeding directly into Pint evaluation. No SymPy or latex2sympy dependencies.
- Custom tokenizer for LaTeX expressions
- Custom parser producing AST nodes
- Direct Pint evaluation without SymPy intermediate
- Structural Markdown parsing (markdown-it-py + pylatexenc)
- Character-level spans for all operations

## Constraints

- **Tech stack**: Python 3.10+, Pint, Click — established (SymPy removed in v3.1)
- **Testing**: TDD approach
- **Compatibility**: Don't break v1.2 functionality

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| TDD for ISS-012 | Failing tests already exist, fix implementation to pass them | ✓ Resolved v1.2 |
| Pre-processing approach | Clear already-processed content before parsing | ✓ Resolved v1.2 |
| Remove SymPy entirely | latex2sympy corrupts global state causing ISS-035/036/037/038 | ✓ Resolved v3.1 |
| Custom LaTeX parser | Direct Pint evaluation, no SymPy dependency | ✓ Shipped v3.0/v3.1 |

---
*Last updated: 2026-01-15 — v3.1 shipped*
