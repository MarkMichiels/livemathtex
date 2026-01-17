# Technology Stack

**Analysis Date:** 2026-01-17

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
- pytest >=8.0 - Unit and snapshot tests
- pytest-cov >=6.0 - Coverage reporting

**Build/Dev:**
- setuptools >=61.0 - Package building
- black >=24.0 - Code formatting
- ruff >=0.8.0 - Linting and import sorting
- mypy >=1.10 - Type checking

## Key Dependencies

**Critical:**
- pint >=0.24 - Unit handling, registry, conversion (sole math backend since v3.0)

**CLI:**
- click >=8.1 - Command-line interface

**Parsing:**
- markdown-it-py >=3.0.0 - Markdown parsing
- mdit-py-plugins >=0.4.0 - Math plugin for markdown-it-py
- pylatexenc >=2.10 - LaTeX encoding/decoding

**Infrastructure:**
- tomli >=2.0 - TOML parsing (Python < 3.11 only)

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

## Removed Dependencies (v3.0+)

The following dependencies were removed to reduce bloat:

| Package | Removed In | Reason |
|---------|------------|--------|
| sympy | v3.0 | Replaced by custom expression parser + Pint |
| latex2sympy2 | v3.0 | Replaced by custom LaTeX tokenizer/parser |
| numpy | v4.2 | Never used; Pint works without it |
| rich | v4.2 | Never used; click.echo/style suffices |
| watchdog | v4.2 | Watch mode not implemented; add back when needed |
| isort | v4.2 | ruff handles import sorting via "I" rules |

---

*Stack analysis: 2026-01-17*
*Update after major dependency changes*
