# LiveMathTeX v1.3 - Unit Hint Preservation

## What This Is

LiveMathTeX is a CLI tool that processes Markdown documents containing LaTeX calculations, evaluating them with unit support via SymPy and Pint. This milestone fixes unit hint preservation (ISS-013) and custom unit evaluation lookup (ISS-009).

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

### Active

<!-- Current scope. Building toward these. -->

- [ ] ISS-013: Inline unit hints survive processing/re-processing
  - [ ] `$E == [kJ]$` preserved in output (not lost when result inserted)
  - [ ] Re-processing uses preserved hint (not SI base units)
  - [ ] clear_text() restores inline hints from processed output

- [ ] ISS-009: Custom unit evaluation lookup works for all syntaxes
  - [ ] Division-based units (`SEC === MWh/kg`) work in standalone `$var ==`
  - [ ] Combined `:= ==` syntax (already works)
  - [ ] Separate definition then evaluation (currently fails)

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
*Last updated: 2026-01-12 after milestone v1.3 initialization*
