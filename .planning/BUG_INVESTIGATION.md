# Bug Investigation: In-Place Processing Issues with Processed Files

## Summary

When processing an already-processed output file multiple times, or after clearing it, unexpected changes occur. The file should remain stable (only timestamp should change) but instead:
1. Additional errors appear on repeated processing
2. File content changes after clearing and re-processing
3. Error markup is not fully cleaned, causing parsing issues

## Test Scenario

**Setup:**
- `input.md` with directive: `<!-- livemathtex: output=output.md, json=true -->`
- `output.md` is the processed output file

**Steps and Expected vs Actual Behavior:**

### Scenario 1: F9 on input.md → output.md generated ✅
**Action:** Press F9 on `input.md`
**Expected:** `output.md` is generated/updated with calculations and errors displayed
**Actual:** ✅ Works correctly - output.md contains calculated values and error markup

### Scenario 2: Shift+F9 on input.md → output.md cleaned ✅
**Action:** Press Shift+F9 on `input.md`
**Expected:** `output.md` is overwritten with clean version (no calculations, clean content)
**Actual:** ✅ Works correctly - output.md is overwritten with clean content from input.md

### Scenario 3: F9 on output.md (first time) ✅
**Action:** Press F9 on `output.md` (after it was cleaned in Scenario 2)
**Expected:** `output.md` is recalculated in-place, same result as Scenario 1
**Actual:** ✅ Works correctly - output.md is recalculated and matches Scenario 1 result

### Scenario 4: F9 on output.md (second time) ❌ BUG
**Action:** Press F9 on `output.md` again (already processed)
**Expected:**
- File should NOT change (already processed)
- Only timestamp in metadata should update
- No new errors should appear

**Actual:** ❌ **BUG**
- File content changes
- Additional errors appear (e.g., error markup in middle of document)
- Content is not stable

**Example of unexpected change:**
```markdown
# Before second F9:
$V := 37824
\\ }$

# After second F9:
$V := 37824
\\ }$
# (but with additional error markup or parsing issues)
```

### Scenario 5: Shift+F9 on output.md ❌ BUG
**Action:** Press Shift+F9 on `output.md` (to clear computed values)
**Expected:**
- All computed values removed (`== value$` → `==$`)
- All error markup removed
- File ready for re-processing

**Actual:** ❌ **BUG**
- Computed values are cleared
- Error markup is removed
- BUT: File is not fully cleaned - some artifacts remain that cause issues on re-processing

### Scenario 6: F9 on output.md after Shift+F9 ❌ BUG
**Action:** Press F9 on `output.md` after clearing it (Scenario 5)
**Expected:**
- Should produce same result as Scenario 1 (original processing from input.md)
- Same errors, same calculations

**Actual:** ❌ **BUG**
- Many additional errors appear
- Different file content than original
- File is corrupted or incorrectly parsed

## Root Cause Analysis

### Issue 1: Error Markup Not Fully Cleaned

The `clear_text()` function in `src/livemathtex/core.py` removes error markup using regex patterns:

```python
# Pattern 3: Remove error markup (red color)
error_pattern = r'\\color\{red\}\{[^}]*\}'

# Pattern 4: Remove inline error text
error_text_pattern = r'\\text\{\(Error:[^)]*\)\}'

# Pattern 5: Remove newline + error continuation
multiline_error = r'\s*\\\\\s*\\color\{red\}\{\\text\{[^}]*\}\}'
```

**Problem:** These patterns may not catch all error markup formats, especially:
- Multiline errors with complex LaTeX escaping
- Errors that span multiple lines with different formatting
- Error markup that was partially processed

**Evidence:**

1. **Incomplete math blocks with error artifacts** (lines 15-16, 27-28, 37-38, 49-50, 64-65, 79-80, 92-93):
```markdown
$V := 37824
\\ }$
```
The `\\ }$` is error markup that should be removed, but the current regex patterns don't catch this format. This leaves incomplete math blocks that confuse the parser on re-processing.

2. **Multiline error format** (lines 157-159):
```markdown
$\text{aantal} ==
\\ \color{red}{\text{
    Error: Undefined variable 'textv\_14'. Define it before use.}}$
```
This multiline error format may not be fully cleaned by the current regex patterns, especially when it spans multiple lines with complex LaTeX escaping.

3. **Error patterns found in output.md:**
   - `\\ }$` - Incomplete math block terminator (appears 7 times)
   - `\\ \color{red}{\text{...}}` - Multiline error markup (appears 5 times)

These patterns are not fully handled by the current `clear_text()` regex patterns.

### Issue 2: Parser Confusion with Error Artifacts

When a file contains error markup that wasn't fully cleaned, the parser (`lexer.py`) may:
- Misinterpret incomplete math blocks
- Treat error markup as part of the math expression
- Create incorrect `MathBlock` objects

**Example:**
```markdown
$V := 37824
\\ }$
```

The `\\ }$` is error markup that should be removed, but if it remains, the parser sees an incomplete math block.

### Issue 3: In-Place Processing Doesn't Check for Already-Processed State

When processing `output.md` with `output=output.md` directive (in-place), the system:
1. Reads the file (which may contain error markup)
2. Parses it (may misinterpret error artifacts)
3. Processes it (may generate new errors from misinterpreted content)
4. Writes back (overwrites with potentially different content)

**Problem:** There's no check to see if the file is already in a "stable processed state" where only the timestamp should change.

### Issue 4: Clear Function Doesn't Restore Original Input State

The `clear_text()` function removes computed values and errors, but:
- It doesn't restore the file to the exact state of `input.md`
- It may leave behind formatting artifacts
- It may not handle all edge cases of error markup removal

**Result:** After clearing, the file is not in the same state as the original input, so re-processing generates different results.

## Recommended Fixes

### Fix 1: Improve Error Markup Cleaning

Enhance `clear_text()` to handle all error markup formats:
- **Fix incomplete math blocks:** Remove `\\ }$` patterns (incomplete math block terminators)
- **Fix multiline errors:** Improve regex to handle `\\ \color{red}{\text{...}}` across multiple lines
- **Add comprehensive patterns:** Test with all error types from the error catalog
- **Handle edge cases:** Ensure all LaTeX escaping variations are caught

**Specific patterns to add:**
```python
# Pattern: Remove incomplete math block terminators
# Matches: \\ }$ or \\}$ at end of line (error artifact)
incomplete_math_pattern = r'\\\s*\}\$'

# Pattern: Remove multiline error with newlines
# Matches: \\ \color{red}{\text{...}} with newlines inside
multiline_error_improved = r'\\\s*\\color\{red\}\{[^}]*\}'
```

### Fix 2: Add Stability Check for In-Place Processing

When processing a file in-place:
- Compare parsed content with current file content
- If only metadata differs, only update metadata
- Prevent unnecessary re-processing of stable content

### Fix 3: Improve Clear Function

Ensure `clear_text()` fully restores file to processable state:
- Remove ALL error markup (comprehensive patterns)
- Remove ALL computed values
- Ensure file can be re-processed to identical result

### Fix 4: Add Regression Tests

Create test cases for:
- Multiple F9 presses on same file (should be stable)
- Clear → Process cycle (should match original)
- Error markup cleaning (all formats)

## Files Involved

- `src/livemathtex/core.py` - `clear_text()` function, `process_file()` function
- `src/livemathtex/parser/lexer.py` - Math block parsing, error handling
- `src/livemathtex/cli.py` - `process` and `copy` commands

## Test Files

- `examples/error-handling/input.md` - Original input
- `examples/error-handling/output.md` - Processed output (shows the bugs)

## Priority

**High** - This affects the core workflow of processing → clearing → re-processing, which is a common use case.
