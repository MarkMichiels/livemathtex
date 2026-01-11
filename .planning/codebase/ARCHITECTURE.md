# Architecture

**Analysis Date:** 2026-01-11

## Pattern Overview

**Overall:** CLI Application with Modular Pipeline

**Key Characteristics:**
- Single executable with subcommands (`process`, `inspect`)
- Pipeline architecture: Parse → IR → Evaluate → Render
- Intermediate Representation (IR) for debugging and symbol tracking
- File-based state (no database)

## Layers

**CLI Layer:**
- Purpose: Parse user input and route to pipeline
- Contains: Command definitions, argument parsing
- Location: `src/livemathtex/cli.py`
- Depends on: Core pipeline
- Used by: Shell invocation (`livemathtex`)

**Core Layer:**
- Purpose: Orchestrate the processing pipeline
- Contains: `process_file()`, `process_text()`, `process_text_v3()`
- Location: `src/livemathtex/core.py`
- Depends on: Parser, Engine, IR, Renderer
- Used by: CLI commands

**Parser Layer:**
- Purpose: Tokenize Markdown and extract calculations
- Contains: Lexer, AST models (Document, MathBlock)
- Location: `src/livemathtex/parser/`
- Depends on: None
- Used by: Core pipeline

**IR Layer:**
- Purpose: Intermediate Representation for symbols and debugging
- Contains: Schema classes (LivemathIR, SymbolEntry), IR builder
- Location: `src/livemathtex/ir/`
- Depends on: Parser models
- Used by: Core pipeline, Engine

**Engine Layer:**
- Purpose: Evaluate calculations, manage symbols, handle units
- Contains: Evaluator, SymbolTable, Pint backend
- Location: `src/livemathtex/engine/`
- Depends on: SymPy, Pint, latex2sympy2
- Used by: Core pipeline

**Render Layer:**
- Purpose: Generate output Markdown with results
- Contains: MarkdownRenderer
- Location: `src/livemathtex/render/`
- Depends on: Parser models
- Used by: Core pipeline

## Data Flow

**CLI Command Execution:**

1. User runs: `livemathtex process input.md`
2. CLI parses args and flags (`src/livemathtex/cli.py`)
3. `process_file()` invoked (`src/livemathtex/core.py`)
4. Lexer parses Markdown, extracts calculations (`src/livemathtex/parser/lexer.py`)
5. IRBuilder creates IR from parsed AST (`src/livemathtex/ir/builder.py`)
6. Evaluator processes each calculation (`src/livemathtex/engine/evaluator.py`)
7. IR populated with symbol values
8. MarkdownRenderer generates output (`src/livemathtex/render/markdown.py`)
9. Output written to file
10. Optional: IR JSON written (`--verbose`)

**State Management:**
- File-based: All state lives in processed output and `.lmt.json` IR files
- Symbol table is per-processing-run (no persistent state)
- Each run is independent

## Key Abstractions

**Calculation:**
- Purpose: Single LaTeX calculation to evaluate
- Location: `src/livemathtex/parser/models.py`
- Pattern: Data class with operation type (`:=`, `==`, `=>`)

**SymbolEntry:**
- Purpose: Track variable with original and converted values
- Location: `src/livemathtex/ir/schema.py`
- Pattern: Data class for IR serialization

**Evaluator:**
- Purpose: Execute calculations and manage symbol table
- Location: `src/livemathtex/engine/evaluator.py`
- Pattern: Stateful processor (holds symbol table)

**PintBackend:**
- Purpose: Unit validation, conversion, and SymPy compatibility
- Location: `src/livemathtex/engine/pint_backend.py`
- Pattern: Module with unit registry singleton

## Entry Points

**CLI Entry:**
- Location: `src/livemathtex/cli.py` → `main()`
- Triggers: User runs `livemathtex <command>`
- Responsibilities: Register commands, parse args, invoke pipeline

**Commands:**
- `process`: Process a markdown file with calculations
- `inspect`: View contents of an IR JSON file

## Error Handling

**Strategy:** Catch exceptions per-calculation, continue processing, collect errors in IR

**Patterns:**
- Calculations wrapped in try/catch
- Errors displayed inline with `\color{red}`
- Error list tracked in IR for inspection
- CLI exits with code 1 on fatal errors

## Cross-Cutting Concerns

**Logging:**
- click.echo for CLI output
- Rich for styled terminal output

**Configuration:**
- Hierarchical: CLI → Document directives → Local TOML → Project TOML → User TOML → Defaults
- `src/livemathtex/config.py` handles loading and merging

**Unit Handling:**
- Pint is single source of truth for unit recognition
- No hardcoded unit lists
- Custom units defined via `===` syntax in documents

---

*Architecture analysis: 2026-01-11*
*Update when major patterns change*
