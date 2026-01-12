"""
Core processing pipeline for livemathtex.

Pipeline: Read -> Parse -> Build IR -> Evaluate -> Render -> Write

Version 2.0:
- Simplified IR population (no blocks array)
- Symbols store original + SI values
- Custom units extracted from document

Version 3.0:
- IR as central state throughout processing
- Clean IDs (v1, f1, x1)
- Full custom unit metadata
- Pint-based unit conversions
- Formula dependency tracking
"""

from pathlib import Path
import re
import time
from datetime import datetime
from typing import Optional

from .parser.lexer import Lexer
from .parser.models import MathBlock
from .engine.evaluator import Evaluator
from .render.markdown import MarkdownRenderer
from .ir import IRBuilder, LivemathIR, SymbolEntry, ValueWithUnit
from .ir.schema import LivemathIRV3, SymbolEntryV3, FormulaInfo, CustomUnitEntry
from .config import LivemathConfig


def clear_text(content: str) -> tuple[str, int]:
    """
    Clear computed values from a processed livemathtex document.

    Removes evaluation results (everything after ==) and error markup
    while preserving definitions, structure, and unit hints.

    Args:
        content: Processed markdown content with computed values

    Returns:
        Tuple of (cleared_content, count_of_cleared_evaluations)

    Patterns cleared:
    - `== 42$` -> `==$`
    - `== 49.05\\ \\text{N}$` -> `==$`
    - `\\color{red}{...}` -> removed
    - livemathtex metadata comment -> removed

    Patterns preserved:
    - `:= 5$` (definitions)
    - `<!-- [N] -->` (HTML comment unit hints)
    - `== [N]$` (inline unit hints)
    - `===` (unit definitions)
    - `=>` results (symbolic)
    """
    cleared = content
    count = 0

    # Pattern 1: Clear evaluation results in inline math `$...$`
    # Match: == followed by anything up to closing $
    # But NOT === (unit definitions)
    # Preserves: [unit] inline unit hints
    # Restores: inline unit hints from \text{unit} in output
    # Captures: (stuff before ==)
    # Replace with: \1==$ or \1== [unit]$ if unit hint present
    def clear_inline_eval(match):
        nonlocal count
        count += 1
        prefix = match.group(1)  # Everything before ==
        result_part = match.group(0)[len(prefix)+2:]  # Everything after ==

        # Check if inline unit hint [unit] is already present at end
        unit_hint_match = re.search(r'\[([^\]]+)\]\s*$', result_part)
        if unit_hint_match:
            # Preserve the existing unit hint
            unit = unit_hint_match.group(1)
            return f'{prefix}== [{unit}]$'

        # Try to extract unit from \text{unit} in processed output
        # Pattern: \text{unit} at end of result (handle escaped backslashes)
        # Match both \\text{unit} (escaped) and \text{unit} (single)
        text_unit_match = re.search(r'(?:\\\\)?\\text\{([^}]+)\}\s*$', result_part)
        if text_unit_match:
            # Extract unit from \text{unit} and restore as inline hint
            unit = text_unit_match.group(1)
            # Clean up LaTeX formatting (e.g., \text{m³/h} -> m³/h)
            # Remove LaTeX commands but keep the unit string
            unit_clean = unit.replace('\\', '').strip()
            return f'{prefix}== [{unit_clean}]$'

        # No unit hint found, just clear
        return f'{prefix}==$'

    # Pattern for inline: $...== value$ (not ===)
    # Use negative lookbehind AND negative lookahead to avoid ===
    # Exclude: $...== [unit]$ (unit hints only, no evaluation to clear)
    # Capture group does NOT include the ==
    # Match: == followed by something that's NOT just [unit]
    inline_pattern = r'(\$[^\$]*?)(?<!=)==(?!=)(?!\s*\[[^\]]+\]\s*\$)\s*[^\$]+\$'
    cleared = re.sub(inline_pattern, clear_inline_eval, cleared)

    # Special case: preserve inline unit hints $...== [unit]$
    # These are not evaluations, just unit hints, so don't clear them
    # (They should remain as-is in the input)

    # Pattern 2: Clear evaluation results in display math `$$...$$`
    # Capture group does NOT include the ==
    def clear_display_eval(match):
        nonlocal count
        count += 1
        prefix = match.group(1)
        return f'{prefix}==$$'

    display_pattern = r'(\$\$[^\$]*?)(?<!=)==(?!=)\s*[^\$]+\$\$'
    cleared = re.sub(display_pattern, clear_display_eval, cleared)

    # Pattern 3: Remove error markup (red color) with nested braces
    # \color{red}{...} - LaTeX color commands with braced content
    # Uses pattern that handles one level of nesting: \{(?:[^{}]|\{[^{}]*\})*\}
    # This properly matches \color{red}{\text{...}} without stopping at inner }
    error_pattern = r'\\color\{red\}\{(?:[^{}]|\{[^{}]*\})*\}'
    cleared = re.sub(error_pattern, '', cleared)

    # Pattern 4: Remove inline error text
    # \text{(Error: ...)}
    error_text_pattern = r'\\text\{\(Error:[^)]*\)\}'
    cleared = re.sub(error_text_pattern, '', cleared)

    # Pattern 5: Remove multiline error blocks entirely
    # Matches: newline + \\ + \color{red}{\text{...}} spanning multiple lines
    # The [\s\S]*? matches any character including newlines (non-greedy)
    multiline_error = r'\n\\\\\s*\\color\{red\}\{\\text\{[\s\S]*?\}\}'
    cleared = re.sub(multiline_error, '', cleared)

    # Pattern 6: Remove orphaned line continuation artifacts
    # After error removal, we may have:
    # - \\ }$ (incomplete closing brace)
    # - \\ $ (just line continuation before closing)
    # Replace with just $ to close the math block properly
    orphan_brace = r'\n?\\\\\s*\}\$'
    cleared = re.sub(orphan_brace, '$', cleared)
    orphan_newline = r'\n\\\\\s*\$'
    cleared = re.sub(orphan_newline, '$', cleared)

    # Pattern 7: Fix definitions that end with newline (error was removed)
    # Matches: $expr := value\n$ or $expr := value\n\n$
    # Convert to: $expr := value$
    incomplete_def = r'(\$[^$]+:=\s*[^\n$]+)\n+\$'
    cleared = re.sub(incomplete_def, r'\1$', cleared)

    # Pattern 8: Convert \text{varname} back to varname in evaluations
    # The evaluator wraps variable names in \text{} for display, but the parser
    # needs the original syntax. Only convert at start of math: $\text{name}
    # This allows re-processing of cleared files.
    text_var_pattern = r'\$\\text\{([^}]+)\}\s*(==)'
    cleared = re.sub(text_var_pattern, r'$\1 \2', cleared)

    # Pattern 9: Remove livemathtex metadata comment
    # > *livemathtex: timestamp | stats | errors | duration* <!-- livemathtex-meta -->
    meta_pattern = r'\n+---\n+>\s*\*livemathtex:[^*]+\*\s*<!--\s*livemathtex-meta\s*-->\n*'
    cleared = re.sub(meta_pattern, '\n', cleared)

    # Clean up any double newlines left by removals
    cleared = re.sub(r'\n{3,}', '\n\n', cleared)

    return cleared, count


def process_file(
    input_path: str,
    output_path: str = None,
    verbose: bool = False,
    ir_output_path: str = None,
) -> LivemathIR:
    """
    Main pipeline: Read -> Parse -> Build IR -> Evaluate -> Render -> Write

    Configuration is loaded hierarchically:
    1. CLI -o (output path only, passed via output_path parameter)
    2. Document directives (<!-- livemathtex: ... -->)
    3. Local config (.livemathtex.toml)
    4. Project config (pyproject.toml [tool.livemathtex])
    5. User config (~/.config/livemathtex/config.toml)
    6. Defaults

    Args:
        input_path: Path to input markdown file
        output_path: Path to output markdown file (CLI -o override)
        verbose: If True, write IR to JSON file for debugging
        ir_output_path: Custom path for IR JSON (default: input_path.lmt.json)

    Returns:
        The processed LivemathIR containing all symbol values and results
    """
    start_time = time.time()
    input_path_obj = Path(input_path)

    # 1. Read document
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1a. Pre-process: If content appears to be already processed
    # (contains error markup or livemathtex-meta), clear it first.
    # This ensures idempotent processing of output files.
    if '\\color{red}' in content or 'livemathtex-meta' in content:
        content, _ = clear_text(content)

    # 2. Load config from files (levels 3-6 of hierarchy)
    base_config = LivemathConfig.load(input_path_obj)

    # 3. Parse document directives (level 2 of hierarchy)
    lexer = Lexer()
    doc_directives = lexer.parse_document_directives(content)
    config = base_config.with_overrides(doc_directives)

    # 4. Resolve output path (CLI level 1 > config)
    resolved_output = config.resolve_output_path(input_path_obj, output_path)

    # 5. Parse document structure
    document = lexer.parse(content)

    # 6. Build IR (extracts custom units)
    builder = IRBuilder()
    ir = builder.build(document, source=str(input_path))

    # 7. Evaluate all calculations
    evaluator = Evaluator(config=config)
    results = {}  # Map MathBlock -> Resulting LaTeX string

    error_count = 0
    assign_count = 0
    eval_count = 0
    symbolic_count = 0
    value_count = 0

    for block in document.children:
        if isinstance(block, MathBlock):
            calculations = lexer.extract_calculations(block)
            block_calcs_results = []

            if not calculations:
                continue

            # Extract expression-level config overrides from block comment
            expr_overrides = lexer.extract_config_from_comment(block)

            for calc in calculations:
                # Count by operation type
                if calc.operation == ':=':
                    assign_count += 1
                elif calc.operation == '==':
                    eval_count += 1
                elif calc.operation == ':=_==':
                    assign_count += 1
                    eval_count += 1
                elif calc.operation == '=>':
                    symbolic_count += 1
                elif calc.operation == 'value':
                    value_count += 1

                try:
                    block_line = block.location.start_line if block.location else 0
                    result_latex = evaluator.evaluate(calc, config_overrides=expr_overrides, line=block_line)
                    if '\\color{red}' in result_latex:
                        error_count += 1
                        # Add to IR errors
                        line = block_line
                        ir.add_error(line, f"Evaluation error in: {calc.latex[:50]}...")
                    block_calcs_results.append(result_latex)
                except Exception as e:
                    error_count += 1
                    line = block.location.start_line if block.location else 0
                    ir.add_error(line, str(e))
                    block_calcs_results.append(f"{calc.latex} \\quad \\text{{(Error: {e})}}")

            results[block] = "\n".join(block_calcs_results)

    duration = time.time() - start_time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 8. Update IR with symbol values from evaluator
    _populate_ir_symbols(ir, evaluator)

    # Update IR stats
    ir.stats = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "symbols": len(ir.symbols),
        "definitions": assign_count,
        "evaluations": eval_count,
        "symbolic": symbolic_count,
        "value_refs": value_count,
        "errors": error_count,
    }

    # 9. Render
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "assigns": assign_count,
        "evals": eval_count,
        "symbolics": symbolic_count,
        "values": value_count,
        "errors": error_count
    }

    renderer = MarkdownRenderer()
    new_doc_content = renderer.render(document, results, metadata=metadata)

    # 10. Write output markdown
    with open(resolved_output, 'w') as f:
        f.write(new_doc_content)

    # 11. Optionally write IR JSON for debugging
    if verbose:
        if ir_output_path:
            ir_path = Path(ir_output_path)
        else:
            ir_path = input_path_obj.with_suffix('.lmt.json')
        ir.to_json(ir_path)

    return ir


def _populate_ir_symbols(ir: LivemathIR, evaluator: Evaluator) -> None:
    """
    Populate IR symbols from the evaluator's symbol table.

    Creates SymbolEntry for each defined symbol with:
    - id: Internal v_{n} ID
    - original: User's input value and unit
    - si: SI-converted value and unit
    - valid: Conversion validation flag
    - line: Line number (if available)
    """
    import sympy
    from sympy.physics.units import convert_to
    from sympy.physics import units as u

    si_base = [u.kg, u.meter, u.second, u.ampere, u.kelvin, u.mole, u.candela]

    for name in evaluator.symbols.all_names():
        entry = evaluator.symbols.get(name)
        if not entry:
            continue

        # Use the LaTeX name as the key (user's original notation)
        symbol_key = entry.latex_name if entry.latex_name else name

        # Create original value struct
        original = ValueWithUnit(
            value=entry.original_value,
            unit=entry.original_unit
        )

        # Create SI value struct
        si_value = None
        si_unit_str = None

        try:
            # Get the SI value
            if entry.si_value is not None:
                if hasattr(entry.si_value, 'evalf'):
                    si_value = float(entry.si_value.evalf())
                elif isinstance(entry.si_value, (int, float)):
                    si_value = float(entry.si_value)

            # Get the SI unit as string
            if entry.si_unit is not None:
                si_unit_str = sympy.latex(entry.si_unit)
        except Exception:
            pass

        si = ValueWithUnit(
            value=si_value,
            unit=si_unit_str
        )

        # Create symbol entry
        ir.set_symbol(symbol_key, SymbolEntry(
            id=entry.internal_id or "",
            original=original,
            si=si,
            valid=entry.valid,
            line=entry.line,
        ))


def process_text(
    content: str,
    source: str = "<string>",
) -> tuple[str, LivemathIR]:
    """
    Process markdown content from string (for testing/API use).

    Args:
        content: Markdown content with livemathtex calculations
        source: Source identifier for the IR

    Returns:
        Tuple of (rendered_markdown, ir)
    """
    start_time = time.time()

    # Pre-process: If content appears to be already processed
    # (contains error markup or livemathtex-meta), clear it first.
    # This ensures idempotent processing of output files.
    if '\\color{red}' in content or 'livemathtex-meta' in content:
        content, _ = clear_text(content)

    # 1. Parse document structure
    lexer = Lexer()
    document = lexer.parse(content)

    # 2. Parse document directives and create config
    doc_directives = lexer.parse_document_directives(content)
    config = LivemathConfig().with_overrides(doc_directives) if doc_directives else LivemathConfig()

    # 3. Build IR
    builder = IRBuilder()
    ir = builder.build(document, source=source)

    # 4. Evaluate
    evaluator = Evaluator(config=config)
    results = {}

    error_count = 0
    assign_count = 0
    eval_count = 0
    symbolic_count = 0
    value_count = 0

    for block in document.children:
        if isinstance(block, MathBlock):
            calculations = lexer.extract_calculations(block)
            block_calcs_results = []

            if not calculations:
                continue

            expr_overrides = lexer.extract_config_from_comment(block)

            # ISS-013: Track inline unit hint from calculations for renderer
            # If a calculation has unit_comment but the block doesn't, propagate it
            inline_unit_hint = None
            for calc in calculations:
                if calc.unit_comment and not block.unit_comment:
                    inline_unit_hint = calc.unit_comment
                    break  # Use first found

            for calc in calculations:
                if calc.operation == ':=':
                    assign_count += 1
                elif calc.operation == '==':
                    eval_count += 1
                elif calc.operation == ':=_==':
                    assign_count += 1
                    eval_count += 1
                elif calc.operation == '=>':
                    symbolic_count += 1
                elif calc.operation == 'value':
                    value_count += 1

                try:
                    result_latex = evaluator.evaluate(calc, config_overrides=expr_overrides)
                    if '\\color{red}' in result_latex:
                        error_count += 1
                    block_calcs_results.append(result_latex)
                except Exception as e:
                    error_count += 1
                    block_calcs_results.append(f"{calc.latex} \\quad \\text{{(Error: {e})}}")

            # ISS-013: Store result with optional inline unit hint for renderer
            results[block] = ("\n".join(block_calcs_results), inline_unit_hint)

    duration = time.time() - start_time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Populate IR symbols
    _populate_ir_symbols(ir, evaluator)

    ir.stats = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "symbols": len(ir.symbols),
        "definitions": assign_count,
        "evaluations": eval_count,
        "symbolic": symbolic_count,
        "value_refs": value_count,
        "errors": error_count,
    }

    # Render
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "assigns": assign_count,
        "evals": eval_count,
        "symbolics": symbolic_count,
        "values": value_count,
        "errors": error_count
    }

    renderer = MarkdownRenderer()
    new_doc_content = renderer.render(document, results, metadata=metadata)

    return new_doc_content, ir


# =============================================================================
# IR v3.0 Processing Functions
# =============================================================================


def process_text_v3(
    content: str,
    source: str = "<string>",
    config: Optional[LivemathConfig] = None,
) -> tuple[str, LivemathIRV3]:
    """
    Process markdown content using IR v3.0 schema.

    Uses clean IDs (v1, f1, x1), Pint-based units, and full custom unit
    metadata. The IR serves as central state throughout processing.

    Args:
        content: Markdown content with livemathtex calculations
        source: Source identifier for the IR

    Returns:
        Tuple of (rendered_markdown, ir_v3)
    """
    start_time = time.time()

    # 1. Parse document structure
    lexer = Lexer()
    document = lexer.parse(content)

    # 2. Build config (caller may provide a fully-resolved config, e.g. from file hierarchy)
    if config is None:
        doc_directives = lexer.parse_document_directives(content)
        config = LivemathConfig().with_overrides(doc_directives) if doc_directives else LivemathConfig()

    # 3. Build IR v3.0 (extracts custom units with full metadata)
    builder = IRBuilder()
    ir = builder.build_v3(document, source=source)

    # 4. Evaluate with v3.0 mode
    # Note: For now we still use the existing evaluator but collect v3.0 data
    evaluator = Evaluator(config=config)
    results = {}

    error_count = 0
    assign_count = 0
    eval_count = 0
    symbolic_count = 0
    value_count = 0

    for block in document.children:
        if isinstance(block, MathBlock):
            calculations = lexer.extract_calculations(block)
            block_calcs_results = []

            if not calculations:
                continue

            expr_overrides = lexer.extract_config_from_comment(block)

            for calc in calculations:
                if calc.operation == ':=':
                    assign_count += 1
                elif calc.operation == '==':
                    eval_count += 1
                elif calc.operation == ':=_==':
                    assign_count += 1
                    eval_count += 1
                elif calc.operation == '=>':
                    symbolic_count += 1
                elif calc.operation == 'value':
                    value_count += 1

                try:
                    result_latex = evaluator.evaluate(calc, config_overrides=expr_overrides)
                    if '\\color{red}' in result_latex:
                        error_count += 1
                    block_calcs_results.append(result_latex)
                except Exception as e:
                    error_count += 1
                    block_calcs_results.append(f"{calc.latex} \\quad \\text{{(Error: {e})}}")

            results[block] = "\n".join(block_calcs_results)

    duration = time.time() - start_time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 5. Populate IR v3.0 symbols
    _populate_ir_symbols_v3(ir, evaluator)

    ir.stats = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "symbols": len(ir.symbols),
        "custom_units": len(ir.custom_units),
        "definitions": assign_count,
        "evaluations": eval_count,
        "symbolic": symbolic_count,
        "value_refs": value_count,
        "errors": error_count,
    }

    # 6. Render
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "assigns": assign_count,
        "evals": eval_count,
        "symbolics": symbolic_count,
        "values": value_count,
        "errors": error_count
    }

    renderer = MarkdownRenderer()
    new_doc_content = renderer.render(document, results, metadata=metadata)

    return new_doc_content, ir


def _populate_ir_symbols_v3(ir: LivemathIRV3, evaluator: Evaluator) -> None:
    """
    Populate IR v3.0 symbols from the evaluator's symbol table.

    Creates SymbolEntryV3 for each defined symbol with:
    - Clean ID as key (v1, f1, etc.)
    - latex_name: Original LaTeX name
    - original: User's input value and unit
    - base: SI-converted value and unit (using Pint)
    - conversion_ok: Validation flag
    - formula: Expression, dependencies, parameters (if applicable)
    """
    from .engine.pint_backend import convert_to_base_units

    for name in evaluator.symbols.all_names():
        entry = evaluator.symbols.get(name)
        if not entry:
            continue

        # Get or generate clean ID
        internal_id = entry.internal_id or ""

        # For v3.0, we need clean IDs like v1, f1
        # The current system may still use v_{0} format
        # We'll use the internal_id as-is for now (the NameGenerator handles the format)

        # Create original value struct
        original = ValueWithUnit(
            value=entry.original_value,
            unit=entry.original_unit
        )

        # Convert to base units using Pint
        if entry.original_value is not None and entry.original_unit:
            conversion = convert_to_base_units(entry.original_value, entry.original_unit)
            base = ValueWithUnit(
                value=conversion.base_value,
                unit=conversion.base_unit
            )
            conversion_ok = conversion.success
            conversion_error = conversion.error if not conversion.success else None
        else:
            # No unit or no value - use original as base
            base_value = None
            if entry.si_value is not None:
                try:
                    if hasattr(entry.si_value, 'evalf'):
                        base_value = float(entry.si_value.evalf())
                    elif isinstance(entry.si_value, (int, float)):
                        base_value = float(entry.si_value)
                except Exception:
                    pass
            base = ValueWithUnit(
                value=base_value if base_value is not None else entry.original_value,
                unit=None
            )
            conversion_ok = entry.valid
            conversion_error = None

        # Create formula info if this is a formula
        formula_info = None
        if entry.is_formula:
            formula_info = FormulaInfo(
                expression=entry.formula_expression,
                depends_on=entry.depends_on,
                parameters=entry.parameters if entry.parameters else None,
                parameter_latex=entry.parameter_latex if entry.parameter_latex else None,
            )

        # Create symbol entry
        symbol_entry = SymbolEntryV3(
            latex_name=entry.latex_name if entry.latex_name else name,
            original=original,
            base=base,
            conversion_ok=conversion_ok,
            formula=formula_info,
            line=entry.line,
            conversion_error=conversion_error,
        )

        # Use clean ID as key (or internal_id)
        ir.set_symbol(internal_id if internal_id else name, symbol_entry)
