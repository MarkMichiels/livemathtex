# Architecture

**Analysis Date:** 2026-05-21

## Pattern Overview

**Overall:** Two-phase pipeline architecture with modular separation of concerns

**Key Characteristics:**
- **Two processing pipelines**: v2.0 (legacy) and v3.0 (current with Pint units)
- **Streaming evaluation**: Process document once, evaluate inline as parsing discovers math blocks
- **IR-centric**: All state flows through LivemathIR intermediate representation
- **Unit-aware**: Pint backend provides unit registry, validation, and conversion
- **Symbol normalization**: All variables internally normalized to v{N}, f{N}, x{N} IDs

## Layers

**Parsing Layer:**
- Purpose: Convert raw markdown text → structured Document AST with identified math blocks
- Location: `src/livemathtex/parser/`
- Contains: 
  - `lexer.py` — Document tokenizer, math block extraction, calculation extraction (`:=`, `==`, `=>`, `===`)
  - `markdown_parser.py` — Two-layer hybrid parser (markdown-it-py + pylatexenc)
  - `expression_tokenizer.py` — LaTeX expression tokenization
  - `expression_parser.py` — Expression parsing to AST
  - `calculation_parser.py` — Math block calculation span identification
  - `models.py` — AST node definitions (MathBlock, TextBlock, Calculation, Document)
  - `reference_parser.py` — Cross-reference (`{{variable}}`) detection
- Depends on: markdown-it-py, mdit-py-plugins, pylatexenc
- Used by: IRBuilder, Evaluator, clear_text operations

**IR (Intermediate Representation) Layer:**
- Purpose: Maintain symbol state and calculation metadata throughout processing
- Location: `src/livemathtex/ir/`
- Contains:
  - `schema.py` — V2.0 (legacy) and V3.0 IR schemas (SymbolEntry, LivemathIR, LivemathIRV3)
  - `builder.py` — Document AST → IR conversion, custom unit extraction
- Depends on: parser models
- Used by: Core processing (process_text, process_text_v3), Evaluator

**Engine (Calculation) Layer:**
- Purpose: Execute mathematical expressions and unit conversions
- Location: `src/livemathtex/engine/`
- Contains:
  - `evaluator.py` — Main calculation executor, symbol table management, evaluation orchestration
  - `expression_evaluator.py` — AST evaluation with Pint quantities
  - `pint_backend.py` — Pint unit registry wrapper, unit validation, custom unit definitions
  - `symbols.py` — SymbolTable class, variable name normalization (v0/f0/x0 scheme)
- Depends on: Pint, parser models, IR
- Used by: Core processing, cross-reference evaluation

**Configuration Layer:**
- Purpose: Hierarchical config system with multiple levels of override
- Location: `src/livemathtex/config.py`
- Contains: LivemathConfig dataclass, TOML/pyproject.toml loading
- Depends on: tomli/tomllib (Python 3.11+)
- Used by: Core processing, Evaluator

**Rendering Layer:**
- Purpose: Reconstruct markdown document with calculated results injected
- Location: `src/livemathtex/render/`
- Contains: `markdown.py` — MarkdownRenderer, metadata footer injection
- Depends on: parser models
- Used by: Core processing

**Core Processing Layer:**
- Purpose: Orchestrate full pipeline from text → parsed → evaluated → rendered
- Location: `src/livemathtex/core.py`
- Contains: 
  - `process_text()` — V2.0 pipeline (default)
  - `process_text_v3()` — V3.0 pipeline (Pint-based)
  - `process_file()` — File I/O wrapper
  - `clear_text()` — Remove computed values while preserving definitions
  - `detect_error_markup()` — Check for previous error markup
  - Cross-reference evaluation
- Used by: CLI, public API

**CLI & Configuration Layer:**
- Purpose: Command-line interface and user entry points
- Location: `src/livemathtex/cli.py`
- Contains: Click commands (process, inspect, clear, copy)
- Entry point: `main()` function
- Used by: Command line, setuptools entry point

## Data Flow

**Standard Evaluation Flow (process_text_v3):**

1. **Input**: Raw markdown content (e.g., `$x := 5$\n$y := x^2 ==$ `)
2. **Parse Document** (`Lexer.parse()`)
   - Tokenize: Extract text regions and math blocks (`$...$`, `$$...$$`)
   - Identify: Locate calculation operators within blocks (`:=`, `==`, `=>`, `===`)
   - Output: Document AST with MathBlock and TextBlock nodes
3. **Build IR** (`IRBuilder.build()`)
   - Extract custom unit definitions (`unit === 1000 N` → ir.custom_units)
   - Initialize empty SymbolEntry slots
   - Output: LivemathIR with empty symbols
4. **Evaluate Blocks** (process_text_v3 main loop)
   - For each MathBlock in document:
     - Extract calculations: `var := expr`, `expr ==`, etc.
     - For each Calculation:
       - **Parse expression**: ExpressionTokenizer → ExpressionParser → AST
       - **Evaluate AST**: expression_evaluator uses Pint for unit conversion
       - **Store result**: Update IR symbols, format LaTeX result
       - Increment counters (assignments, evaluations, errors)
   - Handle errors: Wrap in `\color{red}{...}` formatting
5. **Evaluate Cross-References** (evaluate_cross_references)
   - Find `{{variable}}` patterns in prose text
   - Look up in symbol table (with name variation fallback)
   - Replace with calculated value
6. **Render Output** (`MarkdownRenderer.render()`)
   - Reconstruct document from AST
   - Inject calculated results into math blocks
   - Add metadata footer with stats
7. **Output**: Markdown with computed results + LivemathIRV3 JSON (optional)

**Clear Flow (clear_text):**

1. **Input**: Processed markdown with evaluation results and possible error markup
2. **Remove Error Markup**: Regex patterns for `\color{red}{...}`, `\color{orange}{...}`
3. **Parse Math Blocks**: Find structure using markdown parser
4. **Identify Result Spans**: For each `==` evaluation, locate result substring
5. **Edit Spans**: Remove results, preserve unit hints (`[unit]` format)
6. **Remove Metadata**: Strip livemathtex footer comment
7. **Output**: Markdown ready for re-processing

## State Management

**Symbol Table** (`engine/symbols.py`):
- Maps LaTeX variable names ↔ internal IDs (v0, f0, x0)
- Stores current value, unit, dependencies
- Updated during evaluation phase

**IR (Intermediate Representation)**:
- **V2.0 (legacy)**: `symbols` dict with SymbolEntry (id, original, si, valid)
- **V3.0 (current)**: Extended schema with FormulaInfo (expression, depends_on), CustomUnitEntry (type, pint_definition)
- Immutable state passed through pipeline
- Serializable to JSON for inspection

**Pint UnitRegistry** (`engine/pint_backend.py`):
- Global singleton initialized once per process
- Case-sensitive unit parsing
- Custom units: EUR, USD, dag, uur, jaar (Dutch aliases)
- Reset between major operations for test isolation

## Key Abstractions

**MathBlock** (parser/models.py):
- Purpose: Represents a single LaTeX math region
- Examples: `$x := 5$`, `$$\frac{a}{b}$$`
- Pattern: Immutable frozen dataclass with location tracking

**Calculation** (parser/models.py):
- Purpose: Single calculation action within a math block
- Examples: Assignment (`:=`), evaluation (`==`), symbolic (`=>`)
- Pattern: Immutable, contains operation type, target variable, error info

**SymbolEntry** (ir/schema.py):
- Purpose: Complete record of a symbol's definition and conversions
- Contains: id, original value, SI value, validation status, error message
- Used by: IR during evaluation, serialized to JSON output

**Evaluator** (engine/evaluator.py):
- Purpose: Orchestrate expression evaluation with symbol context
- Methods: `evaluate()`, `evaluate_ir()`, `register_custom_unit()`
- State: SymbolTable, warning counter, IR reference

## Entry Points

**CLI Entry** (`cli.py`):
- Location: `src/livemathtex/cli.py`
- Command: `livemathtex process input.md [-o output.md] [-v]`
- Triggers: File reading, config loading, document processing
- Responsibilities: Parse CLI args, load document directives, call process_text_v3 or process_file

**API Entry** (`__init__.py`):
- Location: `src/livemathtex/__init__.py`
- Functions: `process_text()`, `process_text_v3()`, `process_file()`, `clear_text()`
- Triggers: Programmatic calls from external code
- Responsibilities: Full processing pipeline

**File Processing** (`core.py`):
- Location: `src/livemathtex/core.py`
- Function: `process_file(input_path, output_path, verbose)`
- Triggers: File I/O, document loading
- Responsibilities: Read file, process_text_v3, write output

## Error Handling

**Strategy:** Two-level error capture with graceful degradation

**Patterns:**

1. **Expression Evaluation Errors**:
   - Caught in: `Evaluator.evaluate()`, `expression_evaluator.evaluate_expression_tree()`
   - Handling: Wrapped in `\color{red}{\text{(Error: message)}}` for display
   - IR: Error recorded in ir.errors with line number
   - Result: Block continues processing, error marked as failed

2. **Unit Conversion Errors**:
   - Caught in: `expression_evaluator` (Pint IncompatibleUnitsError)
   - Handling: Displayed as dimensional analysis error
   - IR: SymbolEntry.valid = False, error message captured
   - Result: Original and base units both None

3. **Parsing Errors**:
   - Caught in: `ExpressionParser`, `ExpressionTokenizer`
   - Handling: ParseError raised, caught at block level
   - Result: Block evaluation skipped, error logged

4. **File I/O Errors**:
   - Caught in: CLI commands
   - Handling: User-facing error message via click.echo(err=True)
   - Result: SystemExit(1)

## Cross-Cutting Concerns

**Logging**: 
- Framework: Python logging (see logger = logging.getLogger(__name__) in evaluator.py)
- Uses: INFO/DEBUG for calculation steps, ERROR for failures
- Configuration: No explicit handlers (inherits from root logger)

**Validation**:
- Variables: SymbolTable normalization prevents conflicts
- Units: Pint registry validates unit names, check_variable_name_conflict() in pint_backend
- Expressions: ExpressionParser validates syntax
- Configuration: LivemathConfig.with_overrides() type-checks overrides

**Authentication**:
- Not applicable (CLI-only, no API auth)

**Unit System**:
- Configuration: config.unit_system ("SI", "imperial", "CGS")
- Conversion: Pint handles all conversions using registry
- Display: format_unit_latex() in pint_backend formats for LaTeX output
- Custom units: Extracted from document (`unit === definition`), stored in IR

---

*Architecture analysis: 2026-05-21*
