# Codebase Concerns

**Analysis Date:** 2026-01-10

## Tech Debt

**Dual IR Schema (v2.0 and v3.0):**
- Issue: Two IR schemas maintained in parallel (v2.0 legacy, v3.0 current)
- Files: `src/livemathtex/ir/schema.py` (both schemas), `src/livemathtex/core.py` (both `process_file` and `process_text_v3`)
- Why: Backward compatibility during migration to Pint-based units
- Impact: Code duplication, maintenance burden, confusion about which to use
- Fix approach: Deprecate v2.0, migrate all code to v3.0, remove v2.0 after grace period

**Symbol ID Format Inconsistency:**
- Issue: IR v3.0 uses clean IDs (v1, f1) but current implementation may still use v_{0} format
- Files: `src/livemathtex/engine/symbols.py` (NameGenerator), `src/livemathtex/core.py:_populate_ir_symbols_v3()`
- Why: Migration in progress, not fully completed
- Impact: Inconsistent ID formats in IR JSON, potential parsing issues
- Fix approach: Complete migration to clean IDs, update all symbol references

**Unit Registry Global State:**
- Issue: Pint unit registry is global, requires manual reset between tests
- Files: `src/livemathtex/engine/pint_backend.py`, `src/livemathtex/engine/__init__.py` (reset_unit_registry)
- Why: Pint UnitRegistry is designed as singleton
- Impact: Test isolation issues, state leakage between tests
- Fix approach: Consider dependency injection or context manager pattern

**Forked Dependency (latex2sympy2):**
- Issue: Using forked version of latex2sympy2 from git URL
- Files: `pyproject.toml` (dependency specification)
- Why: Bug fix for DIFFERENTIAL operator
- Impact: Dependency on external git repo, harder to track updates
- Fix approach: Contribute fix upstream, switch back to PyPI version when merged

## Known Bugs

**None documented:**
- No known bugs in issue tracker or code comments
- Test suite passes for all examples
- IR v3.0 processing works correctly

## Security Considerations

**LaTeX Expression Evaluation:**
- Risk: User-provided LaTeX expressions evaluated via SymPy (potential code injection)
- Files: `src/livemathtex/engine/evaluator.py` (evaluate method)
- Current mitigation: SymPy sandboxing (no filesystem/network access), timeout per expression (5s default)
- Recommendations: Review SymPy security model, consider additional sandboxing if needed

**File System Access:**
- Risk: CLI reads/writes arbitrary files (user-controlled paths)
- Files: `src/livemathtex/cli.py` (process command), `src/livemathtex/core.py` (process_file)
- Current mitigation: User runs with their own permissions, no elevated access
- Recommendations: Validate file paths, prevent directory traversal (if needed)

**No Input Validation:**
- Risk: No validation of markdown file size or content before processing
- Files: `src/livemathtex/core.py` (reads entire file into memory)
- Current mitigation: Python memory limits, timeout per expression
- Recommendations: Add file size limits, streaming parser for large files (if needed)

## Performance Bottlenecks

**Full File Read:**
- Problem: Entire markdown file read into memory at once
- File: `src/livemathtex/core.py:process_file()` (line 63: `content = f.read()`)
- Measurement: Not measured (acceptable for typical document sizes)
- Cause: Simple implementation, no streaming parser
- Improvement path: Streaming parser for large files (if needed), current approach fine for typical use

**No Caching:**
- Problem: No caching of parsed AST or evaluation results
- Files: `src/livemathtex/core.py` (full parse/evaluate on each run)
- Measurement: Not measured (acceptable for typical document sizes)
- Cause: Stateless design, simplicity
- Improvement path: Add caching for watch mode (future feature)

**Symbol Table Lookups:**
- Problem: Linear search through symbol table (if implemented as list)
- Files: `src/livemathtex/engine/symbols.py` (SymbolTable implementation)
- Measurement: Not measured (acceptable for typical symbol counts)
- Cause: Dictionary-based (O(1) lookup), likely fine
- Improvement path: Profile if performance issues arise

## Fragile Areas

**LaTeX Parsing Compatibility:**
- File: `src/livemathtex/engine/evaluator.py` (latex2sympy2 integration)
- Why fragile: Complex LaTeX expressions may fail to parse, requires symbol normalization workaround
- Common failures: Parsing errors for complex subscripts, Greek letters, special operators
- Safe modification: Test with examples before changing parsing logic
- Test coverage: Example snapshot tests cover parsing scenarios

**Unit Conversion Logic:**
- File: `src/livemathtex/engine/pint_backend.py` (Pint integration)
- Why fragile: Unit recognition depends on Pint registry state, custom units must be registered correctly
- Common failures: Unit not recognized, conversion fails, custom unit conflicts
- Safe modification: Reset unit registry in tests, verify custom unit definitions
- Test coverage: `test_pint_backend.py` covers unit handling

**IR Schema Evolution:**
- File: `src/livemathtex/ir/schema.py` (IR dataclasses)
- Why fragile: Schema changes break backward compatibility, dual schema maintenance
- Common failures: IR JSON from old version incompatible with new code
- Safe modification: Version IR JSON, support multiple versions during transition
- Test coverage: IR structure tests verify schema

## Scaling Limits

**File Size:**
- Current capacity: Limited by Python memory (typically fine for markdown files)
- Limit: Very large files (>100MB) may cause memory issues
- Symptoms at limit: Memory errors, slow processing
- Scaling path: Streaming parser for large files (if needed)

**Number of Calculations:**
- Current capacity: Not measured (acceptable for typical documents)
- Limit: Timeout per expression (5s default), no overall document timeout
- Symptoms at limit: Slow processing, timeout errors
- Scaling path: Optimize expression evaluation, increase timeout if needed

**Symbol Count:**
- Current capacity: Dictionary-based symbol table (O(1) lookup)
- Limit: Python dictionary limits (millions of symbols)
- Symptoms at limit: Memory usage, slower lookups
- Scaling path: Current implementation should scale fine

## Dependencies at Risk

**latex2sympy2 (forked):**
- Risk: Dependency on external git repo, harder to track updates, potential maintenance burden
- Impact: Breaking changes in upstream could break livemathtex
- Migration plan: Contribute fix upstream, switch back to PyPI version when merged

**Pint:**
- Risk: Active project, but API changes possible
- Impact: Unit handling could break with Pint updates
- Migration plan: Pin version, test updates before upgrading

**SymPy:**
- Risk: Large, well-maintained project, but breaking changes possible
- Impact: Core calculation engine could break
- Migration plan: Pin version, test updates before upgrading

## Missing Critical Features

**Import System:**
- Problem: Planned feature not yet implemented (import symbols from other Markdown via IR JSON)
- Current workaround: Manual copy-paste of values
- Blocks: Can't build reusable calculation libraries
- Implementation complexity: Medium (IR JSON loading, symbol merging)

**Watch Mode:**
- Problem: Planned feature not yet implemented (auto-rebuild on file changes)
- Current workaround: Manual re-run after changes
- Blocks: Slower iterative development workflow
- Implementation complexity: Low (watchdog already in dependencies, needs integration)

**Incremental Recalculation:**
- Problem: Full recalculation on every run (no dependency tracking for incremental updates)
- Current workaround: Full pipeline run each time
- Blocks: Slower for large documents with few changes
- Implementation complexity: High (dependency graph, change detection)

## Test Coverage Gaps

**Error Handling Edge Cases:**
- What's not tested: All error scenarios (circular dependencies, timeout, memory limits)
- Risk: Edge cases could cause crashes or incorrect behavior
- Priority: Medium
- Difficulty to test: Need to simulate error conditions

**Large File Handling:**
- What's not tested: Very large markdown files (>10MB)
- Risk: Memory issues or performance problems
- Priority: Low (typical use case is small files)
- Difficulty to test: Need large test files

**Custom Unit Edge Cases:**
- What's not tested: All custom unit definition patterns, unit conflicts
- Risk: Custom units could fail silently or conflict
- Priority: Medium
- Difficulty to test: Need comprehensive unit definition tests

**IR v2.0 to v3.0 Migration:**
- What's not tested: Backward compatibility of IR v2.0 JSON files
- Risk: Old IR files may not load correctly
- Priority: Low (v2.0 is legacy)
- Difficulty to test: Need v2.0 IR JSON test files

---

*Concerns audit: 2026-01-10*
*Update as issues are fixed or new ones discovered*

