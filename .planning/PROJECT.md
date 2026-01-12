# LiveMathTeX v1.2 - Process/Clear Stability

## What This Is

LiveMathTeX is a CLI tool that processes Markdown documents containing LaTeX calculations, evaluating them with unit support via SymPy and Pint. This milestone fixes the process/clear cycle instability bug (ISS-012).

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

### Active

<!-- Current scope. Building toward these. -->

- [ ] ISS-012: Process/clear cycle produces stable results
  - [ ] clear_text() removes ALL error markup formats
  - [ ] Processing already-processed files is idempotent
  - [ ] clear→process cycle produces identical results

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- ISS-009: Compound unit definitions with division — defer to v1.3
- Import system (cross-file symbols) — complex feature, defer
- Watch mode (auto-rebuild) — nice-to-have

## Context

ISS-012 was discovered post-v1.1 during testing. The bug manifests in 3 scenarios:
1. **Scenario 4:** F9 on output.md second time → additional errors appear
2. **Scenario 5:** Shift+F9 on output.md → artifacts remain
3. **Scenario 6:** F9 after clear → different results than original

Root causes identified in `.planning/archive/v1.1/BUG_INVESTIGATION.md`:
- `clear_text()` doesn't remove all error markup (e.g., `\\ }$`, multiline errors)
- Parser misinterprets error artifacts as math content
- No idempotency check for in-place processing

Failing regression tests already exist: `tests/test_process_clear_cycle.py`

## Constraints

- **Tech stack**: Python 3.10+, SymPy, Pint, Click — established
- **Testing**: TDD approach - fix tests first, then implementation
- **Compatibility**: Don't break v1.1 functionality

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| TDD for ISS-012 | Failing tests already exist, fix implementation to pass them | — Pending |
| Focus on clear_text() first | Root cause is incomplete error cleanup | — Pending |

---
*Last updated: 2026-01-12 after milestone initialization*
