# Technology Stack

**Analysis Date:** 2026-01-10

## Languages

**Primary:**
- Python 3.10+ - All application code (CLI tool, core engine, parser, evaluator)

**Secondary:**
- Markdown - Documentation and examples
- TOML - Configuration files (pyproject.toml, .livemathtex.toml)

## Runtime

**Environment:**
- Python 3.10, 3.11, or 3.12 (requires-python: ">=3.10")
- No browser runtime (CLI tool only)
- No server runtime (standalone executable)

**Package Manager:**
- pip (Python package manager)
- pyproject.toml for project metadata and dependencies
- No lockfile (pip freeze for reproducible installs)

## Frameworks

**Core:**
- None (vanilla Python with standard library + dependencies)

**Testing:**
- pytest 7.0+ - Unit and integration tests
- pytest-cov 4.0+ - Coverage reporting

**Build/Dev:**
- setuptools 61.0+ - Package building and distribution
- black 23.0+ - Code formatting
- ruff 0.1.0+ - Linting
- mypy 1.0+ - Type checking
- isort 5.12+ - Import sorting

## Key Dependencies

**Critical:**
- sympy 1.12+ - Symbolic mathematics engine (core calculation engine)
- latex2sympy2 (fork) - LaTeX to SymPy parser (from git+https://github.com/MarkMichiels/latex2sympy.git)
- pint 0.23+ - Unit handling and conversion (primary unit backend)
- numpy 1.24+ - Numeric operations

**Infrastructure:**
- click 8.1+ - CLI argument parsing and command structure
- rich 13.0+ - Terminal output styling and formatting
- watchdog 3.0+ - File watching for watch mode (future feature)
- tomli 2.0+ - TOML parsing (for Python < 3.11, built-in tomllib for 3.11+)

## Configuration

**Environment:**
- No environment variables required for basic operation
- Configuration via hierarchical system:
  1. CLI -o flag (output path only)
  2. Document directives (`<!-- livemathtex: ... -->`)
  3. Local config (`.livemathtex.toml` in document directory)
  4. Project config (`pyproject.toml [tool.livemathtex]`)
  5. User config (`~/.config/livemathtex/config.toml`)
  6. Defaults (hardcoded in `config.py`)

**Build:**
- `pyproject.toml` - Project metadata, dependencies, build config
- `setup.py` - Not used (setuptools.build_meta backend)
- `.livemathtex.toml` - Per-document configuration (optional)

## Platform Requirements

**Development:**
- macOS/Linux/Windows (any platform with Python 3.10+)
- No external dependencies beyond Python packages
- Optional: VS Code or Cursor for editor integration

**Production:**
- Distributed as Python package via pip
- Installed via `pip install -e .` (development) or `pip install livemathtex` (production)
- CLI command: `livemathtex` (via entry point in pyproject.toml)
- Runs on user's Python installation

---

*Stack analysis: 2026-01-10*
*Update after major dependency changes*

