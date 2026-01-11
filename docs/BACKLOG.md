[LiveMathTeX](../README.md) / Backlog

# Issues & Features

This document tracks known limitations (ISSUE), planned improvements (FEAT), and resolved items for LiveMathTeX.

---

## Index

### Issues (Bugs & Problems)

| # | Status | Priority | Description |
|---|--------|----------|-------------|
| [ISSUE-001](#issue-001-value-directive-doesnt-support-complexcustom-units) | ✅ Resolved | High | `value:` directive doesn't support complex/custom units |
| [ISSUE-002](#issue-002-remove-all-hardcoded-unit-lists---use-pint-as-single-source-of-truth) | ✅ Resolved | High | Remove all hardcoded unit lists |
| [ISSUE-003](#issue-003-failed-variable-definition-still-allows-unit-interpretation-in-subsequent-formulas) | ✅ Resolved | Critical | Failed variable definition allows unit fallback |
| [ISSUE-004](#issue-004-document-directive-parser-does-not-ignore-code-blocks) | ✅ Resolved | Medium | Directive parser doesn't ignore code blocks |
| [ISSUE-005](#issue-005-latex-wrapped-units-text-not-parsed-by-pint) | ✅ Resolved | Medium | LaTeX-wrapped units not parsed by Pint |
| [ISSUE-006](#issue-006-incompatible-unit-operations-silently-produce-wrong-results) | ✅ Resolved | High | Incompatible unit operations silently produce wrong results |
| [ISSUE-007](#issue-007-evaluation-results-show-si-base-units-instead-of-requested-output-unit) | 🟡 Open | Medium | Evaluation results show SI base units instead of requested output unit |
| [ISSUE-008](#issue-008-output-unit-hint-syntax-requires-html-comment) | 🟡 Open | Low | Output unit hint syntax requires HTML comment |
| [ISSUE-009](#issue-009-compound-unit-definitions-fail-with-division) | 🟡 Open | Medium | Compound unit definitions fail with division |

### Features (Enhancements & New Functionality)

| # | Status | Priority | Description |
|---|--------|----------|-------------|
| [FEAT-001](#feat-001-expose-public-python-api-for-library-usage) | 🟡 Open | Medium | Expose public Python API for library usage |
| [FEAT-002](#feat-002-livemathtex-clear-command-to-reset-document-calculations) | 🟡 Open | Medium | `livemathtex clear` command to reset calculations |

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

**Status:** ✅ RESOLVED
**Priority:** Critical
**Discovered:** 2026-01-08
**Resolved:** 2026-01-11

**Problem:**
When a variable definition fails due to a name conflict with a unit (e.g., `V` conflicts with Volt), the system:
1. ✅ Correctly shows an error at the definition site
2. ❌ **Incorrectly** still interprets `V` as the unit Volt in all subsequent formulas

**Example:**
```latex
$V := 37824$                        % Error: conflicts with 'volt'
$Cap := V \cdot 15 \cdot 0.001$     % Should ERROR, but instead interprets V as Volt!
```

**Solution implemented:**

The root cause was in `_compute()` where undefined symbols that matched unit names would silently fall back to unit interpretation when the expression contained decimals (triggering `is_definition_with_units=True`).

**Fix:** Remove the unit fallback entirely. Undefined symbols that match unit names now ALWAYS produce an error:

```
Error: Undefined variable 'V'. (Note: 'V' is also a unit (volt).
Units must be attached to numbers like '5\ V', not used as standalone symbols in formulas.)
```

**Key insight:** Units belong as suffixes to numbers (`5\ V`), not as standalone symbols in formulas. The `\cdot` multiplication syntax (`10 \cdot kg`) is incorrect - use backslash-space (`10\ kg`) for unit attachment.

**Breaking change:** Expressions like `$m_1 := 10 \cdot kg$` that previously worked (by interpreting `kg` as a unit) now require correct syntax: `$m_1 := 10\ kg$`.

**Files changed:**
- `src/livemathtex/engine/evaluator.py` - Remove unit fallback in `_compute()`
- `tests/test_definition_types.py` - New test file for definition type handling
- `examples/error-handling/` - New example demonstrating all error types
- `examples/simple-units/` - Updated to use correct unit syntax
- `examples/engineering/` - Renamed U→U_0, A→A_0 to avoid conflicts

**Test coverage:**
- 13 new tests in `test_definition_types.py`
- All 115 tests passing

---

## ISSUE-004: Document directive parser does not ignore code blocks

**Status:** ✅ RESOLVED
**Priority:** Medium
**Discovered:** 2026-01-08
**Resolved:** 2026-01-11

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

**Solution implemented:**
Before scanning for directives, strip all fenced code blocks from a temporary copy of the content:

```python
def parse_document_directives(self, content: str) -> Dict[str, Any]:
    # Strip fenced code blocks before scanning (ISSUE-004)
    content_for_scan = re.sub(r'```[\s\S]*?```', '', content)
    content_for_scan = re.sub(r'~~~[\s\S]*?~~~', '', content_for_scan)

    for match in self.DOCUMENT_DIRECTIVE_RE.finditer(content_for_scan):
        # ... rest of parsing
```

**Test coverage:**
- 8 new tests in `tests/test_lexer_directives.py`
- Tests backtick and tilde code blocks
- Tests multiple code blocks
- Tests edge cases (empty document, only code blocks)
- All 129 tests passing

**Files changed:**
- `src/livemathtex/parser/lexer.py` - Strip code blocks before directive scanning
- `tests/test_lexer_directives.py` - New test file for directive code block skipping

---

## ISSUE-005: LaTeX-wrapped units (`\text{...}`) not parsed by Pint

**Status:** ✅ RESOLVED
**Priority:** Medium
**Discovered:** 2026-01-08
**Resolved:** 2026-01-11

**Problem:**
When units are written with LaTeX formatting like `\text{m/s}^2`, Pint cannot parse them. The `\text{...}` wrapper and LaTeX escape sequences break Pint's unit parser.

**Example:**
```latex
$a_1 := 9.81\ \text{m/s}^2$
$F_1 := m_1 \cdot a_1$
$F_1 ==$ <!-- [N] -->
```

**Solution implemented:**

Added `clean_latex_unit()` function to `pint_backend.py` that converts LaTeX unit notation to Pint-compatible strings:

1. **Wrapper removal:** `\text{...}`, `\mathrm{...}`, `\mathit{...}`, `\textit{...}`, `\mathbf{...}`
2. **Fraction conversion:** `\frac{m}{s^2}` -> `m/s**2`
3. **Exponent conversion:** `^2` -> `**2`, `^{-3}` -> `**-3`
4. **Multiplication:** `\cdot` and Unicode middle dot (·) -> `*`
5. **Cleanup:** Remove remaining LaTeX escapes, normalize whitespace

The function is now integrated into:
- `is_unit_token()` - Checks if LaTeX unit string is valid
- `get_unit()` - Gets Pint Unit from LaTeX notation
- `parse_unit_string()` - Main unit parsing function

**Test coverage:**
- 11 new tests in `tests/test_pint_backend.py::TestCleanLatexUnit`
- All 140 tests passing

**Files changed:**
- `src/livemathtex/engine/pint_backend.py` - Added `clean_latex_unit()`, integrated into unit parsing functions
- `tests/test_pint_backend.py` - Added TestCleanLatexUnit test class

---

## ISSUE-006: Incompatible unit operations silently produce wrong results

**Status:** ✅ RESOLVED
**Priority:** High
**Discovered:** 2026-01-11
**Resolved:** 2026-01-11

**Problem:**
When adding or subtracting quantities with incompatible units (e.g., kg + m), the system silently produces numerically wrong results instead of raising an error.

**Example (before fix):**
```latex
$m_1 := 5\ kg$
$d_1 := 3\ m$
$nonsense := m_1 + d_1 ==$    % Displayed: 8 (wrong!)
```

**Solution implemented:**

Used Option A from the proposed solutions: Pre-check dimensional compatibility.

1. **Added helper functions to `pint_backend.py`:**
   - `get_unit_dimensionality()` - Get Pint dimensionality for unit string
   - `get_sympy_unit_dimensionality()` - Extract dimensionality from SymPy expressions
   - `are_dimensions_compatible()` - Check if two dimensions can be added/subtracted

2. **Added dimensional check to `evaluator.py`:**
   - `_check_dimensional_compatibility()` - Entry point after `_compute()`
   - `_check_add_dimensional_compatibility()` - Recursive check for Add expressions
   - Called in both `_handle_evaluation()` and `_handle_assignment_evaluation()`

**Error message format:**
```
Error: Cannot add/subtract incompatible units: kilogram and meter.
Dimensions must match for addition/subtraction.
```

**Test coverage:**
- 8 tests in `tests/test_dimensional_analysis.py`:
  - `TestIncompatibleUnits`: 3 tests for error detection (kg+m, s-m/s, 3 terms)
  - `TestCompatibleUnits`: 3 tests for allowed operations (kg+kg, km+m, unitless)
  - `TestEdgeCases`: 2 tests for multiplication/division (different units OK)

**Files changed:**
- `src/livemathtex/engine/pint_backend.py` - Added 3 helper functions
- `src/livemathtex/engine/evaluator.py` - Added dimensional check methods
- `tests/test_dimensional_analysis.py` - New test file (8 tests)
- `examples/error-handling/input.md` - Added Category 5: Dimension Mismatch Errors

**Result:**
- All 148+ tests passing
- Incompatible unit additions/subtractions now produce clear errors
- Compatible operations (same dimension, different scale) still work
- Multiplication/division of different units still works

---

## ISSUE-007: Evaluation results show SI base units instead of requested output unit

**Status:** 🟡 OPEN
**Priority:** Medium
**Discovered:** 2026-01-11

**Problem:**
When evaluating expressions with units, the result is displayed in SI base units (kg·m²/s²) instead of the user's preferred output unit specified in the `<!-- [unit] -->` comment.

**Example:**
```latex
$P_{sys} := 310.7\ kW$
$t_{yr} := 1\ yr$
$E := P_{sys} \cdot t_{yr} == 2\,722\,000\,000\ \text{kg} \cdot \text{m}^{2}/\text{s}^{2}$ <!-- [MWh] -->
```

**Expected:**
```latex
$E := P_{sys} \cdot t_{yr} == 2722\ \text{MWh}$
```

**Current workaround:**
Use dimensionless numbers with manual unit tracking:
```latex
$P := 310.7$  % kW (dimensionless)
$t := 8760$   % hours/year
$E := P \cdot t \cdot 0.001 == 2722$  % MWh
```

**Root cause:**
The evaluator computes in SI base units and formats the result directly. The `<!-- [unit] -->` comment is not parsed or used for unit conversion in the output.

**Proposed solution:**
1. Parse the `<!-- [unit] -->` comment after `==`
2. Convert the computed result to the requested unit using Pint
3. Format the result with the requested unit

**Files to change:**
- `src/livemathtex/parser/lexer.py` - Parse output unit hints
- `src/livemathtex/engine/evaluator.py` - Apply unit conversion before formatting
- `src/livemathtex/engine/pint_backend.py` - Add conversion helper

**Effort:** Medium (4-6 hours)

---

## ISSUE-008: Output unit hint syntax requires HTML comment

**Status:** 🟡 OPEN
**Priority:** Low
**Discovered:** 2026-01-11

**Problem:**
The current syntax for specifying output units uses HTML comments:
```latex
$E == 2722$ <!-- [MWh] -->
```

This is:
1. Verbose and breaks reading flow
2. Invisible in rendered Markdown
3. Easy to forget or misplace

**Proposed syntax options:**

**Option A: Inline after `==` (recommended)**
```latex
$E == [MWh]$
```
The `[unit]` is parsed and replaced with the converted value.

**Option B: LaTeX comment style**
```latex
$E == \% [MWh]$
```

**Option C: Keep HTML but make it optional**
If no unit hint, use "smart" unit selection based on magnitude.

**Depends on:** ISSUE-007 (output unit conversion must work first)

**Files to change:**
- `src/livemathtex/parser/lexer.py` - Parse new syntax
- `src/livemathtex/engine/evaluator.py` - Handle inline unit hints

**Effort:** Small (2-3 hours, after ISSUE-007)

---

## ISSUE-009: Compound unit definitions fail with division

**Status:** 🟡 OPEN
**Priority:** Medium
**Discovered:** 2026-01-11

**Problem:**
Unit definitions (`===`) with division fail to register correctly with Pint:

```latex
$PPE === umol/J$           % FAILS: Pint can't parse this
$SEC === MWh/kg$           % FAILS: Same issue
$\gamma === mg/(L \cdot d)$ % FAILS: Complex compound
```

**Current behavior:**
- Simple aliases work: `$kWh === 1000\ Wh$`
- Multiplied compounds work: `$Wh === W \cdot hour$`
- Division compounds fail silently or produce errors

**Root cause:**
The `===` parser in `pint_backend.py` doesn't properly handle:
1. Division (`/`) in unit expressions
2. Compound units with multiple operators
3. LaTeX-style parentheses in unit expressions

**Workaround:**
Use dimensionless values with documented units:
```latex
$PPE_{red} := 4.29$  % PPE in µmol/J (dimensionless)
```

**Proposed solution:**
1. Extend `register_custom_unit()` to parse compound unit expressions
2. Use Pint's `define()` with proper dimensional analysis
3. Handle division by converting `a/b` to `a * b**-1`

**Example fix:**
```python
# Convert "umol/J" to Pint definition
# umol = 1e-6 mol, J = joule
# So: PPE = umol/J = 1e-6 * mole / joule
ureg.define("PPE = 1e-6 * mole / joule")
```

**Complexity:** This requires understanding of:
- Pint's unit definition syntax
- SI prefixes (µ = 1e-6)
- Compound dimensional analysis

**Files to change:**
- `src/livemathtex/engine/pint_backend.py` - Extend `register_custom_unit()`
- `tests/test_pint_backend.py` - Add compound unit definition tests

**Effort:** Medium-Large (4-8 hours)

---

## FEAT-001: Expose public Python API for library usage

**Status:** 🟡 OPEN
**Priority:** Medium
**Requested:** 2026-01-08

**Request:**
Currently, LiveMathTeX is primarily a CLI tool. The `__init__.py` only exports `main()`, making it difficult to use as a Python library in other projects.

**Current state:**
```python
# src/livemathtex/__init__.py
from .cli import main
__version__ = "0.1.0"
```

**Desired API:**
```python
from livemathtex import process_text, LivemathConfig
from pathlib import Path

# Process markdown string directly
config = LivemathConfig.load(Path("document.md"))
markdown_out, ir = process_text(markdown_in, config)

# Or simpler one-liner
result = livemathtex.process("$x := 5 \cdot 2 ==$")
```

**Use cases:**
1. **Integration in pipelines** - Process documents programmatically
2. **Custom tooling** - Build tools on top of LiveMathTeX
3. **Testing** - Easier unit testing without CLI
4. **IDE plugins** - Direct Python integration

**Proposed changes:**

1. **Extend `__init__.py`:**
```python
from .cli import main
from .core import process_text_v3 as process_text
from .config import LivemathConfig
from .ir.schema import LivemathIR

__version__ = "0.1.0"

__all__ = [
    "main",
    "process_text",
    "LivemathConfig",
    "LivemathIR",
]
```

2. **Add convenience function** (optional):
```python
def process_string(content: str, **kwargs) -> tuple[str, LivemathIR]:
    """Process a markdown string with LiveMathTeX calculations."""
    config = LivemathConfig(**kwargs)
    return process_text(content, config)
```

3. **Update README** to document library usage

**Files to change:**
- `src/livemathtex/__init__.py` - Add exports
- `src/livemathtex/core.py` - Possibly simplify API
- `README.md` - Document library usage
- `docs/USAGE.md` - Add library examples

**Effort:** Small (1-2 hours)

---

## FEAT-002: `livemathtex clear` command to reset document calculations

**Status:** 🟡 OPEN
**Priority:** Medium
**Requested:** 2026-01-08

**Request:**
After running `livemathtex process`, the document contains computed values and error messages. When errors occur or the document needs resetting, there is no command to clean it back to the original state.

**Current workflow (manual and error-prone):**
1. User makes changes to document
2. Runs `livemathtex process` (F9)
3. Sees errors or wrong values
4. Must **manually** remove all computed values and errors
5. Fix the formulas
6. Run process again

**Desired workflow:**
1. User makes changes → `process` (F9) → sees errors → `clear` (Shift-F9) → fix → `process` (F9)

**Proposed command:**
```bash
livemathtex clear <input.md> [-o <output.md>]
```

**What it should do:**
1. **Remove computed values** after `==`:
   - `$x := 5 \cdot 2 == 10$` → `$x := 5 \cdot 2 ==$`
2. **Remove error markup**:
   - `$x == 10 \\ \color{red}{\text{Error: ...}}$` → `$x ==$`
3. **Remove meta comment**:
   - `> *livemathtex: ... <!-- livemathtex-meta -->` → remove
4. **Preserve**: All definitions, unit definitions, markdown structure

**Use cases:**
1. **Debug workflow:** Error → clear → fix → process → verify
2. **Validation workflow:** Fill in expected values, process, compare diff
3. **Clean commits:** Clear before committing to avoid diff noise
4. **Fresh start:** Reset document after major restructuring

**Implementation approach:**
1. Add `clear` subcommand to `cli.py`
2. Use regex or parser to strip computed values and errors
3. Same output options as `process` (timestamped, inplace, custom)

**Files to change:**
- `src/livemathtex/cli.py` - Add `clear` subcommand
- `src/livemathtex/core.py` - Add `clear_text()` function
- `.cursor/commands/livemathtex.md` - Document new command

**Effort:** Small-Medium (2-4 hours)

---

## Contributing

When adding new items:

**For issues (bugs):**
1. Use format: `ISSUE-XXX: Brief title`
2. Include: Status, Priority, Discovered date
3. Describe: Problem, What works/doesn't, Root cause, Impact
4. Propose: Solution options
5. List: Affected files and workarounds

**For features:**
1. Use format: `FEAT-XXX: Brief title`
2. Include: Status, Priority, Requested date
3. Describe: Request, Current state, Desired API
4. List: Use cases, Proposed changes, Files to change, Effort estimate

---

## Related

- **[ROADMAP.md](ROADMAP.md)** - Development phases and milestones
- **[README.md](../README.md)** - Project overview

---

*Last updated: 2026-01-11*
