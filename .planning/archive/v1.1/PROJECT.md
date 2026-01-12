# LiveMathTeX v1.1 - Bug Fixes & API

## What This Is

LiveMathTeX is a CLI tool that processes Markdown documents containing LaTeX calculations, evaluating them with unit support via SymPy and Pint. This milestone focuses on fixing critical bugs and exposing a public Python API.

## Core Value

Calculations must evaluate correctly with proper error handling - a failed variable definition must not silently fall back to unit interpretation.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ CLI with `process` and `inspect` commands — existing
- ✓ LaTeX calculation evaluation (`:=`, `==`, `=>` operators) — existing
- ✓ Unit handling via Pint (dynamic, no hardcoded lists) — existing
- ✓ Custom unit definitions via `===` syntax — existing
- ✓ IR (Intermediate Representation) for debugging — existing
- ✓ Configuration via TOML and document directives — existing
- ✓ Snapshot testing with pytest — existing

### Active

<!-- Current scope. Building toward these. -->

- [x] ISS-003: Failed variable definition blocks unit fallback (Critical) - Fixed in Phase 1
- [x] ISS-004: Directive parser ignores code blocks (Medium) - Fixed in Phase 2
- [x] ISS-005: LaTeX-wrapped units parsed correctly (Medium) - Fixed in Phase 2
- [ ] ISS-010: Public Python API exposed via `__init__.py` - Planned for Phase 3
- [ ] ISS-011: `livemathtex clear` command to reset calculations - Planned for Phase 3

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Import system (cross-file symbols) — complex feature, defer to future milestone
- Watch mode (auto-rebuild) — nice-to-have, not critical for this milestone
- Large file streaming — current MVP handles typical documents fine
- GUI/IDE integration — CLI focus for now

## Context

LiveMathTeX is a personal tool for technical calculations in Markdown documents. The codebase is mature with 102 passing tests. Recent work resolved unit handling issues (ISS-001, ISS-002), consolidating all unit logic in Pint.

**Tech debt identified:**
- Large files: `evaluator.py` (91KB), `pint_backend.py` (58KB)
- Forked `latex2sympy2` dependency for DIFFERENTIAL bug fix

**Known issues from ISSUES.md:**
- ISS-003 was critical: failed `V := 37824` silently became `V = 1 volt` in subsequent formulas (fixed)
- ISS-004 affected documentation: example directives in code blocks got parsed (fixed)
- ISS-005 affected usability: `\text{m/s}^2` units didn't work (fixed)

## Constraints

- **Tech stack**: Python 3.10+, SymPy, Pint, Click — established, don't change
- **Dependencies**: Forked latex2sympy2 from GitHub — monitor upstream
- **Testing**: Maintain 102+ passing tests, use TDD for bug fixes
- **Compatibility**: Don't break existing document processing

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Focus on bugs before features | Critical bugs undermine trust in calculations | — Pending |
| TDD for ISS-003 | Complex error handling needs test coverage first | — Pending |

---
*Last updated: 2026-01-11 after initialization*
