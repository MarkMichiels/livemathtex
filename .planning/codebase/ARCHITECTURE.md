# Architecture

**Analysis Date:** 2026-01-10

## Pattern Overview

**Overall:** Pipeline-based CLI Application with Intermediate Representation (IR)

**Key Characteristics:**
- Single executable with subcommands (`process`, `inspect`)
- Stateless processing (each file processed independently)
- Pipeline architecture: Parse → Build IR → Evaluate → Render → Write
- IR v3.0 as central state throughout processing
- Symbol normalization for LaTeX parsing compatibility

## Layers

**CLI Layer:**
- Purpose: Parse user input and route to appropriate handler
- Contains: Command definitions (`cli.py`), argument parsing (Click), help text
- Location: `src/livemathtex/cli.py`
- Depends on: Core processing layer
- Used by: Entry point (`livemathtex` command)

**Core Processing Layer:**
- Purpose: Orchestrate the processing pipeline
- Contains: `process_file()`, `process_text()`, `process_text_v3()` functions
- Location: `src/livemathtex/core.py`
- Depends on: Parser, IR Builder, Evaluator, Renderer
- Used by: CLI layer

**Parser Layer:**
- Purpose: Analyze Markdown files and recognize formulas, variables, units
- Contains: Lexer for tokenization, MathBlock detection, calculation extraction
- Location: `src/livemathtex/parser/` (lexer.py, models.py)
- Depends on: Regex patterns, Markdown structure
- Used by: Core processing layer

**IR Layer:**
- Purpose: Intermediate Representation for symbol management and debugging
- Contains: IR Builder, IR Schema (v2.0 and v3.0), symbol normalization
- Location: `src/livemathtex/ir/` (builder.py, schema.py)
- Depends on: Parser output
- Used by: Evaluator, Renderer, Debug output

**Engine Layer:**
- Purpose: Execute calculations, manage symbols, handle units
- Contains: Evaluator, SymbolTable, Pint backend for units
- Location: `src/livemathtex/engine/` (evaluator.py, symbols.py, pint_backend.py)
- Depends on: SymPy, Pint, latex2sympy2
- Used by: Core processing layer

**Renderer Layer:**
- Purpose: Transform calculated results to output format
- Contains: Markdown renderer (only output format)
- Location: `src/livemathtex/render/` (markdown.py)
- Depends on: IR, evaluation results
- Used by: Core processing layer

**Config Layer:**
- Purpose: Hierarchical configuration management
- Contains: LivemathConfig dataclass, config loading from files
- Location: `src/livemathtex/config.py`
- Depends on: TOML parsing (tomllib/tomli)
- Used by: All layers (via config parameter)

## Data Flow

**CLI Command Execution:**

1. User runs: `livemathtex process input.md`
2. Click parses args and flags
3. CLI handler (`cli.py:process()`) invoked
4. Config loaded hierarchically (files → directives → CLI overrides)
5. Core processing (`core.py:process_file()`) called
6. Pipeline executes:
   - Lexer parses Markdown → Document AST
   - IR Builder extracts custom units, builds IR
   - Evaluator processes calculations, updates symbol table
   - IR populated with symbol values
   - Renderer generates output Markdown
7. Output written to file (timestamped, inplace, or specified path)
8. IR JSON optionally written (if `--verbose` or `json=true`)
9. Stats displayed to console
10. Process exits

**State Management:**
- Stateless: Each file processed independently
- Symbol table: In-memory during processing, persisted to IR JSON
- No persistent state between runs
- Unit registry: Global Pint registry (reset between tests)

## Key Abstractions

**IR (Intermediate Representation):**
- Purpose: Central state for symbols, custom units, errors, stats
- Examples: `LivemathIR` (v2.0), `LivemathIRV3` (v3.0)
- Pattern: Dataclass with symbols dict, custom_units dict, errors list

**SymbolTable:**
- Purpose: Manage variable/function definitions and values
- Examples: `SymbolTable` in `engine/symbols.py`
- Pattern: Dictionary with internal ID mapping (v_{n}, f_{n}) to SymbolValue

**Evaluator:**
- Purpose: Execute calculations using SymPy
- Examples: `Evaluator` class in `engine/evaluator.py`
- Pattern: Stateful class with symbol table, config, evaluation methods

**Config:**
- Purpose: Immutable configuration with hierarchical overrides
- Examples: `LivemathConfig` dataclass in `config.py`
- Pattern: Frozen dataclass with `with_overrides()` method

**Lexer:**
- Purpose: Parse Markdown and extract calculations
- Examples: `Lexer` class in `parser/lexer.py`
- Pattern: Stateless parser with regex-based detection

## Entry Points

**CLI Entry:**
- Location: `src/livemathtex/cli.py:main()`
- Triggers: User runs `livemathtex <command>`
- Responsibilities: Register commands, parse args, route to handlers

**Commands:**
- Location: `src/livemathtex/cli.py` (decorated with `@main.command()`)
- Triggers: Matched command from CLI
- Responsibilities: Validate input, call core processing, format output

**API Entry (for testing):**
- Location: `src/livemathtex/core.py:process_text()`, `process_text_v3()`
- Triggers: Direct function call (used by tests)
- Responsibilities: Process markdown string, return rendered output and IR

## Error Handling

**Strategy:** Errors never crash the system, collected in IR errors list

**Patterns:**
- Try/catch at calculation level (each calculation isolated)
- Errors added to IR.errors list with line numbers
- Error messages rendered in output as red LaTeX: `\color{red}`
- Evaluation continues even if some calculations fail
- CLI shows error count in stats output

**Error Types:**
- `EvaluationError` - Calculation failures
- `UndefinedVariableError` - Variable not defined
- Unit conversion errors - Tracked in IR with `conversion_ok` flag

## Cross-Cutting Concerns

**Logging:**
- Click.echo for normal output
- Click.style for colored output (errors in red)
- No structured logging framework

**Validation:**
- Config validation via dataclass types
- Unit validation via Pint registry
- LaTeX parsing validation via latex2sympy2 (fails gracefully)

**Unit Handling:**
- Pint as single source of truth for unit recognition
- Dynamic unit checking (no hardcoded lists)
- Custom units registered in Pint registry
- SymPy compatibility layer for calculations

**Symbol Normalization:**
- Complex LaTeX names (e.g., `P_{LED,out}`) normalized to simple IDs (`v_{0}`)
- Bidirectional mapping: internal ID ↔ LaTeX name
- Ensures 100% latex2sympy2 parsing success

---

*Architecture analysis: 2026-01-10*
*Update when major patterns change*

