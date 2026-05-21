# Codebase Concerns

**Analysis Date:** 2026-05-21

## Tech Debt

**Legacy Regex-Based Clear Implementation:**
- Issue: `_clear_text_regex()` in `src/livemathtex/core.py` (lines 34-98) is marked DEPRECATED but still exists as fallback
- Files: `src/livemathtex/core.py` (contains deprecated regex patterns)
- Impact: Maintainability burden; potential for regression if used
- Fix approach: Remove entirely or consolidate with the structural parsing-based implementation. Verify that `clear_text()` (lines 100+) fully replaces this implementation and covers all edge cases

**Unsafe eval() Call Without Sandbox:**
- Issue: `evaluate_formula_with_units()` in `src/livemathtex/engine/pint_backend.py:1343` uses `eval()` with restricted builtins but on user-provided expressions
- Files: `src/livemathtex/engine/pint_backend.py` (lines 1296-1360)
- Impact: If expression contains malicious code or unexpected constructs, could leak information or fail unexpectedly
- Fix approach: Replace with tree-walking evaluator or use AST validation before eval(). This is particularly important if documents are processed from untrusted sources. Consider: Is this function actually used in production, or is `evaluate_expression_tree()` the primary path?

**Bare except Clauses:**
- Issue: Multiple bare `except:` blocks that catch all exceptions without logging details
- Files: `src/livemathtex/engine/evaluator.py` (line 153), `src/livemathtex/engine/pint_backend.py` (lines 213, 241, 286, 389)
- Impact: Silent failures hide bugs; makes debugging difficult
- Fix approach: Replace with specific exception types and proper logging. At minimum, log the exception details before re-raising or returning a default value

**Missing Error Recovery in Symbol Normalization:**
- Issue: `_rewrite_with_internal_ids()` in `src/livemathtex/engine/evaluator.py:520-530` uses regex replacement on formulas; if a variable name matches partially within another symbol, replacement could corrupt the expression
- Files: `src/livemathtex/engine/evaluator.py` (lines 520-530)
- Impact: Formulas with nested subscripts or commas could be silently corrupted. Fixed for digit check in ISS-048 but may have other boundary cases
- Fix approach: Use AST-based rewriting instead of regex. Consider: Are there test cases for all subscript formats (underscores, commas, combinations)?

---

## Known Bugs

**Variable Subscripts with Commas in Complex Expressions (ISS-036):**
- Symptoms: Variables like `PPE_{eff,9010}` fail in complex expressions with error "argument of type 'Symbol' is not iterable"
- Files: `src/livemathtex/engine/expression_evaluator.py`, `src/livemathtex/engine/symbols.py`
- Trigger: Use subscript with comma in multi-term expression: `$PPE_{eff,9010} := (0.90 \cdot PPE_{red,raw} + 0.10 \cdot PPE_{blue,raw}) \cdot f_{geom} ==$`
- Workaround: Use underscores instead of commas: `PPE_{eff_9010}`
- Root cause: Likely in symbol name normalization or tokenizer handling of comma in subscripts

**Variables in Table Cells Fail (ISS-037):**
- Symptoms: Variables that work correctly in inline math fail inside table cells with error "argument of type 'Symbol' is not iterable"
- Files: `src/livemathtex/parser/markdown_parser.py`, `src/livemathtex/parser/calculation_parser.py`
- Trigger: Use variable evaluation in markdown table cell: `| Year | Value | \n |------|-------| \n | 2027 | $U_{27} ==$ |`
- Workaround: Calculate values outside table, then use plain numbers
- Root cause: Table cell parsing may not properly normalize variable names or may lose context during markdown-it parsing

**Dimensionless Unit Conversion Bug (ISS-043):**
- Symptoms: Dimensionless results incorrectly displayed with `kg/mg` units, producing values 1,000,000x too small
- Files: `src/livemathtex/engine/evaluator.py` (unit conversion logic), `src/livemathtex/engine/pint_backend.py` (format_unit_latex)
- Trigger: `$U_{26} := \frac{T_{26}}{C_{26}} \cdot 90 ==` → Displays as `5.4084e-05 kg/mg` instead of `54.084` (dimensionless)
- Root cause: LiveMathTeX internally calculates correct value but then attempts to convert dimensionless to kg/mg (dividing by 1,000,000)
- Impact: High - cascading errors in dependent calculations; internal value is correct but displayed value is wrong

---

## Security Considerations

**No Input Validation on LaTeX Expressions:**
- Risk: LaTeX math expressions are tokenized and parsed without whitelist validation; malformed LaTeX could cause unhandled exceptions or stack overflow
- Files: `src/livemathtex/parser/expression_tokenizer.py`, `src/livemathtex/parser/expression_parser.py`
- Current mitigation: Tokenizer uses regex patterns to limit input; parser has limited recursion (no runaway parsing observed in tests)
- Recommendations: 
  1. Add maximum nesting depth check in expression_parser.py to prevent stack overflow on deeply nested fractions/radicals
  2. Add expression size limit (max 10,000 characters) to prevent DOS
  3. Document input constraints (max nesting, max expression length)

**Custom Unit Definitions Not Validated:**
- Risk: User-provided unit definitions like `$custom := 5\ \text{kg}$` are accepted without checking for conflicts with Pint reserved names or problematic patterns
- Files: `src/livemathtex/engine/evaluator.py` (_handle_unit_definition)
- Current mitigation: Pint's own validation for unit syntax
- Recommendations: Add pre-flight validation to reject problematic patterns (e.g., units that are Python keywords, units that shadow system units)

**No Rate Limiting on Document Processing:**
- Risk: Very large documents (e.g., 100,000+ calculations) could consume unbounded memory or CPU
- Files: `src/livemathtex/core.py` (process_text, process_file)
- Current mitigation: None observed
- Recommendations: Add configurable limits for max calculations per document, max document size

---

## Performance Bottlenecks

**O(n²) Symbol Lookup in Large Documents:**
- Problem: SymbolTable.set() is called for every calculation; if documents have 10,000+ variables, lookup becomes slow
- Files: `src/livemathtex/engine/symbols.py` (SymbolTable class)
- Cause: Dictionary-based lookup with linear search through internal IDs for name normalization
- Improvement path: Profile with large documents (1000+ variables); consider caching normalization results

**Regex-Based Reference Detection:**
- Problem: `extract_references()` in `src/livemathtex/parser/reference_parser.py` uses non-greedy regex on entire document; with 10,000+ references, becomes slow
- Files: `src/livemathtex/parser/reference_parser.py` (extract_references)
- Cause: Regex iteration over entire content without chunking
- Improvement path: Consider line-by-line parsing with position tracking to avoid full-content regex passes

**Pint Unit Registry Initialization:**
- Problem: `get_unit_registry()` in `src/livemathtex/engine/pint_backend.py:40-54` initializes entire Pint registry on first call; Pint loads ~1000+ units and dimensions
- Files: `src/livemathtex/engine/pint_backend.py` (get_unit_registry)
- Cause: Global initialization pattern; Pint itself is slow to initialize
- Improvement path: Acceptable for CLI use but may be slow for serverless/cloud deployments. Consider lazy unit definition or pre-compiled registry

---

## Fragile Areas

**Expression Parser Operator Precedence:**
- Files: `src/livemathtex/parser/expression_parser.py` (lines 200+)
- Why fragile: Manual precedence implementation using recursive descent; changes to operator precedence require careful modification of multiple parsing functions
- Safe modification: Add comprehensive tests for each operator combination (a+b*c, a^b^c, etc.) before changing precedence
- Test coverage: `tests/test_expression_parser.py` has 69 tests covering basic cases, but may lack edge cases like `a - b ^ c` or `a / b / c`

**Unit Conversion Chain:**
- Files: `src/livemathtex/engine/evaluator.py` (lines 700-790), `src/livemathtex/engine/pint_backend.py` (lines 400-500)
- Why fragile: Multiple unit conversion pathways (original unit → base unit → target unit). If any step modifies the unit representation, downstream conversions fail
- Safe modification: Ensure unit_str is always preserved alongside Pint Quantity. Add assertion checks that unit_str matches Pint units at each step
- Test coverage: `tests/test_unit_conversion.py` exists but may not cover complex recursive units (MWh, mol/day, etc.)

**Symbol Name Normalization:**
- Files: `src/livemathtex/engine/evaluator.py` (lines 175-185), `src/livemathtex/engine/symbols.py`
- Why fragile: Converts `P_{LED,out}` → `v0` using regex and name generation; if symbol table is corrupted or internal IDs collide, formulas may evaluate with wrong values
- Safe modification: Add symbol table validation before/after each evaluation step; verify that all internal_ids are unique
- Test coverage: `tests/test_definition_types.py` covers some cases but may not test rapid symbol creation/deletion cycles

**LaTeX Parsing in Unit Expressions:**
- Files: `src/livemathtex/parser/expression_tokenizer.py` (lines 65-90), `src/livemathtex/engine/evaluator.py` (lines 1408+)
- Why fragile: `\text{}` wrapping is detected by simple regex; if unit contains braces or special chars (e.g., `\text{m{³}}`), tokenizer may fail
- Safe modification: Use pylatexenc for robust LaTeX parsing instead of regex
- Test coverage: Check if tests cover units with exponents, special chars, or nested commands

---

## Scaling Limits

**Array Operations Size:**
- Current capacity: Arrays are stored as Python lists; no observed limit
- Limit: NumPy or built-in Python memory limits (~1GB for typical systems)
- Scaling path: For production use with arrays >10,000 elements, consider using NumPy arrays; current implementation uses Pint Quantities which are slower for vectorized ops

**Cross-Reference Lookup:**
- Current capacity: Regex-based search in entire document; tested with ~100 references
- Limit: O(n) per reference lookup; with 10,000 references, becomes slow (seconds to minutes)
- Scaling path: Build index of variable positions during parsing; use direct lookup instead of regex search

**Custom Unit Registry Size:**
- Current capacity: Pint's default registry + LiveMathTeX custom units; tested with ~50 custom units
- Limit: Pint can handle hundreds of units but becomes slow if registry size exceeds 1000+ custom definitions
- Scaling path: For production with many custom units, consider splitting into multiple registries or using Pint's built-in unit categories

---

## Dependencies at Risk

**Pint Unit Registry Initialization:**
- Risk: Pint 0.x series (current requirement) is deprecated; may not receive security updates
- Impact: Long-term maintainability; potential compatibility issues with NumPy/SymPy on new Python versions
- Migration plan: Monitor Pint 1.0 release; test compatibility before upgrading. Consider: Does LiveMathTeX depend on Pint 0.x specific behavior?

**SymPy Constants Handling:**
- Risk: `sympy.core.numbers.NumberSymbol` base class may change in SymPy 1.13+
- Impact: Calculations with π, e, or other SymPy constants fail with isinstance errors (ISS-025 notes this was previously a bug)
- Migration plan: Add version check for SymPy; add fallback handler for unknown constant types

**markdown-it-py Parser:**
- Risk: markdown-it-py is relatively new and may have edge cases with complex markdown
- Impact: Document parsing may fail on unusual markdown structures; currently mitigated by fallback to regex-based parsing
- Migration plan: Maintain regex fallback; add comprehensive markdown test suite covering real-world edge cases

---

## Missing Critical Features

**No Input Size Limits:**
- Problem: No maximum document size, maximum calculations per document, or maximum expression length enforced
- Blocks: Cannot safely run LiveMathTeX in serverless/cloud environments where there are strict CPU/memory quotas
- Recommendation: Add configurable limits in LivemathConfig for max document size, max calculation count, max expression length

**No Operator Definitions for Custom Functions:**
- Problem: Only prefix functions supported (like `sin()`, `ln()`); cannot define custom infix operators (like `a |+| b`)
- Blocks: Advanced mathematical notation for domain-specific problems
- Recommendation: Consider adding operator definition syntax for specialized domains

---

## Test Coverage Gaps

**Unit Conversion Edge Cases (ISS-030, ISS-031, ISS-043):**
- What's not tested: Dimensionless × dimensionless results; unit propagation through multiplication chains; conversions between rarely-used unit combinations
- Files: `src/livemathtex/engine/pint_backend.py` (unit conversion logic)
- Risk: Cascading failures in dependent calculations
- Priority: High - these are active issues in LESSONS_LEARNED.md

**Variable Names with Special Characters:**
- What's not tested: Variables with non-ASCII subscripts, multiple subscripts with various separators (comma, underscore, space), mixed case
- Files: `src/livemathtex/engine/symbols.py`, `src/livemathtex/parser/expression_tokenizer.py`
- Risk: Name collision or silent corruption
- Priority: High - ISS-036, ISS-037 indicate this is a real problem

**Error Recovery in Parser:**
- What's not tested: How parser behaves with malformed LaTeX (unclosed braces, invalid commands, syntax errors)
- Files: `src/livemathtex/parser/expression_parser.py`, `src/livemathtex/parser/expression_tokenizer.py`
- Risk: Unhandled exceptions crash processing or produce cryptic error messages
- Priority: Medium - affects user experience

**Large Document Processing:**
- What's not tested: Documents with 1000+ calculations, 10,000+ variables, or 100+ MB size
- Files: `src/livemathtex/core.py` (process_text, process_file)
- Risk: Memory exhaustion, timeout, or quadratic slowdown
- Priority: Low for current use cases but important for production deployment

**Table Cell Variable Evaluation (ISS-037):**
- What's not tested: Variables in markdown table cells specifically
- Files: `src/livemathtex/parser/calculation_parser.py`, `src/livemathtex/parser/markdown_parser.py`
- Risk: Silent failures or incorrect results in tabulated data
- Priority: High - blocks common use case

---

## Deprecated Paths

**Old LaTeX Parser Fallback:**
- Location: References in `src/livemathtex/engine/evaluator.py` (line 1033, 1513) mention "old latex parser"
- Status: Removed in v3.0 Pure Pint Architecture; no longer used
- Cleanup needed: Remove references and documentation about the fallback path

**Phase-based Evaluation (Comments):**
- Location: `src/livemathtex/engine/evaluator.py` (lines 1515-1516) document previous architecture phases
- Status: Informational only; no code remains
- Cleanup: Consider moving to architecture docs instead of inline comments

---

*Concerns audit: 2026-05-21*
