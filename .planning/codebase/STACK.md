# Technology Stack

**Analysis Date:** 2026-01-11

## Languages

**Primary:**
- Python 3.10+ - All application code

**Secondary:**
- Markdown - Documentation and test fixtures

## Runtime

**Environment:**
- Python 3.10, 3.11, 3.12 supported
- No browser runtime (CLI tool only)

**Package Manager:**
- pip with setuptools
- `pyproject.toml` for project configuration

## Frameworks

**Core:**
- None (vanilla Python CLI)

**Testing:**
- pytest >=7.0 - Unit and snapshot tests
- pytest-cov >=4.0 - Coverage reporting

**Build/Dev:**
- setuptools >=61.0 - Package building
- black >=23.0 - Code formatting
- ruff >=0.1.0 - Linting
- mypy >=1.0 - Type checking
- isort >=5.12 - Import sorting

## Key Dependencies

**Critical:**
- sympy >=1.12 - Core math engine, symbolic computation
- latex2sympy2 (forked) - LaTeX to SymPy parsing (`git+https://github.com/MarkMichiels/latex2sympy.git`)
- pint >=0.23 - Unit handling, registry, conversion (primary unit backend)
- numpy >=1.24 - Numeric operations

**CLI:**
- click >=8.1 - Command-line interface
- rich >=13.0 - Terminal output styling

**Infrastructure:**
- watchdog >=3.0 - Watch mode file monitoring
- tomli >=2.0 - TOML parsing (Python < 3.11)

## Configuration

**Environment:**
- No environment variables required
- Configuration via TOML files and document directives

**Build:**
- `pyproject.toml` - Project metadata, dependencies, tool configs

**Tool Configuration (in pyproject.toml):**
- `[tool.black]` - Line length 100
- `[tool.ruff]` - Linting rules
- `[tool.pytest.ini_options]` - Test paths, coverage
- `[tool.mypy]` - Type checking config

## Platform Requirements

**Development:**
- macOS/Linux/Windows (any platform with Python 3.10+)
- Symlinks to proviron for shared tooling (optional)

**Production:**
- Installed via `pip install -e .`
- CLI entry point: `livemathtex`

---

*Stack analysis: 2026-01-11*
*Update after major dependency changes*
