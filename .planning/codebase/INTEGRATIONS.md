# External Integrations

**Analysis Date:** 2026-01-10

## APIs & External Services

**None:**
- No external APIs or services
- Standalone CLI tool with no network dependencies
- All processing is local

## Data Storage

**None:**
- No databases
- No file storage services
- File I/O: Local filesystem only (read input.md, write output.md)

**File Operations:**
- Input: Read markdown files from local filesystem
- Output: Write markdown files to local filesystem
- IR JSON: Optional debug output (`.lmt.json` files)

## Authentication & Identity

**None:**
- No authentication required
- No user accounts
- No identity providers
- CLI tool runs with user's local permissions

## Monitoring & Observability

**Error Tracking:**
- None (CLI tool, not a service)
- Errors collected in IR.errors list
- Displayed to console via Click.echo

**Analytics:**
- None

**Logging:**
- Console output only (stdout/stderr)
- Stats displayed after processing (symbols, definitions, evaluations, errors)
- No file logging, no remote logging

## CI/CD & Deployment

**Hosting:**
- Distributed as Python package via PyPI (future) or git
- Installed via `pip install -e .` (development) or `pip install livemathtex` (production)
- Runs on user's local Python installation

**CI Pipeline:**
- Not configured (no CI/CD setup documented)
- Tests run locally via pytest
- No automated deployment

## Environment Configuration

**Development:**
- Required: Python 3.10+
- No environment variables required
- Configuration via files (see Configuration section)

**Production:**
- Same as development (no environment differences)
- User installs via pip
- Configuration via same hierarchical system

## Webhooks & Callbacks

**None:**
- No webhooks
- No callbacks
- No external triggers

## External Libraries (Dependencies)

**Mathematical Libraries:**
- **SymPy 1.12+** - Symbolic mathematics engine
  - Purpose: Core calculation engine
  - Usage: Expression evaluation, symbolic math, unit conversions
  - Integration: Direct import, no API calls

- **latex2sympy2 (fork)** - LaTeX to SymPy parser
  - Purpose: Parse LaTeX expressions to SymPy
  - Source: `git+https://github.com/MarkMichiels/latex2sympy.git`
  - Integration: Direct import, function calls

- **Pint 0.23+** - Unit handling library
  - Purpose: Unit registry, validation, conversion
  - Usage: Primary unit backend (replaces SymPy units)
  - Integration: Direct import, UnitRegistry instance

- **NumPy 1.24+** - Numeric operations
  - Purpose: Numeric calculations
  - Usage: Used by SymPy/Pint internally
  - Integration: Indirect (via SymPy/Pint)

**CLI Libraries:**
- **Click 8.1+** - CLI framework
  - Purpose: Command-line argument parsing
  - Usage: Command definitions, help text, output formatting
  - Integration: Decorator-based command registration

- **Rich 13.0+** - Terminal formatting
  - Purpose: Colored output, tables (if used)
  - Usage: Terminal styling
  - Integration: Direct import (if used)

**File Watching:**
- **Watchdog 3.0+** - File system monitoring
  - Purpose: Watch mode (future feature)
  - Usage: Monitor input files for changes
  - Integration: Not yet implemented

**Configuration:**
- **tomli 2.0+** - TOML parsing (Python < 3.11)
  - Purpose: Parse TOML config files
  - Usage: Configuration loading
  - Integration: Conditional import (built-in tomllib for Python 3.11+)

## Editor Integration

**VS Code / Cursor:**
- VS Code tasks configured (bind to F9)
- Cursor command wrappers:
  - `/livemathtex` - Process current file
  - `/livemathtex-setup` - Setup instructions
- Location: `.cursor/commands/` directory
- Documentation: `docs/EDITOR_INTEGRATION.md`

## External Tools (User's Responsibility)

**PDF Export:**
- Pandoc (not included, user installs)
- Usage: `pandoc output.md -o output.pdf`
- Out of scope for livemathtex

**Markdown Preview:**
- User's markdown previewer (VS Code, Cursor, etc.)
- Out of scope for livemathtex

**Plotting:**
- Matplotlib, etc. (not included)
- Out of scope for livemathtex

---

*Integration audit: 2026-01-10*
*Update when adding/removing external services*

