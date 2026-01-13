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


def _clear_text_regex(content: str) -> tuple[str, int]:
    """
    DEPRECATED: Legacy regex-based clear implementation.
    Kept for reference/fallback. Use clear_text() instead.

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


def detect_error_markup(content: str) -> dict:
    """
    Detect existing error/warning markup in content from previous processing.

    Use this to check if a document contains error/warning markup from a previous
    processing run before re-processing.

    Args:
        content: Markdown content to check

    Returns:
        Dict with:
        - has_errors: bool - True if error markup found
        - has_warnings: bool - True if warning markup found (ISS-017)
        - count: int - Number of error patterns found
        - warning_count: int - Number of warning patterns found (ISS-017)
        - has_meta: bool - True if livemathtex-meta comment found
        - patterns: list[str] - Types of error/warning patterns found
    """
    result = {
        'has_errors': False,
        'has_warnings': False,  # ISS-017
        'count': 0,
        'warning_count': 0,  # ISS-017
        'has_meta': False,
        'patterns': []
    }

    # Check for error color markup
    error_matches = re.findall(r'\\color\{red\}', content)
    if error_matches:
        result['has_errors'] = True
        result['count'] = len(error_matches)
        result['patterns'].append('color{red}')

    # ISS-017: Check for warning color markup
    warning_matches = re.findall(r'\\color\{orange\}', content)
    if warning_matches:
        result['has_warnings'] = True
        result['warning_count'] = len(warning_matches)
        result['patterns'].append('color{orange}')

    # Check for inline error text
    inline_errors = re.findall(r'\\text\{\(Error:', content)
    if inline_errors:
        result['has_errors'] = True
        result['count'] += len(inline_errors)
        result['patterns'].append('text{Error}')

    # Check for livemathtex metadata
    if 'livemathtex-meta' in content:
        result['has_meta'] = True
        result['patterns'].append('livemathtex-meta')

    return result


def clear_text(content: str) -> tuple[str, int]:
    """
    Clear computed values from a processed livemathtex document.

    Uses span-based operations with the hybrid parser to identify math blocks and
    calculation spans, then applies targeted edits without regex-based
    structural matching that can corrupt documents.

    Args:
        content: Processed markdown content with computed values

    Returns:
        Tuple of (cleared_content, count_of_cleared_evaluations)

    Key improvements over regex-based clear_text:
    - Uses parser to find math block boundaries (no regex structure matching)
    - Preserves document structure (no merged blocks)
    - Handles multiline error blocks correctly (ISS-021 fix)
    """
    from .parser.markdown_parser import extract_math_blocks
    from .parser.calculation_parser import parse_math_block_calculations, Span

    # Track edits to apply (start, end, replacement)
    edits: list[tuple[int, int, str]] = []
    count = 0

    # 1. Parse document to find all math blocks
    try:
        blocks = extract_math_blocks(content)
    except Exception:
        # If parsing fails, fall back to empty (no math blocks found)
        blocks = []

    # 2. For each block, identify spans to clear
    for block in blocks:
        try:
            calcs = parse_math_block_calculations(block)
        except Exception:
            continue

        for calc in calcs:
            # For == evaluations, clear the result
            if calc.operation == "==" and calc.result_span:
                count += 1
                # Check if there's a unit hint to preserve
                unit_replacement = ""
                if calc.unit_hint and calc.unit_hint_span:
                    # Preserve the unit hint as [unit] format
                    unit_replacement = f" [{calc.unit_hint}]"
                elif calc.result:
                    # Try to extract unit from \text{unit} in result
                    text_unit_match = re.search(
                        r'(?:\\\\)?\\text\{([^}]+)\}\s*$', calc.result
                    )
                    if text_unit_match:
                        unit = text_unit_match.group(1).replace('\\', '').strip()
                        unit_replacement = f" [{unit}]"

                # Replace result with empty (or unit hint)
                edits.append((
                    calc.result_span.start,
                    calc.result_span.end,
                    unit_replacement
                ))

            # For :=_== combined, clear only the result part after ==
            elif calc.operation == ":=_==" and calc.result_span:
                # Skip if result is already empty (nothing to clear)
                if not calc.result or not calc.result.strip():
                    continue
                count += 1
                unit_replacement = ""
                if calc.unit_hint and calc.unit_hint_span:
                    unit_replacement = f" [{calc.unit_hint}]"
                elif calc.result:
                    text_unit_match = re.search(
                        r'(?:\\\\)?\\text\{([^}]+)\}\s*$', calc.result
                    )
                    if text_unit_match:
                        unit = text_unit_match.group(1).replace('\\', '').strip()
                        unit_replacement = f" [{unit}]"

                edits.append((
                    calc.result_span.start,
                    calc.result_span.end,
                    unit_replacement
                ))

            # For ERROR, we need to handle error markup specially
            # The calculation itself might have error markup inserted
            # We'll handle this with regex below since error markup
            # is inserted by the renderer, not part of the parsed structure

    # 3. Remove error/warning markup with regex (safe - doesn't affect structure)
    # This handles \color{red}{...} and \color{orange}{...} which is rendering output
    # We do this BEFORE applying span edits since error/warning markup may be
    # outside the parsed calculation spans
    cleared = content

    # Error patterns (same as original, safe for error markup removal)
    # Pattern: \color{red}{...} with nested braces
    error_pattern = r'\\color\{red\}\{(?:[^{}]|\{[^{}]*\})*\}'
    cleared = re.sub(error_pattern, '', cleared)

    # ISS-017: Warning patterns - \color{orange}{...} with nested braces
    warning_pattern = r'\\color\{orange\}\{(?:[^{}]|\{[^{}]*\})*\}'
    cleared = re.sub(warning_pattern, '', cleared)

    # Inline error text: \text{(Error: ...)}
    error_text_pattern = r'\\text\{\(Error:[^)]*\)\}'
    cleared = re.sub(error_text_pattern, '', cleared)

    # Multiline error blocks: newline + \\ + \color{red}{\text{...}}
    multiline_error = r'\n\\\\\s*\\color\{red\}\{\\text\{[\s\S]*?\}\}'
    cleared = re.sub(multiline_error, '', cleared)

    # ISS-017: Multiline warning blocks: newline + \\ + \color{orange}{\text{...}}
    multiline_warning = r'\n\\\\\s*\\color\{orange\}\{\\text\{[\s\S]*?\}\}'
    cleared = re.sub(multiline_warning, '', cleared)

    # Clean up orphan artifacts (from old implementation patterns 6-7)
    # Remove orphan line continuation before closing $
    orphan_brace = r'\n?\\\\\s*\}\$'
    cleared = re.sub(orphan_brace, '$', cleared)
    orphan_newline = r'\n\\\\\s*\$'
    cleared = re.sub(orphan_newline, '$', cleared)

    # Fix incomplete definitions with trailing newlines
    incomplete_def = r'(\$[^$]+:=\s*[^\n$]+)\n+\$'
    cleared = re.sub(incomplete_def, r'\1$', cleared)

    # Remove trailing whitespace after == before $ (after error removal)
    # This handles cases like `$bad == $` → `$bad ==$`
    # But preserves `$x == [kJ]$` (unit hints)
    trailing_ws_after_eval = r'(==)\s+\$'
    cleared = re.sub(trailing_ws_after_eval, r'\1$', cleared)

    # 4. Re-parse after error removal to get accurate spans
    # (Error removal may have changed offsets)
    try:
        blocks = extract_math_blocks(cleared)
    except Exception:
        blocks = []

    # Rebuild edits list with fresh spans
    edits = []
    count = 0

    for block in blocks:
        try:
            calcs = parse_math_block_calculations(block)
        except Exception:
            continue

        for calc in calcs:
            if calc.operation == "==" and calc.result_span and calc.operator_span:
                # Skip if result is already empty (nothing to clear)
                if not calc.result or not calc.result.strip():
                    continue
                count += 1
                unit_replacement = ""
                if calc.unit_hint and calc.unit_hint_span:
                    unit_replacement = f" [{calc.unit_hint}]"
                elif calc.result:
                    text_unit_match = re.search(
                        r'(?:\\\\)?\\text\{([^}]+)\}\s*$', calc.result
                    )
                    if text_unit_match:
                        unit = text_unit_match.group(1).replace('\\', '').strip()
                        unit_replacement = f" [{unit}]"

                # Extend span start to operator end to capture whitespace
                edit_start = calc.operator_span.end
                edit_end = calc.result_span.end
                # Also include unit hint span if present
                if calc.unit_hint_span:
                    edit_end = calc.unit_hint_span.end
                    unit_replacement = f" [{calc.unit_hint}]"

                edits.append((edit_start, edit_end, unit_replacement))

            elif calc.operation == ":=_==" and calc.result_span:
                # Skip if result is already empty (nothing to clear)
                if not calc.result or not calc.result.strip():
                    continue
                count += 1
                unit_replacement = ""
                if calc.unit_hint and calc.unit_hint_span:
                    unit_replacement = f" [{calc.unit_hint}]"
                elif calc.result:
                    text_unit_match = re.search(
                        r'(?:\\\\)?\\text\{([^}]+)\}\s*$', calc.result
                    )
                    if text_unit_match:
                        unit = text_unit_match.group(1).replace('\\', '').strip()
                        unit_replacement = f" [{unit}]"

                # For :=_==, there's a secondary == operator
                # We need to find where the == ends and clear from there
                # The result_span starts after == + whitespace
                # Extend start to capture whitespace before result
                edit_start = calc.result_span.start
                edit_end = calc.result_span.end
                if calc.unit_hint_span:
                    edit_end = calc.unit_hint_span.end
                    unit_replacement = f" [{calc.unit_hint}]"

                # Back up to include whitespace (simple approach: start at result - look for space)
                while edit_start > 0 and cleared[edit_start - 1] in ' \t':
                    edit_start -= 1

                edits.append((edit_start, edit_end, unit_replacement))

    # 5. Apply edits in reverse order (end to start) to preserve offsets
    edits.sort(key=lambda x: x[0], reverse=True)

    for start, end, replacement in edits:
        cleared = cleared[:start] + replacement + cleared[end:]

    # 6. Clean up orphan artifacts that may remain
    # After clearing, we might have:
    # - Empty \\ before $ (line continuation without content)
    # - Trailing whitespace before $
    orphan_newline = r'\n\\\\\s*\$'
    cleared = re.sub(orphan_newline, '$', cleared)
    orphan_brace = r'\n?\\\\\s*\}\$'
    cleared = re.sub(orphan_brace, '$', cleared)

    # Fix definitions that end with newline (error was removed)
    incomplete_def = r'(\$[^$]+:=\s*[^\n$]+)\n+\$'
    cleared = re.sub(incomplete_def, r'\1$', cleared)

    # Convert \text{varname} back to varname for evaluations
    text_var_pattern = r'\$\\text\{([^}]+)\}\s*(==)'
    cleared = re.sub(text_var_pattern, r'$\1 \2', cleared)

    # 7. Remove livemathtex metadata comment
    meta_pattern = r'\n+---\n+>\s*\*livemathtex:[^*]+\*\s*<!--\s*livemathtex-meta\s*-->\n*'
    cleared = re.sub(meta_pattern, '\n', cleared)

    # 8. Clean up excessive newlines
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
    if '\\color{red}' in content or '\\color{orange}' in content or 'livemathtex-meta' in content:
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

    # ISS-017: Get warning count from evaluator
    warning_count = evaluator.get_warning_count()

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
        "warnings": warning_count,  # ISS-017
    }

    # 9. Render
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "assigns": assign_count,
        "evals": eval_count,
        "symbolics": symbolic_count,
        "values": value_count,
        "errors": error_count,
        "warnings": warning_count,  # ISS-017
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
    if '\\color{red}' in content or '\\color{orange}' in content or 'livemathtex-meta' in content:
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

    # ISS-017: Get warning count from evaluator
    warning_count = evaluator.get_warning_count()

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
        "warnings": warning_count,  # ISS-017
    }

    # Render
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "assigns": assign_count,
        "evals": eval_count,
        "symbolics": symbolic_count,
        "values": value_count,
        "errors": error_count,
        "warnings": warning_count,  # ISS-017
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

    # ISS-017: Get warning count from evaluator
    warning_count = evaluator.get_warning_count()

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
        "warnings": warning_count,  # ISS-017
    }

    # 6. Render
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "assigns": assign_count,
        "evals": eval_count,
        "symbolics": symbolic_count,
        "values": value_count,
        "errors": error_count,
        "warnings": warning_count,  # ISS-017
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
