from pathlib import Path
import time
from datetime import datetime
from typing import Optional

from .parser.lexer import Lexer
from .parser.models import MathBlock
from .engine.evaluator import Evaluator
from .render.markdown import MarkdownRenderer
from .ir import IRBuilder, LivemathIR
from .config import LivemathConfig

try:
    from .utils.errors import livemathtexError
except ImportError:
    pass


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

    # 6. Build IR
    builder = IRBuilder()
    ir = builder.build(document, source=str(input_path))

    # 7. Extract calculations and evaluate (with config)
    evaluator = Evaluator(config=config)
    results = {}  # Map MathBlock -> Resulting LaTeX string (full block content)
    all_calculations = []  # Flat list for IR evaluation

    error_count = 0
    assign_count = 0  # :=
    eval_count = 0    # ==
    symbolic_count = 0  # =>
    value_count = 0   # <!-- value -->

    for block in document.children:
        if isinstance(block, MathBlock):
            calculations = lexer.extract_calculations(block)
            block_calcs_results = []

            # If no calculations in block, we don't put it in results dict (renderer uses original)
            if not calculations:
                continue

            # Extract expression-level config overrides from block comment
            expr_overrides = lexer.extract_config_from_comment(block)

            for calc in calculations:
                all_calculations.append(calc)

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
                    # Pass expression-level overrides to evaluator
                    result_latex = evaluator.evaluate(calc, config_overrides=expr_overrides)
                    # Check if the evaluator returned an error (contains \color{red})
                    if '\\color{red}' in result_latex:
                        error_count += 1
                    block_calcs_results.append(result_latex)
                except Exception as e:
                    error_count += 1
                    block_calcs_results.append(f"{calc.latex} \\quad \\text{{(Error: {e})}}")

            # Join multiple calculations in one block with newline to preserve structure
            results[block] = "\n".join(block_calcs_results)

    duration = time.time() - start_time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update IR stats
    ir.stats = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "definitions": assign_count,
        "evaluations": eval_count,
        "symbolic": symbolic_count,
        "value_refs": value_count,
        "errors": error_count,
    }

    # Update IR blocks with results
    block_idx = 0
    for block in document.children:
        if isinstance(block, MathBlock):
            calculations = lexer.extract_calculations(block)
            for calc in calculations:
                if block_idx < len(ir.blocks):
                    result_key = block
                    if result_key in results:
                        # Split results back to individual calculations
                        result_parts = results[result_key].split('\n')
                        if block_idx < len(result_parts):
                            ir.blocks[block_idx].latex_output = result_parts[block_idx % len(result_parts)]
                block_idx += 1

    # Update IR symbols with computed values from evaluator
    from sympy.physics.units import convert_to
    from sympy.physics import units as u
    import sympy

    si_base = [u.kg, u.meter, u.second, u.ampere, u.kelvin, u.mole, u.candela]

    for name in evaluator.symbols.all_names():
        entry = evaluator.symbols.get(name)
        if not entry:
            continue

        # IR stores original LaTeX names (L_{pipe}), SymbolTable stores normalized (L_pipe)
        # Look up by original latex_name if available
        ir_key = entry.latex_name if entry.latex_name else name

        if ir_key not in ir.symbols:
            # Try normalized name as fallback
            ir_key = name

        if ir_key in ir.symbols:
            ir_entry = ir.symbols[ir_key]

            # Update internal_name in mapping to v_{n} format
            if entry.internal_id:
                ir_entry.mapping.internal_name = entry.internal_id

            # Update unit_latex from SymbolValue
            if entry.unit_latex:
                ir_entry.unit_latex = entry.unit_latex

            try:
                value = entry.value

                # First convert to SI base units for consistent storage
                try:
                    value_si = convert_to(value, si_base)
                except:
                    value_si = value

                # Simplify and evaluate any remaining symbolic constants (like pi)
                if hasattr(value_si, 'simplify'):
                    value_si = value_si.simplify()
                if hasattr(value_si, 'evalf'):
                    value_si = value_si.evalf()

                # Extract numeric value and unit using as_coeff_Mul
                if hasattr(value_si, 'as_coeff_Mul'):
                    coeff, unit_part = value_si.as_coeff_Mul()

                    # Store numeric coefficient
                    if hasattr(coeff, 'is_number') and coeff.is_number:
                        ir_entry.value = float(coeff)
                    elif hasattr(coeff, 'evalf'):
                        ir_entry.value = float(coeff.evalf())
                    else:
                        ir_entry.value = float(coeff)

                    # Store unit as simplified SI string
                    if unit_part != 1:
                        ir_entry.unit = sympy.latex(unit_part)

                elif isinstance(value, (int, float)):
                    ir_entry.value = float(value)

            except Exception:
                pass  # Skip symbols that can't be converted

    # 8. Render
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

    # 9. Write output markdown (using resolved path from config)
    with open(resolved_output, 'w') as f:
        f.write(new_doc_content)

    # 10. Optionally write IR JSON for debugging
    if verbose:
        if ir_output_path:
            ir_path = Path(ir_output_path)
        else:
            ir_path = input_path_obj.with_suffix('.lmt.json')
        ir.to_json(ir_path)

    return ir


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

    # 1. Parse document structure
    lexer = Lexer()
    document = lexer.parse(content)

    # 2. Parse document directives and create config
    doc_directives = lexer.parse_document_directives(content)
    config = LivemathConfig().with_overrides(doc_directives) if doc_directives else LivemathConfig()

    # 3. Build IR
    builder = IRBuilder()
    ir = builder.build(document, source=source)

    # 4. Evaluate (with config)
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

            # Extract expression-level config overrides from block comment
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
                    # Pass expression-level overrides to evaluator
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

    ir.stats = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s",
        "definitions": assign_count,
        "evaluations": eval_count,
        "symbolic": symbolic_count,
        "value_refs": value_count,
        "errors": error_count,
    }

    # 4. Render
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
