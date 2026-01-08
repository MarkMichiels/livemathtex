[LiveMathTeX](../README.md) / Known Issues & Backlog

# Known Issues & Backlog

This document tracks known limitations and planned improvements for LiveMathTeX.

---

## Issue Index

| # | Status | Priority | Description |
|---|--------|----------|-------------|
| [ISSUE-001](#issue-001-value-directive-doesnt-support-complexcustom-units) | ✅ Resolved | High | `value:` directive doesn't support complex/custom units |
| [ISSUE-002](#issue-002-remove-all-hardcoded-unit-lists---use-pint-as-single-source-of-truth) | ✅ Resolved | High | Remove all hardcoded unit lists |
| [ISSUE-003](#issue-003-failed-variable-definition-still-allows-unit-interpretation-in-subsequent-formulas) | 🔴 Open | Critical | Failed variable definition allows unit fallback |
| [ISSUE-004](#issue-004-need-livemathtex-clear-command-to-reset-document-calculations) | 🟡 Open | Medium | Need `livemathtex clear` command |
| [ISSUE-005](#issue-005-document-directive-parser-does-not-ignore-code-blocks) | 🟡 Open | Medium | Directive parser doesn't ignore code blocks |
| [ISSUE-006](#issue-006-latex-wrapped-units-text-not-parsed-by-pint) | 🟡 Open | Medium | LaTeX-wrapped units not parsed by Pint |

---

## ISSUE-001: `value:` directive doesn't support complex/custom units

**Status:** ✅ RESOLVED
**Priority:** High
**Discovered:** 2026-01-08
**Resolved:** 2026-01-08

**Problem:**
The `value:` directive for displaying variable values in tables only supported simple units from a hardcoded `unit_map`. Custom units (EUR, €), energy units (MWh, kWh), and compound units (MWh/kg) did not work.

**Solution implemented:**
1. **Pint-based unit conversion** - `_get_numeric_in_unit_latex()` now uses Pint via `convert_value_to_unit()` for unit conversion
2. **Custom unit registration** - Unit definitions (`===`) are registered in both Pint and SymPy registries
3. **Complete unit support** - All Pint-recognized units now work in value directives, including:
   - Energy: MWh, kWh, GWh
   - Currency: EUR (€), USD ($)
   - Compound: MWh/kg, €/kWh
4. **Removed `units.py`** - All unit handling consolidated in `pint_backend.py`

**Test coverage:**
- Added ISSUE-001 test section in `examples/custom-units/input.md`
- Tests MWh conversion (5000 kWh → 5 MWh)
- Tests EUR value display
- All 76 tests passing

**Files changed:**
- `src/livemathtex/engine/evaluator.py` - Use Pint for value: directive conversions
- `src/livemathtex/engine/pint_backend.py` - Added `convert_value_to_unit()`, SymPy compatibility layer
- `src/livemathtex/engine/units.py` - REMOVED (all code migrated to pint_backend.py)
- `examples/custom-units/input.md` - Added ISSUE-001 test cases

---

## ISSUE-002: Remove all hardcoded unit lists - use Pint as single source of truth

**Status:** ✅ RESOLVED
**Priority:** High
**Discovered:** 2026-01-08
**Resolved:** 2026-01-08

**Problem:**
The codebase contained **4 separate hardcoded unit lists** across 2 files, totaling ~230 unit definitions:
- `evaluator.py`: `RESERVED_UNIT_NAMES` (~50), `unit_map` (~20), `unit_mapping` (~40)
- `pint_backend.py`: `UNIT_ABBREVIATIONS` (~50)

**Key Discovery:** Pint already recognizes almost everything natively (MWh, kWh, m³/h, µm, etc.). Only currency (€, $) needs custom definition.

**Solution Implemented:**

All 4 hardcoded lists removed and replaced with dynamic Pint queries:
- `is_pint_unit()` - Check if token is Pint-recognized
- `is_custom_unit()` - Check if token is user-defined
- `pint_to_sympy_with_prefix()` - Dynamic Pint → SymPy conversion

**Result:**
- **Before:** ~230 hardcoded unit definitions
- **After:** 0 hardcoded definitions; Pint is single source of truth
- **Tests:** 102 passing (76 existing + 26 new in `tests/test_unit_recognition.py`)

**Files Changed:**
- `evaluator.py` - Removed all hardcoded unit lists
- `pint_backend.py` - Removed `UNIT_ABBREVIATIONS`, added dynamic functions
- `examples/unit-library/` - Updated as canonical custom unit reference

---

## ISSUE-003: Failed variable definition still allows unit interpretation in subsequent formulas

**Status:** 🔴 OPEN
**Priority:** Critical
**Discovered:** 2026-01-08

**Problem:**
When a variable definition fails due to a name conflict with a unit (e.g., `V` conflicts with Volt), the system:
1. ✅ Correctly shows an error at the definition site
2. ❌ **Incorrectly** still interprets `V` as the unit Volt in all subsequent formulas

**Example:**
```latex
$V := 37824$                        % Error: conflicts with 'volt'
$Cap := V \cdot 15 \cdot 0.001$     % Should ERROR, but instead interprets V as Volt!
```

**Observed behavior:**
- Definition `V := 37824` shows error (correct)
- Subsequent formula `Cap := V · 15 · 0.001` evaluates with `V = 1 volt`
- Result: `Cap = 0.000015 kg·m²/(A·s³)` (units of voltage × numbers)

**Expected behavior:**
If a definition fails, the variable should be **completely undefined**, and any subsequent use should produce:
- Either: An "undefined variable" error
- Or: A propagated error from the failed definition

**Root cause:**
The error handling for unit conflicts only blocks the definition assignment, but doesn't prevent the parser from falling back to interpreting the token as a unit in later formulas.

**Impact:**
- Results silently become wrong with nonsensical units
- Users may not notice the error if they don't check the first line
- All downstream calculations are corrupted

**Proposed solution:**
1. Track failed variable definitions in a "blacklist"
2. When a token matches both a failed variable AND a unit, produce an error rather than silently using the unit
3. Alternative: Don't produce error at definition - suggest subscript and proceed with unitless interpretation

**Workaround:**
Use subscripted variable names to avoid unit conflicts:
```latex
$V_{tot} := 37824$      % OK - no conflict
$Cap := V_{tot} \cdot 15 \cdot 0.001$  % Works correctly
```

**Affected formulas in user document:**
All `Cap_XX` and `C_XX` and `U_XX` calculations showed wrong units because `V` was interpreted as Volt instead of failing completely.

---

## ISSUE-004: Need `livemathtex clear` command to reset document calculations

**Status:** 🟡 OPEN
**Priority:** Medium
**Discovered:** 2026-01-08

**Problem:**
After running `livemathtex process`, the document contains:
1. Computed values to the right of `==` (e.g., `$x == 42$`)
2. Error messages embedded in LaTeX (`\\ \color{red}{\text{Error: ...}}`)
3. A meta comment with timestamp and statistics

When errors occur or the document needs to be "reset" for a fresh calculation cycle, there is no command to clean the document back to its original state.

**Current workflow (manual and error-prone):**
1. User makes changes to document
2. Runs `livemathtex process` (F9)
3. Sees errors or wrong values
4. Must **manually** remove all computed values and errors
5. Fix the formulas
6. Run process again

**Desired workflow:**
1. User makes changes to document
2. Runs `livemathtex process` (F9)
3. Sees errors or wrong values
4. Runs `livemathtex clear` (Shift-F9) - document is reset
5. Fix the formulas
6. Run process again

**Proposed `livemathtex clear` command:**

```bash
livemathtex clear <input.md> [-o <output.md>]
```

**What it should do:**
1. **Remove computed values** after `==`:
   - `$x := 5 \cdot 2 == 10$` → `$x := 5 \cdot 2 ==$`
   - `$y == 42$` → `$y ==$`

2. **Remove error markup**:
   - `$x == 10 \\ \color{red}{\text{Error: ...}}$` → `$x ==$`

3. **Remove or reset meta comment**:
   - `> *livemathtex: 2026-01-08 ... | 15 errors | ...* <!-- livemathtex-meta -->` → remove or reset

4. **Preserve**:
   - All definitions (`:=`) with their formulas (left side of `==`)
   - Unit definitions (`===`)
   - All markdown structure
   - Comments

**Use cases:**
1. **Debug workflow:** Error → clear → fix → process → verify
2. **Validation workflow:** User fills in expected values, processes, compares diff
3. **Clean commits:** Clear before committing to avoid noise in diffs
4. **Fresh start:** Reset document after major restructuring

**Implementation approach:**
1. Add `clear` subcommand to `cli.py`
2. Use regex or parser to identify:
   - `== <value>` patterns → strip value
   - `\\ \color{red}{...}` patterns → remove entirely
   - `<!-- livemathtex-meta -->` lines → remove
3. Output cleaned document (same options as `process`: timestamped, inplace, or custom output)

**Regex patterns (initial approach):**
```python
# Remove computed value after ==
r'\s*==\s*[^$]+(?=\$)'  →  ' =='

# Remove error markup
r'\s*\\\\\s*\\color\{red\}\{\\text\{[^}]+\}\}'  →  ''

# Remove meta comment
r'^>?\s*\*livemathtex:.*<!-- livemathtex-meta -->\s*$'  →  ''
```

**Alternative: Parser-based approach:**
Use the existing Lexer to identify math blocks, then strip computed portions. More robust but more complex.

**Files to modify:**
- `src/livemathtex/cli.py` - Add `clear` subcommand
- `src/livemathtex/core.py` - Add `clear_file()` function (or new `cleaner.py` module)
- `.cursor/commands/livemathtex.md` - Document the new command

**Integration with Cursor:**
After CLI implementation, the Cursor command can be updated to support Shift-F9 for clearing, providing a complete edit → process → clear → fix cycle.

---

## ISSUE-005: Document directive parser does not ignore code blocks

**Status:** 🟡 OPEN
**Priority:** Medium
**Discovered:** 2026-01-08

**Problem:**
The `parse_document_directives()` function in `lexer.py` scans the entire document for `<!-- livemathtex: ... -->` patterns, but does **not** skip content inside fenced code blocks (``` ... ```).

This causes directives shown as **examples** in documentation to be parsed and applied as if they were real configuration.

**Example (README.md):**
```markdown
<!-- livemathtex: output=timestamped -->   ← Line 14: Real directive

Output behavior is configurable. To overwrite in place:

```markdown
<!-- livemathtex: output=inplace -->       ← Line 68: EXAMPLE in code block
```
```

**Observed behavior:**
- Parser finds both directives
- Later directive wins → `output=inplace`
- Document is processed in-place instead of timestamped

**Expected behavior:**
Content inside fenced code blocks should be completely ignored by the directive parser.

**Root cause:**
`DOCUMENT_DIRECTIVE_RE` regex scans raw content without first stripping code blocks.

**Proposed solution:**
1. Before scanning for directives, remove all fenced code blocks from content
2. Or: Modify regex to use negative lookbehind for code fence context
3. Or: Use the existing `Document` parse tree which already identifies `CodeBlock` nodes

**Implementation approach (option 1 - simplest):**
```python
def parse_document_directives(self, content: str) -> Dict[str, Any]:
    # Strip fenced code blocks before scanning
    content_no_code = re.sub(r'```[\s\S]*?```', '', content)
    content_no_code = re.sub(r'~~~[\s\S]*?~~~', '', content_no_code)

    directives = {}
    for match in self.DOCUMENT_DIRECTIVE_RE.finditer(content_no_code):
        # ... rest of parsing
```

**Files to modify:**
- `src/livemathtex/parser/lexer.py` - `parse_document_directives()` method

**Workaround:**
Ensure example directives in documentation use different syntax that won't match, e.g.:
```markdown
```text
< !-- livemathtex: output=inplace -- >   ← Spaces break the pattern
```
```

---

## ISSUE-006: LaTeX-wrapped units (`\text{...}`) not parsed by Pint

**Status:** 🟡 OPEN
**Priority:** Medium
**Discovered:** 2026-01-08

**Problem:**
When units are written with LaTeX formatting like `\text{m/s}^2`, Pint cannot parse them. The `\text{...}` wrapper and LaTeX escape sequences break Pint's unit parser.

**Example:**
```latex
$a_1 := 9.81\ \text{m/s}^2$
$F_1 := m_1 \cdot a_1$
$F_1 ==$ <!-- [N] -->
```

**Observed behavior (from IR JSON):**
```json
"a_1": {
    "original": {
        "value": 9.81,
        "unit": "\\text{m/s}^2"
    },
    "conversion_ok": false,
    "conversion_error": "('unexpected character after line continuation character', (1, 14))"
}
```

Because `a_1` has no valid unit, `F_1 = m_1 · a_1` becomes unitless, and the `<!-- [N] -->` conversion request fails silently.

**Expected behavior:**
The system should:
1. Strip LaTeX formatting (`\text{...}`, `\mathrm{...}`, etc.) from unit strings
2. Convert LaTeX escapes (`^2` → `**2`, `\cdot` → `*`)
3. Pass clean unit string to Pint: `m/s**2`
4. Result: `F_1` correctly has unit `kg·m/s²` = `N`

**Root cause:**
Unit extraction passes raw LaTeX to Pint without preprocessing.

**Proposed solution:**

Add a `clean_latex_unit()` function before Pint parsing:

```python
def clean_latex_unit(latex_unit: str) -> str:
    """
    Convert LaTeX unit notation to Pint-compatible string.

    Examples:
        \\text{m/s}^2  →  m/s**2
        \\mathrm{kg}   →  kg
        m^3            →  m**3
        \\cdot         →  *
    """
    unit = latex_unit

    # Remove \text{...} and \mathrm{...} wrappers
    unit = re.sub(r'\\text\{([^}]+)\}', r'\1', unit)
    unit = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', unit)

    # Convert LaTeX exponents to Python
    unit = re.sub(r'\^(\d+)', r'**\1', unit)
    unit = re.sub(r'\^\{(\d+)\}', r'**\1', unit)

    # Convert multiplication
    unit = unit.replace('\\cdot', '*')
    unit = unit.replace('·', '*')

    # Remove remaining backslashes and extra spaces
    unit = unit.replace('\\', '')
    unit = unit.strip()

    return unit
```

**Files to modify:**
- `src/livemathtex/engine/pint_backend.py` - Add `clean_latex_unit()`
- `src/livemathtex/engine/evaluator.py` - Call `clean_latex_unit()` before Pint conversion

**Test cases to add:**
```python
def test_latex_unit_cleaning():
    assert clean_latex_unit("\\text{m/s}^2") == "m/s**2"
    assert clean_latex_unit("\\mathrm{kg}") == "kg"
    assert clean_latex_unit("m^3") == "m**3"
    assert clean_latex_unit("kg \\cdot m/s^2") == "kg * m/s**2"
    assert clean_latex_unit("\\text{kW} \\cdot \\text{h}") == "kW * h"
```

**Workaround:**
Write units without LaTeX wrappers:
```latex
$a_1 := 9.81\ m/s^2$        % Works (if parser handles ^2)
$a_1 := 9.81\ \frac{m}{s^2}$  % May work with fraction parsing
```

---

## Contributing

When adding new issues:
1. Use format: `ISSUE-XXX: Brief title`
2. Include: Status, Priority, Discovered date, Context
3. Describe: Problem, What works/doesn't, Root cause, Impact
4. Propose: Solution options with short/medium/long term
5. List: Affected files and workarounds

---

*Last updated: 2026-01-08*
