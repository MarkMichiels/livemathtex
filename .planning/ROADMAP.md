# Roadmap: LiveMathTeX

## Overview

LiveMathTeX is a CLI tool for evaluating LaTeX calculations in Markdown with unit support. Development progresses through focused milestones addressing stability, unit handling, and features.

## Domain Expertise

None (regex patterns, Python, Pint library)

## Milestones

- ✅ **v1.1 Foundation** - Phases 1-4 (shipped 2026-01-12)
- ✅ **v1.2 Process/Clear Stability** - Phase 1 (shipped 2026-01-12)
- ✅ **v1.3 Unit Hint Preservation** - Phases 2-4 (shipped 2026-01-12)
- ✅ **v1.4 Cleanup & Docs** - Phases 5-7 (shipped 2026-01-12)
- ✅ **v1.5 Parser Architecture** - Phases 8-12 (shipped 2026-01-13)
- ✅ **v1.6 Pint Evaluation Engine** - Phases 13-15 (shipped 2026-01-13)
- ✅ **v1.7 Pint Evaluator Hotfixes** - Phases 16-18 (shipped 2026-01-13)
- ✅ **v1.8 Pint Unit Handling Fixes** - Phase 19 (verified 2026-01-13 - issues not bugs)
- ✅ **v1.9 µmol Unit Conversion Fix** - Phase 20 (shipped 2026-01-14)
- ✅ **v2.0 Function Evaluation** - Phase 21 (shipped 2026-01-14)
- ✅ **v2.1 Superscript Variable Names** - Phase 22 (shipped 2026-01-14)
- ✅ **v3.0 Pure Pint Architecture** - Phases 23-27 (complete 2026-01-14)
- 🚧 **v3.1 Table and Comma Subscript Fixes** - Phases 28-29 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (1.1, 1.2): Urgent insertions (marked with INSERTED)

<details>
<summary>✅ v1.2 Process/Clear Stability (Phase 1) - SHIPPED 2026-01-12</summary>

### Phase 1: Fix Clear/Process Cycle
**Goal**: Make process/clear cycle stable and idempotent
**Depends on**: Nothing (first phase)
**Research**: Unlikely (root cause documented in BUG_INVESTIGATION.md)
**Plans**: 2 plans

Plans:
- [x] 01-01: Fix clear_text() error markup patterns
- [x] 01-02: Add idempotency check and verify full cycle

</details>

<details>
<summary>✅ v1.3 Unit Hint Preservation (Phases 2-4) - SHIPPED 2026-01-12</summary>

**Milestone Goal:** Fix unit hint preservation (ISS-013) and custom unit evaluation lookup (ISS-009)

See: [v1.3 Archive](.planning/milestones/v1.3-ROADMAP.md)

**Summary:**
- Phase 2: Preserve Inline Unit Hints - HTML comment injection for unit hint persistence
- Phase 3: Fix Evaluation Unit Lookup - Unit propagation for formula assignments
- Phase 4: Re-processing Verification - Comprehensive cycle tests (190 total tests)

**Issues Resolved:** ISS-013, ISS-009

</details>

<details>
<summary>✅ v1.4 Cleanup & Docs (Phases 5-7) - SHIPPED 2026-01-12</summary>

**Milestone Goal:** Address deferred issues - recursive unit conversion, error markup cleanup, and user documentation

**Issues Resolved:** ISS-014, ISS-015, ISS-016

#### Phase 5: Fix Recursive Units ✅
**Goal**: Fix unit conversion for recursively defined units like MWh, mol/day (ISS-014)
**Depends on**: v1.3 complete
**Completed**: 2026-01-12
**Plans**: 1

Plans:
- [x] 05-01: Verify and test recursive unit conversion (ISS-014 already fixed)

#### Phase 6: Error Markup Cleanup ✅
**Goal**: Detect and clean error markup in input documents (ISS-016)
**Depends on**: Phase 5
**Completed**: 2026-01-12
**Plans**: 1

Plans:
- [x] 06-01: Error markup detection and auto-cleanup

#### Phase 7: User Documentation ✅
**Goal**: Update and complete user documentation (ISS-015)
**Depends on**: Phase 6
**Completed**: 2026-01-12
**Plans**: 1

Plans:
- [x] 07-01: Complete user documentation for v1.4 features

</details>

<details>
<summary>✅ v1.5 Parser Architecture (Phases 8-12) - SHIPPED 2026-01-13</summary>

**Milestone Goal:** Replace regex-driven processing with structural parsing for robustness and extensibility.

See: [v1.5 Archive](milestones/v1.5-ROADMAP.md)

**Summary:**
- Phase 8: Markdown Parser Integration - Hybrid parser (markdown-it-py + pylatexenc)
- Phase 9: Structural Math Parsing - ParsedCalculation with character-level spans
- Phase 10: Clear Refactor - Span-based clear_text implementation (ISS-021)
- Phase 11: Token Classification - Multi-letter identifier diagnostics (ISS-018, ISS-022)
- Phase 12: Unit Warnings - Orange warnings with SI fallback (ISS-017)

**Issues Resolved:** ISS-017, ISS-018, ISS-019, ISS-020, ISS-021, ISS-022

</details>

### ✅ v1.6 Pint Evaluation Engine (Shipped 2026-01-13)

**Milestone Goal:** Fix numerical calculation accuracy by replacing SymPy-based evaluation with Pint-based evaluation for numerical calculations.

**Issues to Resolve:** ISS-023, ISS-024

#### Phase 13: SI Value Fix ✅
**Goal**: Fix `_format_si_value()` LaTeX cleanup that produces malformed output (ISS-023)
**Depends on**: v1.5 complete
**Completed**: 2026-01-13
**Plans**: 1

Plans:
- [x] 13-01: Fix LaTeX cleanup regex in evaluator.py (lines 1314, 1342)

#### Phase 14: Pint Evaluator Core ✅
**Goal**: Replace SymPy numerical evaluation with Pint-based evaluation (ISS-024 core fix)
**Depends on**: Phase 13
**Completed**: 2026-01-13
**Research**: ✅ COMPLETE - see `.planning/phases/14-pint-evaluator/RESEARCH.md`
**Key findings**: Implemented hybrid architecture - latex2sympy for parsing, Pint for numeric evaluation.
**Plans**: 5

Plans:
- [x] 14-01: Create `evaluate_sympy_ast_with_pint()` in pint_backend.py
- [x] 14-02: Add `_compute_with_pint()` wrapper in evaluator.py
- [x] 14-03: Route numeric evaluations (`==` operator) through Pint
- [x] 14-04: Update tests and verify core calculation
- [x] 14-05: Comprehensive tests (15 tests in test_pint_evaluator.py)

#### Phase 15: Verification & Docs ✅
**Goal**: Comprehensive testing of rate×time calculations, update documentation for v1.6
**Depends on**: Phase 14
**Completed**: 2026-01-13
**Plans**: 5

Plans:
- [x] 15-01: Update docs/USAGE.md with rate×time documentation
- [x] 15-02: Create CHANGELOG.md for v1.6 release
- [x] 15-03: Verify edge cases (15 tests in test_pint_evaluator.py)
- [x] 15-04: Update README.md version to 1.6.0
- [x] 15-05: Tag v1.6.0 release

</details>

### ✅ v1.7 Pint Evaluator Hotfixes (Shipped 2026-01-13)

**Milestone Goal:** Fix critical bugs discovered during real-world usage of Pint evaluator with production documents.

**Issues to Resolve:** ISS-025, ISS-026, ISS-027

#### Phase 16: Fix SymPy Constants Handling (ISS-025) ✅
**Goal**: Fix `evaluate_sympy_ast_with_pint()` to handle SymPy mathematical constants (π, e) and fix unsafe isinstance() check
**Depends on**: v1.6 complete
**Status**: Complete
**Completed**: 2026-01-13
**Research**: Unlikely (bug fix with clear solution in ISSUES.md)
**Plans**: 1

Plans:
- [x] 16-01: Add handlers for SymPy constants and fix SympyQuantity isinstance check

#### Phase 17: Fix Compound Rate Units (ISS-026) ✅ (Already Fixed)
**Goal**: Fix calculations with compound rate units containing division (mg/L/day) that produce 86.4x wrong results
**Depends on**: Phase 16
**Status**: Already fixed by v1.6 Pint evaluator work
**Resolution**: Verified 2026-01-13 - compound rate unit calculations work correctly

Plans:
- [x] N/A - Already fixed in Phase 14 (ISS-024)

#### Phase 18: Fix Currency Unit Conversion (ISS-027) ✅ (Already Fixed)
**Goal**: Fix EUR to k€ conversion - ensure EUR/€ are recognized as equivalent and k€ definition works
**Depends on**: Phase 17
**Status**: Already fixed by v1.6 Pint evaluator work
**Resolution**: Verified 2026-01-13 - custom unit prefixes work correctly

Plans:
- [x] N/A - Already fixed in Phase 14 (ISS-024)

</details>

### ✅ v1.8 Pint Unit Handling Fixes (Verified 2026-01-13)

**Milestone Goal:** Verify rate×time calculation and currency unit aliasing reported in ISS-028, ISS-029.

**Issues to Resolve:** ISS-028, ISS-029

#### Phase 19: Verify Pint Unit Calculations (ISS-028, ISS-029) ✅
**Goal**: Verify rate×time calculations and currency unit aliasing work correctly
**Depends on**: v1.7 complete
**Status**: Complete - Issues were not bugs (user reporting error)
**Completed**: 2026-01-13
**Research**: N/A - verification only

**Verification Results:**
- ISS-029: `49,020 g/day × 365 d × 0.90` → Actual: `16,103.07 kg` ✅ (works correctly)
- ISS-028: `139 €/MWh × 1472 MWh` with `<!-- [k€] -->` → Actual: `204.608 kilo€` ✅ (works correctly)
- 365 tests pass, no code changes required

Plans:
- [x] 19-01: Verified - no code changes needed (issues were not bugs)

### ✅ v1.9 µmol Unit Conversion Fix (Complete)

**Milestone Goal:** Fix µmol unit storage in JSON output causing 1,000,000x calculation errors.

**Issues Resolved:** ISS-030, ISS-031
**Completed**: 2026-01-14

#### Phase 20: Fix µmol JSON Serialization (ISS-030, ISS-031) ✅
**Goal**: Fix unit conversion when storing values in JSON - µmol should be stored as mol with correct magnitude conversion
**Depends on**: v1.8 complete
**Status**: Complete
**Completed**: 2026-01-14
**Research**: Unlikely (bug with clear root cause in ISSUES.md)
**Plans**: 1

**Fix Applied:**
- Root cause: SymPy symbol format mismatch (v_0 vs v_{15}) in `_compute_with_pint`
- Updated regex to handle both formats: `r'^v_\{?(\d+)\}?$'`
- Also fixed ISS-031 (unit×dimensionless) as side effect

Plans:
- [x] 20-01: Fix regex mismatch in Pint evaluation

### ✅ v2.0 Function Evaluation (Complete)

**Milestone Goal:** Fix function evaluation so functions can be called with arguments.

**Issues Resolved:** ISS-032
**Completed**: 2026-01-14

#### Phase 21: Fix Function Evaluation (ISS-032) ✅
**Goal**: Fix function calls to properly substitute arguments and evaluate Lambda expressions
**Depends on**: v1.9 complete
**Status**: Complete
**Completed**: 2026-01-14
**Research**: N/A
**Plans**: 1

**Fix Applied:**
- Root cause: Three interrelated bugs in function lookup/substitution
  1. Function name not normalized before lookup
  2. latex_name included full signature instead of just function name
  3. No reverse lookup from internal ID to original symbol
- Fixed all three in `evaluator.py`
- All 365 tests pass + 3 xpassed

Plans:
- [x] 21-01: Fix function call evaluation in Pint evaluator

### ✅ v2.1 Superscript Variable Names (Complete)

**Milestone Goal:** Allow variable names with superscripts (R^2) without false unit conflicts.

**Issues Resolved:** ISS-033, ISS-034 (verified), ISS-035 (updated - same root cause as ISS-018)
**Completed**: 2026-01-14

#### Phase 22: Fix Superscript Unit Conflict (ISS-033) ✅
**Goal**: Allow variable names with superscripts like R^2 without false unit conflict
**Depends on**: v2.0 complete
**Status**: Complete
**Completed**: 2026-01-14
**Research**: N/A
**Plans**: 1

**Fix Applied:**
- Root cause: `check_variable_name_conflict()` converted `R^2` to `R**2` via `clean_latex_unit()`
- `R` is molar_gas_constant in Pint, so `R**2` was treated as a valid unit expression
- Fix: Treat `^` (superscript) the same as `_` (subscript) for disambiguation
- Variable names containing `^` are now allowed without unit conflict checking
- All 365 tests pass + 3 xpassed

Plans:
- [x] 22-01: Fix superscript unit conflict in pint_backend.py

### ✅ v3.0 Pure Pint Architecture (Complete 2026-01-14)

**Milestone Goal:** Remove latex2sympy and SymPy dependencies entirely. Build custom LaTeX expression parser that feeds directly into Pint evaluation. Eliminates implicit multiplication issues and simplifies the codebase.

**Research:** ✅ COMPLETE - see `.planning/phases/23-remove-latex2sympy/23-RESEARCH.md`

**⚠️ IMPORTANT: Development Strategy**

This is a major architectural refactor. To minimize risk:

1. **Develop on separate branch:** `feature/v3-pure-pint`
   - All v3.0 work happens on this branch
   - Master remains stable with current (working) latex2sympy implementation
   - Merge to master only when ALL tests pass and feature is complete

2. **Incremental validation:**
   - Each phase must pass all existing 365+ tests before proceeding
   - Run real-world documents (astaxanthin_production_analysis.md) as validation
   - Compare outputs between old and new implementation

3. **Rollback strategy:**
   - Keep latex2sympy/SymPy code intact until Phase 27
   - Phase 26 should support both paths (feature flag) for testing
   - Only remove old code in Phase 27 after thorough validation

4. **Documentation updates:**
   - Update ARCHITECTURE.md with new pipeline
   - Update docs/USAGE.md if user-facing behavior changes
   - Update CONTRIBUTING.md with new parser architecture
   - Add inline documentation in new modules

**Key architectural change:**
```
OLD: LaTeX → latex2sympy → SymPy AST → evaluate_sympy_ast_with_pint() → Result
NEW: LaTeX → Custom Tokenizer → Expression Tree → Pint Evaluation → Result
```

**Benefits:**
- No more implicit multiplication (`PPE` won't become `P*P*E`)
- No more special character conflicts (`E` in subscripts)
- No more unit splitting (`kg` won't become `k*g`)
- Simpler codebase (~100MB SymPy dependency removed)
- Full control over parsing behavior

#### Phase 23: Expression Tokenizer ✅
**Goal**: Build custom LaTeX tokenizer that correctly identifies variables, units, operators, and numbers
**Depends on**: v2.1 complete
**Status**: Complete
**Completed**: 2026-01-14
**Research**: ✅ Complete (see 23-RESEARCH.md)
**Plans**: 1

Key deliverables:
- `expression_tokenizer.py` module (169 lines)
- TokenType enum (NUMBER, VARIABLE, UNIT, OPERATOR, FRAC, LPAREN, RPAREN, LBRACE, RBRACE, EOF)
- Token dataclass with type, value, start, end
- Pattern-based tokenization with priority ordering (units before single letters)
- 47 tests for all supported LaTeX constructs

Plans:
- [x] 23-01: TDD implementation of expression tokenizer

#### Phase 24: Expression Parser ✅
**Goal**: Build recursive descent parser that converts tokens into an expression tree
**Depends on**: Phase 23
**Status**: Complete
**Completed**: 2026-01-14
**Research**: Not needed (standard parsing patterns)
**Plans**: 1

Key deliverables:
- `expression_parser.py` module (225 lines)
- ExprNode hierarchy (NumberNode, VariableNode, BinaryOpNode, UnaryOpNode, FracNode, UnitAttachNode)
- Operator precedence handling (PEMDAS)
- Right associativity for exponentiation
- Fraction parsing (`\frac{a}{b}`)
- 69 tests for expression tree construction

Plans:
- [x] 24-01: TDD implementation of expression parser

#### Phase 25: Direct Pint Evaluator ✅
**Goal**: Implement expression tree evaluation using Pint directly (no SymPy)
**Depends on**: Phase 24
**Status**: Complete
**Completed**: 2026-01-14
**Research**: Not needed (Pint patterns established)
**Plans**: 1

Key deliverables:
- `expression_evaluator.py` module (153 lines)
- `evaluate_expression_tree()` function
- Variable lookup with name normalization
- Unit handling during evaluation
- Error handling (EvaluationError for undefined variables)
- 47 tests for numeric evaluation with units

Plans:
- [x] 25-01: TDD implementation of expression tree evaluator

#### Phase 26: Evaluator Integration ✅
**Goal**: Integrate new parser into evaluator.py, replacing latex2sympy calls
**Depends on**: Phase 25
**Status**: Complete
**Completed**: 2026-01-14
**Research**: Unlikely (internal refactoring)
**Plans**: 1

Key deliverables:
- Update `_compute()` to use new parser
- Update `_substitute_symbols()` for new AST format
- Remove `_rewrite_with_internal_ids()` (no longer needed)
- Remove token_classifier.py (implicit multiplication detection no longer needed)
- Maintain backward compatibility for all existing tests
- All 365+ tests still pass

Plans:
- [x] 26-01: Evaluator integration (try-first-fallback pattern)

#### Phase 27: Remove Dependencies ✅
**Goal**: Remove latex2sympy and sympy from project dependencies
**Depends on**: Phase 26
**Status**: Complete
**Completed**: 2026-01-14
**Research**: Unlikely (cleanup)
**Plans**: 1

Key deliverables:
- Remove `from latex2sympy2 import latex2sympy` imports
- Remove SymPy imports (except where truly needed for Lambda storage - evaluate alternatives)
- Update pyproject.toml / requirements.txt
- Update documentation
- Verify package size reduction
- Tag v3.0.0 release

Plans:
- [x] 27-01: Custom parser primary path (complete 2026-01-14)

### 🚧 v3.1 Complete SymPy Removal (In Progress)

**Milestone Goal:** Complete removal of SymPy and latex2sympy from the codebase. All bugs (ISS-035, ISS-036, ISS-037, ISS-038) are caused by latex2sympy's global state corruption - fix by removing it entirely.

**Issues to Resolve:** ISS-035, ISS-036, ISS-037, ISS-038

#### Phase 28: Complete SymPy/latex2sympy Removal
**Goal**: Remove ALL SymPy and latex2sympy code, no fallbacks, clean Pure Pint architecture
**Depends on**: v3.0 complete
**Status**: Planning complete, ready to execute
**Research**: Not needed (removal, not implementation)
**Plans**: 6 plans

**What gets removed:**
- evaluator.py: 106 sympy references → 0
- pint_backend.py: 148 sympy references → 0
- token_classifier.py: DELETE entire file
- core.py: 4 sympy references → 0
- Internal IDs: v_{0} format → v0 format (no LaTeX)
- Dependencies: sympy, latex2sympy2 uninstalled

**Issues Addressed:**
- ISS-037: Variables in table cells fail (caused by latex2sympy corruption)
- ISS-035: Multi-letter variables parsed as multiplication (caused by latex2sympy)
- ISS-038: Comma subscripts fail in expressions (caused by latex2sympy)
- ISS-036: Comma subscripts fail with Symbol error (caused by latex2sympy)

Plans:
- [x] 28-01: Remove latex2sympy fallback from evaluator.py
- [ ] 28-02: Remove SymPy from pint_backend.py
- [ ] 28-03: Remove SymPy from remaining files, delete token_classifier.py
- [ ] 28-04: Simplify internal IDs (v_{0} → v0)
- [ ] 28-05: Uninstall packages from dependencies
- [ ] 28-06: Full test suite verification and bug fixes
