[LiveMathTeX](../README.md) / Known Issues & Backlog

# Known Issues & Backlog

This document tracks known limitations and planned improvements for LiveMathTeX.

---

## Critical Issues

### ISSUE-003: Failed variable definition still allows unit interpretation in subsequent formulas

**Status:** OPEN
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

## Medium Priority

### ISSUE-004: Need `livemathtex clear` command to reset document calculations

**Status:** OPEN
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

## Low Priority / Nice-to-Have

*(None currently)*

---

## Resolved Issues

### ISSUE-002: Remove all hardcoded unit lists - use Pint as single source of truth

**Status:** RESOLVED
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

### ISSUE-001: `value:` directive doesn't support complex/custom units

**Status:** RESOLVED
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

## Contributing

When adding new issues:
1. Use format: `ISSUE-XXX: Brief title`
2. Include: Status, Priority, Discovered date, Context
3. Describe: Problem, What works/doesn't, Root cause, Impact
4. Propose: Solution options with short/medium/long term
5. List: Affected files and workarounds

---

*Last updated: 2026-01-08 (ISSUE-004 opened, ISSUE-003 opened, ISSUE-002 resolved)*
