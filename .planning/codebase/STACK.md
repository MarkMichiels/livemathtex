# Technology Stack

**Analysis Date:** 2026-05-21

## Languages

**Primary:**
- Python 3.10+ - Full application, CLI, parsing, evaluation engine
- LaTeX - Math expression parsing and unit notation

**Secondary:**
- Markdown - Document format for input/output

## Runtime

**Environment:**
- Python 3.10, 3.11, 3.12 (see `requires-python = ">=3.10"` in `pyproject.toml`)

**Package Manager:**
- pip / setuptools
- Lockfile: `pyproject.toml` (setuptools-based, no poetry/pipenv)

## Frameworks

**Core:**
- setuptools 61.0+ - Build system and package management

**Parsing & Expression:**
- markdown-it-py 3.0.0+ - Markdown parsing
- mdit-py-plugins 0.4.0+ - Markdown extensions (dollarmath plugin for math blocks)
- pylatexenc 2.10+ - LaTeX parsing and character-level position tracking

**Units & Scientific:**
- pint 0.23+ - Unit registry, conversion, dimensional analysis
- numpy 1.24+ - Numeric operations

**CLI & Interface:**
- click 8.1+ - Command-line interface and argument parsing
- rich 13.0+ - Terminal output formatting and styling

**File Monitoring:**
- watchdog 3.0+ - File system event monitoring for watch mode

**Configuration:**
- tomli 2.0+ - TOML parsing (Python < 3.11 only; Python 3.11+ uses built-in tomllib)

**Testing:**
- pytest 7.0+ - Test runner
- pytest-cov 4.0+ - Code coverage reporting

**Development Tools:**
- black 23.0+ - Code formatter
- ruff 0.1.0+ - Linter and code quality checker
- mypy 1.0+ - Static type checker
- isort 5.12+ - Import sorting

**Documentation:**
- mkdocs 1.5+ - Documentation site generator
- mkdocs-material 9.0+ - Material theme for mkdocs

## Key Dependencies

**Critical:**
- pint - Unit handling is core to livemathtex; provides robust unit registry with 1000+ built-in units and custom unit support
- markdown-it-py + mdit-py-plugins - Robust markdown parsing with LaTeX math block support via dollarmath plugin
- pylatexenc - Enables character-level position tracking within LaTeX expressions for precise error reporting

**Infrastructure:**
- click - Powers CLI with process, inspect, clear, copy commands
- watchdog - Supports file monitoring for live reload (dependency present, may be used in future watch mode)
- numpy - Provides numerical operations for expression evaluation
- rich - Terminal styling for colored output and user feedback

## Configuration

**Environment:**
- Configuration loaded hierarchically (pyproject.toml → local .livemathtex.toml → document directives)
- No .env file requirements (configuration is document-centric)

**Build:**
- `pyproject.toml` - Single source of truth for all project configuration
  - `[build-system]` - setuptools with wheel support
  - `[tool.setuptools.packages.find]` - Package discovery from `src/` directory
  - `[tool.black]` - Black formatter: 100-char line length, targets Python 3.10-3.12
  - `[tool.ruff]` - Ruff linter: E, F, W, I, UP, B, C4 rule sets, 100-char line length
  - `[tool.pytest.ini_options]` - Pytest: tests in `tests/`, coverage for `livemathtex` package
  - `[tool.mypy]` - MyPy: Python 3.10 baseline, returns-any warnings enabled

## Platform Requirements

**Development:**
- Python 3.10+ (minimum version)
- Unix-like environment (Linux/macOS) for file system watchers
- 64-bit system recommended for numpy operations

**Production:**
- Python 3.10+ runtime
- Read/write access to file system (for processing markdown documents)
- ~50MB disk space (after installing dependencies)

---

*Stack analysis: 2026-05-21*
