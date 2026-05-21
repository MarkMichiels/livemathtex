# External Integrations

**Analysis Date:** 2026-05-21

## APIs & External Services

**None detected** - LiveMathTeX is a self-contained markdown processing tool with no external API integrations.

## Data Storage

**Databases:**
- None - LiveMathTeX operates on local markdown files only
- No persistent storage or database requirements

**File Storage:**
- Local filesystem only
  - Input: Markdown files (`.md`) with embedded LaTeX math blocks
  - Output: Processed markdown files with computed values inserted
  - IR output: JSON files (`.lmt.json`) for debugging (optional)
  - Location: Same directory as input file (configurable via `-o` flag or document directive)

**Caching:**
- None - Pint unit registry is cached in-memory during session
- Reset available via `reset_unit_registry()` for testing

## Authentication & Identity

**Auth Provider:**
- None required - LiveMathTeX operates locally without authentication
- No user/token management

## Monitoring & Observability

**Error Tracking:**
- None configured - Errors logged to stderr and reported in CLI output
- Optional debug IR file (`.lmt.json`) for manual inspection

**Logs:**
- Console output via `click` and `rich` libraries
- Metadata footer added to processed markdown showing:
  - Last run timestamp
  - Statistics (symbol count, custom units, definitions, evaluations, symbolic operations)
  - Error count
  - Processing duration

## CI/CD & Deployment

**Hosting:**
- None - Standalone CLI tool, not a service
- Distributed as Python package via pip

**CI Pipeline:**
- None detected - Repository has no GitHub Actions, Travis CI, or other CI/CD configuration
- Manual testing via pytest

## LaTeX/PDF Tools

**LaTeX Processing:**
- **No direct LaTeX compilation** - LiveMathTeX does NOT invoke pdflatex, xelatex, or other LaTeX engines
- LaTeX expressions are **parsed only** (not compiled to PDF) via pylatexenc
- Output is markdown with computed values; LaTeX rendering is user's responsibility

**LaTeX Parsing:**
- pylatexenc 2.10+ - Parses LaTeX notation for:
  - Unit expressions: `\text{kg}`, `\frac{m}{s}`, `^2` exponents
  - Math mode detection in markdown (`$...$` and `$$...$$` blocks)
  - Character-level position tracking for error reporting
  - LaTeX wrapper unwrapping: `\text{...}`, `\mathrm{...}` → plain text

**Unit Notation Handling:**
- Converts LaTeX unit syntax to Pint-compatible strings:
  - `\text{m/s}` → `m/s`
  - `^2` → `**2` (exponent conversion)
  - `\cdot` → `*` (multiplication)
  - `\frac{num}{denom}` → `num/denom`
  - Currency symbols: `€` ↔ EUR, `$` ↔ USD

## Markdown Processing

**Markdown Parsing:**
- markdown-it-py 3.0.0+ - Standard CommonMark parser
  - Document structure, heading hierarchy, code fences
- mdit-py-plugins 0.4.0+ - Custom plugin: `dollarmath_plugin`
  - Detects math block delimiters (`$...$` inline, `$$...$$` display)
  - Boundary detection for expression extraction

## File System Monitoring

**Watchdog Integration:**
- watchdog 3.0+ - Present as dependency but **watch mode NOT yet implemented**
- Intended for future live-reload functionality
- Currently available in `pyproject.toml` but no active CLI command

## Environment Configuration

**Required env vars:**
- None - LiveMathTeX requires no environment variables

**Secrets location:**
- None - No credentials or secrets management

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Unit System Backend

**Pint Unit Registry:**
- Location: `src/livemathtex/engine/pint_backend.py`
- Single global unit registry (singleton pattern)
- **Built-in units:** 1000+ standard SI, imperial, CGS, chemistry units
- **Custom units:** User-defined via `===` syntax (e.g., `€ === €`, `kWh === kW * h`)
- **Custom unit definitions:**
  - Currency: EUR, USD (tracked in CustomUnitRegistry)
  - Dutch language: dag (day), uur (hour), jaar (year)
  - User-defined: Dynamic registration via `===` blocks in markdown

**Unit Conversion:**
- Full dimensional analysis via Pint
- SI base unit conversion for IR output
- Compound unit handling: `m³/h`, `mg/L/day`, `kg·m/s²`
- Case-sensitive parsing (lowercase `m` = meter, uppercase `M` = mega)

## Custom Unit Definition Flow

**Input syntax (Markdown):**
```markdown
$$ € === € $$        # Base currency unit
$$ kWh === kW · h $$ # Compound energy unit
$$ dag === day $$    # Alias
```

**Processing:**
1. Lexer detects `===` syntax in markdown
2. Parser extracts unit name and definition
3. CustomUnitRegistry tracks definition metadata
4. Pint backend registers in global UnitRegistry
5. All subsequent calculations use registered unit

**Storage (IR v3.0):**
- custom_units dictionary in JSON with:
  - `name` - unit identifier
  - `type` - "base" or "derived"
  - `pint_definition` - Pint-compatible definition string

## Expression Evaluation

**Expression Parser:**
- Location: `src/livemathtex/parser/expression_parser.py`
- Tokenizes LaTeX/markdown math expressions
- Supports: variables, functions, operators, parentheses, unit expressions

**Evaluation Engine:**
- Location: `src/livemathtex/engine/expression_evaluator.py`
- Safe evaluation (no arbitrary code execution)
- Namespace-based symbol resolution
- Pint quantity arithmetic with dimensional tracking

## Intermediate Representation

**IR v3.0:**
- Location: `src/livemathtex/ir/schema.py`
- JSON serialization format for debugging and analysis
- Contains:
  - Symbol table with original and base unit values
  - Custom unit definitions
  - Calculation statistics and metadata

**Inspection CLI:**
```bash
livemathtex inspect file.lmt.json  # View IR contents
```

---

*Integration audit: 2026-05-21*
