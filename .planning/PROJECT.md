# LiveMathTeX

## What This Is

LiveMathTeX is a CLI tool that processes Markdown documents containing LaTeX calculations, evaluating them with unit support via SymPy and Pint.

**Latest:** v1.3 (shipped 2026-01-12) - Unit hint preservation and custom unit evaluation

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

### Active

<!-- Current scope. Building toward these. -->

None currently.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Import system (cross-file symbols) — complex feature, defer
- Watch mode (auto-rebuild) — nice-to-have

## Context

**ISS-013** discovered post-v1.1: The inline unit hint syntax `$E == [kJ]$` is cleaner than HTML comments but breaks re-processing. The `[kJ]` is extracted during processing and replaced with `\text{kJ}` in the result. When re-processing, the hint is lost and results fall back to SI base units.

**ISS-009** partially resolved: Division-based unit definitions now register correctly with Pint (`is_known_unit('SEC') = True`). However, standalone evaluations `$ratio ==` don't find the custom unit - only combined `:= ==` syntax works.

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
*Last updated: 2026-01-12 — v1.3 shipped*
