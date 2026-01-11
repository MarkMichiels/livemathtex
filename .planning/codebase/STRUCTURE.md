# Codebase Structure

**Analysis Date:** 2026-01-10

## Directory Layout

```
livemathtex/
├── src/
│   └── livemathtex/          # Main package
│       ├── __init__.py
│       ├── cli.py            # CLI entry point
│       ├── core.py            # Pipeline orchestration
│       ├── config.py          # Configuration management
│       ├── parser/            # Markdown/LaTeX parsing
│       │   ├── __init__.py
│       │   ├── lexer.py       # Tokenization and detection
│       │   └── models.py       # AST node types
│       ├── ir/                # Intermediate Representation
│       │   ├── __init__.py
│       │   ├── builder.py     # Build IR from AST
│       │   └── schema.py      # IR dataclasses (v2.0, v3.0)
│       ├── engine/            # Calculation engine
│       │   ├── __init__.py
│       │   ├── evaluator.py   # Main evaluation logic
│       │   ├── pint_backend.py # Pint unit registry
│       │   └── symbols.py     # Symbol table
│       ├── render/            # Output generation
│       │   ├── __init__.py
│       │   └── markdown.py    # Markdown renderer
│       └── utils/             # Utilities
│           ├── __init__.py
│           └── errors.py      # Error types
├── tests/                     # Test files
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_examples.py      # Snapshot tests for examples
│   ├── test_pint_backend.py  # Pint unit tests
│   └── test_unit_recognition.py # Unit recognition tests
├── examples/                  # Example markdown files
│   ├── simple/               # Basic examples
│   ├── simple-units/          # Unit examples
│   ├── engineering/           # Engineering calculations
│   ├── engineering-units/     # Engineering with units
│   ├── custom-units/          # Custom unit definitions
│   ├── unit-library/          # Unit library examples
│   └── settings/              # Configuration examples
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # Technical design
│   ├── USAGE.md               # Syntax reference
│   ├── SETUP.md               # Installation
│   ├── BACKGROUND.md          # Research and alternatives
│   ├── BACKLOG.md             # Issues and features
│   ├── ROADMAP.md             # Development phases
│   └── DEPENDENCIES.md        # Dependency details
├── utils/                     # Utility scripts
│   └── regenerate_json_v3.py # IR v3.0 regeneration
├── libs/                      # Library files (future)
│   └── README.md
├── pyproject.toml             # Project config
├── LICENSE                    # MIT License
└── README.md                  # User documentation
```

## Directory Purposes

**src/livemathtex/:**
- Purpose: Main package containing all source code
- Contains: Python modules organized by layer (parser, engine, render, etc.)
- Key files: `cli.py` (entry point), `core.py` (pipeline), `config.py` (config)
- Subdirectories: Organized by responsibility (parser/, engine/, ir/, render/)

**src/livemathtex/parser/:**
- Purpose: Markdown and LaTeX parsing
- Contains: Lexer for tokenization, models for AST nodes
- Key files: `lexer.py` (main parser), `models.py` (Document, MathBlock, Calculation)

**src/livemathtex/ir/:**
- Purpose: Intermediate Representation for symbols and debugging
- Contains: IR Builder, IR Schema definitions (v2.0 and v3.0)
- Key files: `builder.py` (IR construction), `schema.py` (dataclasses)

**src/livemathtex/engine/:**
- Purpose: Calculation execution and symbol management
- Contains: Evaluator, SymbolTable, Pint backend
- Key files: `evaluator.py` (main engine), `pint_backend.py` (unit handling), `symbols.py` (symbol table)

**src/livemathtex/render/:**
- Purpose: Output generation
- Contains: Markdown renderer (only output format)
- Key files: `markdown.py` (renderer implementation)

**tests/:**
- Purpose: Test files
- Contains: Unit tests, integration tests, snapshot tests
- Key files: `test_examples.py` (snapshot tests), `conftest.py` (fixtures)

**examples/:**
- Purpose: Example markdown files demonstrating features
- Contains: Input/output pairs for each example
- Key files: Each subdirectory has `input.md` and `output.md` (and optionally `input.lmt.json`)

**docs/:**
- Purpose: Technical documentation
- Contains: Architecture, usage, setup guides
- Key files: `ARCHITECTURE.md` (technical design), `USAGE.md` (syntax reference)

## Key File Locations

**Entry Points:**
- `src/livemathtex/cli.py:main()` - CLI entry point (via `livemathtex` command)
- `src/livemathtex/core.py:process_file()` - Main processing pipeline

**Configuration:**
- `pyproject.toml` - Project metadata, dependencies, build config
- `src/livemathtex/config.py` - Configuration dataclass and loading logic
- `.livemathtex.toml` - Per-document configuration (optional, in document directory)

**Core Logic:**
- `src/livemathtex/core.py` - Pipeline orchestration
- `src/livemathtex/engine/evaluator.py` - Calculation engine
- `src/livemathtex/parser/lexer.py` - Markdown/LaTeX parser
- `src/livemathtex/ir/builder.py` - IR construction

**Testing:**
- `tests/test_examples.py` - Snapshot tests for examples
- `tests/conftest.py` - Pytest fixtures (project_root, examples_dir)
- `tests/test_pint_backend.py` - Pint unit tests

**Documentation:**
- `README.md` - User-facing documentation
- `docs/ARCHITECTURE.md` - Technical architecture
- `docs/USAGE.md` - Syntax reference

## Naming Conventions

**Files:**
- `snake_case.py` for all Python modules
- `test_*.py` for test files
- `*.md` for documentation (lowercase, descriptive names)

**Directories:**
- `snake_case` for all directories
- Singular names for modules (parser/, engine/, render/)
- Plural for collections (examples/, tests/)

**Special Patterns:**
- `__init__.py` for package initialization
- `conftest.py` for pytest configuration
- `input.md` / `output.md` for example files

## Where to Add New Code

**New Feature:**
- Primary code: `src/livemathtex/` (appropriate subdirectory)
- Tests: `tests/test_*.py` (alongside or in tests/)
- Config if needed: `src/livemathtex/config.py` (add to LivemathConfig)

**New Parser Feature:**
- Implementation: `src/livemathtex/parser/lexer.py` or `models.py`
- Tests: `tests/test_parser.py` (create if doesn't exist)

**New Engine Feature:**
- Implementation: `src/livemathtex/engine/evaluator.py` or new module
- Tests: `tests/test_engine.py` or `tests/test_evaluator.py`

**New Example:**
- Implementation: `examples/{name}/input.md` and `output.md`
- Tests: Automatically tested via `test_examples.py` (parametrized)

**Utilities:**
- Shared helpers: `src/livemathtex/utils/`
- Type definitions: In module where used (or `utils/` if shared)

## Special Directories

**examples/:**
- Purpose: Example markdown files for testing and documentation
- Source: Manually created, maintained alongside code
- Committed: Yes (part of test suite)

**libs/:**
- Purpose: Library files for import system (future feature)
- Source: User-created markdown files with IR JSON exports
- Committed: No (user content, not in repo)

**src/livemathtex.egg-info/:**
- Purpose: Package metadata (generated by setuptools)
- Source: Auto-generated by `pip install -e .`
- Committed: No (in .gitignore)

---

*Structure analysis: 2026-01-10*
*Update when directory structure changes*

