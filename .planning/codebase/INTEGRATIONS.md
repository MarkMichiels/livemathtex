# External Integrations

**Analysis Date:** 2026-01-11

## APIs & External Services

**Not applicable** - LiveMathTeX is a standalone CLI tool with no external API calls.

## Data Storage

**Databases:**
- None - File-based processing only

**File Storage:**
- Local filesystem only
- Input: Markdown files (`.md`)
- Output: Processed Markdown files
- Debug: IR JSON files (`.lmt.json`)

**Caching:**
- None - Each run processes fresh

## Third-Party Libraries (Key Integrations)

**latex2sympy2 (Forked):**
- Purpose: LaTeX to SymPy expression parsing
- Integration: Git dependency from `https://github.com/MarkMichiels/latex2sympy.git`
- Why forked: DIFFERENTIAL bug fix not in upstream
- Usage: `src/livemathtex/engine/evaluator.py`

**SymPy:**
- Purpose: Symbolic mathematics engine
- Integration: Direct Python import
- Usage: Calculation evaluation, symbolic differentiation, expression manipulation
- Files: `src/livemathtex/engine/evaluator.py`

**Pint:**
- Purpose: Unit handling (parsing, validation, conversion)
- Integration: Direct Python import, singleton UnitRegistry
- Usage: Single source of truth for unit recognition
- Files: `src/livemathtex/engine/pint_backend.py`
- Custom units: Registered dynamically via `===` syntax

**Click:**
- Purpose: CLI framework
- Integration: Direct Python import
- Usage: Command definitions, argument parsing
- Files: `src/livemathtex/cli.py`

**Rich:**
- Purpose: Terminal output styling
- Integration: Direct Python import
- Usage: Colored output, progress indicators

**Watchdog:**
- Purpose: File system monitoring (watch mode)
- Integration: Direct Python import
- Usage: Auto-rebuild on file changes (planned)

## Authentication & Identity

**Not applicable** - No authentication required.

## Monitoring & Observability

**Error Tracking:**
- None - Errors displayed inline and collected in IR

**Logs:**
- stdout/stderr only via click.echo
- No log files or external logging services

## CI/CD & Deployment

**Hosting:**
- Not applicable - Local CLI tool
- Distributed as pip-installable package

**CI Pipeline:**
- Not configured (manual testing currently)

## Environment Configuration

**Development:**
- Required: Python 3.10+
- Virtual environment: `.venv/` (local)
- Dependencies: `pip install -e ".[dev]"`

**Production:**
- Same as development
- Install: `pip install -e .`
- CLI available as `livemathtex`

## Symlinks to Proviron

**Shared Tooling:**
- `tools/` → `/home/mark/Repositories/proviron/tools`
- `scripts/` → `/home/mark/Repositories/proviron/scripts`
- `.crossnote/` → `/home/mark/Repositories/proviron/.crossnote`

**Setup:**
```bash
./setup_symlinks.sh  # Creates symlinks to proviron
```

---

*Integration audit: 2026-01-11*
*Update when adding/removing external services*
