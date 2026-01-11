# Codebase Concerns

**Analysis Date:** 2026-01-11

## Tech Debt

**Large Engine Files:**
- Issue: `evaluator.py` is 91,908 bytes, `pint_backend.py` is 58,337 bytes
- Files: `src/livemathtex/engine/evaluator.py`, `src/livemathtex/engine/pint_backend.py`
- Why: Organic growth during development, complex domain logic
- Impact: Harder to navigate and understand, longer to read
- Fix approach: Consider extracting specific concerns into sub-modules

**Forked latex2sympy2 Dependency:**
- Issue: Using a forked version from GitHub for DIFFERENTIAL bug fix
- Files: `pyproject.toml` (dependency definition)
- Why: Upstream hasn't merged the fix
- Impact: Dependency management complexity, risk if fork unmaintained
- Fix approach: Submit PR upstream, or vendor the fork if upstream inactive

## Known Bugs

**No known bugs identified in codebase scan.**

## Security Considerations

**Expression Evaluation:**
- Risk: LaTeX expressions are parsed and evaluated via SymPy
- Files: `src/livemathtex/engine/evaluator.py`
- Current mitigation: Whitelist approach for allowed functions
- Recommendations: Documented in `docs/ARCHITECTURE.md` (security section)

**No Hardcoded Secrets:**
- Status: Clean - No API keys, tokens, or secrets in codebase
- Verification: Grep for common patterns found nothing

## Performance Bottlenecks

**Pint Unit Registry:**
- Problem: Unit registry must be reset between independent operations
- File: `src/livemathtex/engine/pint_backend.py`
- Measurement: Not benchmarked, but reset_unit_registry() called in tests
- Cause: Custom unit definitions persist in singleton registry
- Improvement path: Consider per-processing-run registry or cleaner isolation

**Large File Processing:**
- Problem: Full file read into memory for processing
- File: `src/livemathtex/core.py`
- Measurement: Not benchmarked, typical documents are small
- Cause: Simple implementation for MVP
- Improvement path: Streaming processing if needed for large documents

## Fragile Areas

**Symbol Normalization:**
- File: `src/livemathtex/engine/symbols.py`, `src/livemathtex/engine/evaluator.py`
- Why fragile: Complex mapping between LaTeX names and internal IDs
- Common failures: Complex subscripts, special characters in variable names
- Safe modification: Snapshot tests in `tests/test_examples.py` catch regressions
- Test coverage: Good - snapshot tests cover many edge cases

**IR Schema Versioning:**
- Files: `src/livemathtex/ir/schema.py`
- Why fragile: v2.0 and v3.0 schemas both supported
- Common failures: Schema evolution, backward compatibility
- Safe modification: Test both v2.0 and v3.0 paths
- Test coverage: Snapshot tests validate output, inspect command tests JSON

## Scaling Limits

**Not applicable** - CLI tool processes single files, no scaling concerns.

## Dependencies at Risk

**latex2sympy2 (forked):**
- Risk: Fork may diverge from upstream, maintenance burden
- Impact: LaTeX parsing could break if upstream changes significantly
- Migration plan: Monitor upstream, contribute fix, or vendor dependency

**Pint:**
- Risk: None significant - actively maintained, stable API
- Impact: Unit handling is core functionality
- Migration plan: Not needed currently

## Missing Critical Features

**Import System:**
- Problem: Cannot import symbols from other Markdown files
- Current workaround: Manual copy of definitions
- Blocks: Reusable constant libraries, modular calculations
- Implementation complexity: Medium - design documented in ARCHITECTURE.md

**Watch Mode:**
- Problem: No auto-rebuild on file changes
- Current workaround: Manual re-run of `livemathtex process`
- Blocks: Live editing workflow
- Implementation complexity: Low - watchdog already a dependency

## Test Coverage Gaps

**Evaluator Coverage:**
- What's not tested: Some error paths in large evaluator.py
- Risk: Edge cases could cause unexpected failures
- Priority: Medium
- Difficulty to test: Complex setup for error conditions

**CLI Integration:**
- What's not tested: End-to-end CLI invocation
- Risk: Argument parsing, file I/O could regress
- Priority: Low - core logic tested via process_text()
- Difficulty to test: Need subprocess testing or click.testing

## Documentation Gaps

**No Significant Gaps:**
- Architecture well-documented in `docs/ARCHITECTURE.md`
- Usage documented in `docs/USAGE.md`
- Module docstrings present in source files

---

*Concerns audit: 2026-01-11*
*Update as issues are fixed or new ones discovered*
