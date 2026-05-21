# Codebase Structure

**Analysis Date:** 2026-05-21

## Directory Layout

```
livemathtex/
├── .planning/               # GSD planning (not part of package)
├── docs/                    # Markdown documentation
├── examples/                # Example documents
│   ├── arrays/
│   ├── cross-references/
│   ├── custom-units/
│   ├── engineering/
│   ├── functions/
│   ├── simple/
│   └── smart-formatting/
├── tests/                   # Test suite (pytest)
├── src/livemathtex/         # Main package source
│   ├── __init__.py          # Public API exports
│   ├── cli.py               # Click CLI implementation
│   ├── config.py            # Configuration system
│   ├── core.py              # Main processing pipelines
│   ├── engine/              # Calculation engine
│   │   ├── __init__.py
│   │   ├── evaluator.py     # Main evaluator orchestrator
│   │   ├── expression_evaluator.py  # AST evaluation with Pint
│   │   ├── pint_backend.py  # Pint wrapper and unit handling
│   │   └── symbols.py       # Symbol table and name normalization
│   ├── ir/                  # Intermediate representation
│   │   ├── __init__.py
│   │   ├── builder.py       # AST → IR conversion
│   │   └── schema.py        # V2.0 and V3.0 IR schemas
│   ├── parser/              # Parsing layer
│   │   ├── __init__.py
│   │   ├── calculation_parser.py  # Math block span identification
│   │   ├── expression_parser.py   # Expression AST parsing
│   │   ├── expression_tokenizer.py # LaTeX tokenization
│   │   ├── lexer.py         # Document tokenizer
│   │   ├── markdown_parser.py     # Hybrid markdown/LaTeX parser
│   │   ├── models.py        # AST node definitions
│   │   └── reference_parser.py    # Cross-reference detection
│   ├── render/              # Output rendering
│   │   ├── __init__.py
│   │   └── markdown.py      # Markdown reconstruction
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── errors.py        # Custom exception classes
├── pyproject.toml           # Project config, dependencies, metadata
├── README.md                # Project overview
├── LICENSE                  # MIT license
└── CHANGELOG.md             # Version history
```

## Directory Purposes

**src/livemathtex/** (Main Package):
- Purpose: Core livemathtex library code
- Contains: All source files for processing pipelines
- Key files: `core.py` (orchestration), `cli.py` (user interface)

**src/livemathtex/parser/**:
- Purpose: Parse markdown and LaTeX syntax
- Contains: Lexer, tokenizers, expression parsers, AST models
- Key files: `lexer.py`, `expression_parser.py`, `models.py`

**src/livemathtex/engine/**:
- Purpose: Execute calculations using Pint
- Contains: Evaluator, symbol management, unit handling
- Key files: `evaluator.py`, `pint_backend.py`, `symbols.py`

**src/livemathtex/ir/**:
- Purpose: Define and build intermediate representation
- Contains: V2.0 and V3.0 schemas, IR construction
- Key files: `schema.py`, `builder.py`

**src/livemathtex/render/**:
- Purpose: Reconstruct markdown with calculated results
- Contains: Markdown renderer, metadata injection
- Key files: `markdown.py`

**src/livemathtex/utils/**:
- Purpose: Shared utilities and exceptions
- Contains: Error classes, helpers
- Key files: `errors.py`

**tests/**:
- Purpose: Test suite
- Contains: Unit tests, integration tests, fixtures
- Pattern: One test file per module (e.g., `test_lexer.py`, `test_evaluator.py`)

**examples/**:
- Purpose: Example documents demonstrating features
- Contains: Markdown files with calculations
- Subdirs: Each feature category (arrays, custom-units, functions, etc.)

**docs/**:
- Purpose: Documentation (external)
- Contains: Markdown docs for users

## Key File Locations

**Entry Points:**
- `src/livemathtex/cli.py` — Click CLI application entry (main function)
- `src/livemathtex/__init__.py` — Public API exports (process_text, process_file, etc.)

**Configuration:**
- `src/livemathtex/config.py` — LivemathConfig class, TOML loading
- `pyproject.toml` — Project metadata, dependencies, build config

**Core Logic:**
- `src/livemathtex/core.py` — process_text(), process_text_v3(), process_file()
- `src/livemathtex/engine/evaluator.py` — Main evaluator
- `src/livemathtex/parser/lexer.py` — Document tokenizer

**Intermediate Representation:**
- `src/livemathtex/ir/schema.py` — SymbolEntry, LivemathIR, LivemathIRV3 classes
- `src/livemathtex/ir/builder.py` — IRBuilder (Document → IR)

**Expression Evaluation:**
- `src/livemathtex/engine/expression_evaluator.py` — evaluate_expression_tree()
- `src/livemathtex/engine/pint_backend.py` — Pint unit handling
- `src/livemathtex/parser/expression_parser.py` — Expression AST parsing

**Testing:**
- `tests/conftest.py` — Pytest fixtures and configuration
- `tests/test_*.py` — Test files (alphabetical by module)

## Naming Conventions

**Files:**
- Module files: `snake_case.py` (e.g., `expression_tokenizer.py`)
- Test files: `test_*.py` (e.g., `test_evaluator.py`)

**Directories:**
- Package dirs: `snake_case` (e.g., `src/livemathtex/parser/`)
- Functional groups: By layer (parser, engine, ir, render, utils)

**Classes:**
- Main classes: PascalCase (e.g., `Evaluator`, `SymbolTable`, `ExpressionParser`)
- Dataclasses: PascalCase (e.g., `MathBlock`, `Calculation`, `SymbolEntry`)
- Enums: PascalCase (e.g., `UnitFormat`)

**Functions:**
- Public functions: `snake_case` (e.g., `process_text()`, `evaluate_expression_tree()`)
- Internal/helper: `_snake_case` (e.g., `_escape_latex_text()`)

**Variables:**
- Local/instance: `snake_case` (e.g., `result_latex`, `symbol_table`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `GREEK_LETTERS`, `OPERATOR_RE`)

## Where to Add New Code

**New Feature (Calculation Type):**
- Primary code: `src/livemathtex/parser/lexer.py` (add new operation), `src/livemathtex/engine/evaluator.py` (handle operation)
- Tests: `tests/test_lexer.py`, `tests/test_evaluator.py`

**New Parsing Component:**
- Implementation: `src/livemathtex/parser/` (new file if significant)
- Model definition: `src/livemathtex/parser/models.py` (add new Node subclass)
- Tests: `tests/test_<component>.py`

**New Engine Operation:**
- Main code: `src/livemathtex/engine/evaluator.py`
- Supporting: `src/livemathtex/engine/expression_evaluator.py` (if expression-related)
- Tests: `tests/test_evaluator.py`

**Unit Handling / Pint Integration:**
- Code: `src/livemathtex/engine/pint_backend.py`
- Tests: `tests/test_pint_backend.py`, `tests/test_unit_conversion.py`

**New Utilities:**
- Shared helpers: `src/livemathtex/utils/` (new file if major feature)
- Error types: `src/livemathtex/utils/errors.py`

**CLI Command:**
- Implementation: `src/livemathtex/cli.py` (add @main.command())
- Supporting: Add function to core.py if reusable

**Configuration Option:**
- Define: Add field to LivemathConfig dataclass in `src/livemathtex/config.py`
- Loading: Update config._load_toml() if file-based
- Usage: Pass through process_text() to evaluator

## Special Directories

**tests/**:
- Purpose: Pytest test suite
- Generated: No (committed to git)
- Committed: Yes
- Structure: One test file per major module, conftest.py for shared fixtures
- Patterns: Test functions named `test_<feature>()`, fixtures use @pytest.fixture

**examples/**:
- Purpose: Example markdown documents for users
- Generated: No (hand-written examples)
- Committed: Yes
- Structure: One subdirectory per feature/use case
- Files: `.md` input files, `output.md` processed versions

**.planning/codebase/**:
- Purpose: GSD mapping documents (ARCHITECTURE.md, STRUCTURE.md, etc.)
- Generated: Yes (by /gsd:map-codebase)
- Committed: Yes
- Files: *.md analysis documents

**docs/**:
- Purpose: External documentation
- Generated: No (hand-written)
- Committed: Yes
- Format: Markdown with mkdocs configuration

**.git/** / **.venv/**:
- Purpose: Git history, Python virtual environment
- Committed: .git yes, .venv no (in .gitignore)

## Cross-Module Imports

**Direction: Layered (Dependencies point inward)**

```
CLI (cli.py)
  ↓
Core (core.py) ← Uses →  Config, Parser, IR, Engine, Render
  ↓
Parser → Models
IR → Builder → Schema
Engine → Evaluator → ExpressionEvaluator → PintBackend
  ↓
Parser ← ExpressionTokenizer ← ExpressionParser
```

**Import Organization:**
- Parser modules import from `parser.models` for AST types
- Engine modules import from `ir.schema` for symbol storage
- Core imports all layers: parser, ir, engine, render, config
- CLI imports only core + config + parser (minimal)

---

*Structure analysis: 2026-05-21*
