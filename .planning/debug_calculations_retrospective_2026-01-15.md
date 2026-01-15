# Debug Calculations Retrospective - 2026-01-15

## Document Processed

**Document:** `mark-private/private/axabio_confidential/business/abp_2026_2030/docs/astaxanthin_production_analysis.md`
- **Total calculations:** 181 evaluations
- **Total errors:** 98 errors
- **Document size:** 961 lines

## Issues Found

### Bugs Identified (3 total)

1. **ISS-037: Variables in table cells fail**
   - **Errors:** 4
   - **Test file:** `tests/test_iss_037_table_cell_symbol_not_iterable.md` (1 error confirmed)
   - **Status:** ✅ Reproducible

2. **ISS-038: Variables with commas fail in expressions**
   - **Errors:** 25
   - **Test file:** `tests/test_iss_038_comma_subscript_expression_parse_error.md` (2 errors confirmed)
   - **Status:** ✅ Reproducible

3. **ISS-036: Variables with commas fail in definitions (context-dependent)**
   - **Errors:** 69
   - **Test file:** `tests/test_iss_036_comma_subscript_symbol_not_iterable.md` (11 errors, 13 instances confirmed)
   - **Status:** ✅ Reproducible (but context-dependent - requires many variables defined earlier)
   - **Key insight:** Simple test cases work, but bug manifests when many variables (especially with commas) are defined earlier in document

### User Errors

- **None found** - All 98 errors were classified as LiveMathTeX bugs

## What Was Tricky

### 1. Context-Dependent Bug (ISS-036)

**Problem:** Initial test cases for ISS-036 passed (0 errors), but the original document failed with 69 errors.

**Root cause:** The bug is context-dependent - it only manifests when:
- Many variables are defined earlier in the document (80+ variables)
- Some of those variables have commas in subscripts (P_{LED,dc}, P_{LED,ac}, m_{ax,rct})
- Then defining a new variable with comma using expression with other variables with commas fails

**Solution:** Created test file with full context (lines 1-490 from original document) to reproduce the bug. This required:
- Binary search to find minimal failing case (line 482)
- Incremental testing to identify what triggers the bug
- Copying exact failing section to test file

**Lesson:** Some bugs require significant context to reproduce. The command should emphasize that test files MUST fail, and if a simple test passes, the test file needs to be expanded with more context from the original document.

### 2. Multiple Error Patterns

**Problem:** 98 errors seemed overwhelming, but they actually fell into just 3 patterns.

**Solution:** Used `grep` to count unique error messages, which revealed:
- "argument of type 'Symbol' is not iterable" (73 errors - ISS-036 + ISS-037)
- "I expected something else here" (25 errors - ISS-038)

**Lesson:** Always group errors by message pattern first - this makes classification much faster.

### 3. Test File Must Actually Fail

**Problem:** Initially created test files that passed, which violates the requirement that test files must reproduce the bug.

**Solution:** User correctly pointed out that test files MUST fail. Spent significant time simplifying the original document to find minimal failing case, then copied that to test file.

**Lesson:** The command should be more explicit: "Test file MUST fail when processed. If test file passes, expand it with more context from original document until it fails."

## Command Improvements Needed

### 1. Test File Validation

**Current:** Command says to create test file, but doesn't verify it fails.

**Improvement needed:**
- After creating test file, automatically verify it fails: `livemathtex process test_file.md`
- If test file passes, warn user and suggest expanding with more context
- Only proceed to create issue if test file actually fails

### 2. Context-Dependent Bug Detection

**Current:** No guidance on handling context-dependent bugs.

**Improvement needed:**
- Add step: "If simple test case passes but original document fails, expand test case with more context from original document"
- Suggest binary search approach: start with full document, then remove sections until bug disappears, then add back minimal needed context

### 3. Error Pattern Grouping

**Current:** Command processes errors one by one.

**Improvement needed:**
- Add step before classification: "Group errors by error message pattern"
- Show summary: "Found X unique error patterns: [list]"
- Classify patterns first, then handle individual errors within each pattern

### 4. Test File Naming

**Current:** Test files use descriptive names, but don't indicate if they're minimal or context-dependent.

**Improvement needed:**
- For context-dependent bugs, add note in test file: "**Note:** This test requires significant context to reproduce. Simple test cases pass, but this expanded version fails."
- Consider separate naming: `test_iss_XXX_minimal.md` vs `test_iss_XXX_context_dependent.md`

## Files Created/Modified

### Test Files
- `tests/test_iss_036_comma_subscript_symbol_not_iterable.md` (450 lines, 11 errors - context-dependent)
- `tests/test_iss_037_table_cell_symbol_not_iterable.md` (70 lines, 1 error)
- `tests/test_iss_038_comma_subscript_expression_parse_error.md` (70 lines, 2 errors)

### Documentation
- `.planning/ISSUES.md` - Added ISS-036, ISS-037, ISS-038
- `.planning/LESSONS_LEARNED.md` - Added workarounds for all 3 bugs
- `.planning/.debug-calculations-status.json` - Status tracking

### Temporary Files (not committed)
- `temp_input_clean.md` - Cleaned source document
- `temp_output_actual.md` - Processed output with errors
- `/tmp/test_*.md` - Various test iterations

## Time Spent

- **Total time:** ~30 minutes
- **Most time spent on:** Finding minimal failing case for ISS-036 (context-dependent bug)
- **Could be faster:** If command had better guidance on context-dependent bugs

## User Feedback

- **Critical requirement:** Test files MUST fail - cannot create issue without reproducible test case
- **Important insight:** If test passes but original fails, need to expand test with more context
- **Decision:** ENOUGH - stop debugging, no commit to original document

---

**Date:** 2026-01-15
**Status:** Complete (user said ENOUGH)
