from pathlib import Path
import time
from datetime import datetime

from .parser.lexer import Lexer
from .parser.models import MathBlock
from .engine.evaluator import Evaluator
from .render.markdown import MarkdownRenderer
try:
    from .utils.errors import livemathtexError
except ImportError:
    pass

def process_file(input_path: str, output_path: str = None):
    """
    Main pipeline: Read -> Parse -> Calculate -> Render -> Write
    """
    start_time = time.time()
    
    # 1. Read
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 2. Parse
    lexer = Lexer()
    document = lexer.parse(content)
    
    # 3. Evaluate
    evaluator = Evaluator()
    results = {} # Map MathBlock -> Resulting Latex string (full block content)
    
    for block in document.children:
        if isinstance(block, MathBlock):
            calculations = lexer.extract_calculations(block)
            block_calcs_results = []
            
            # If no calculations in block, we don't put it in results dict (renderer uses original)
            if not calculations:
                continue
                
            for calc in calculations:
                try:
                    result_latex = evaluator.evaluate(calc)
                    block_calcs_results.append(result_latex)
                except Exception as e:
                     block_calcs_results.append(f"{calc.latex} \\quad \\text{{(System Error: {e})}}")
            
            # Join multiple calculations in one block with newline to preserve structure
            # Use newline character \n
            results[block] = "\n".join(block_calcs_results)

    duration = time.time() - start_time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata = {
        "last_run": now_str,
        "duration": f"{duration:.2f}s"
    }
    
    # 4. Render
    renderer = MarkdownRenderer()
    new_doc_content = renderer.render(document, results, metadata=metadata)
    
    # 5. Write
    if output_path:
        final_path = output_path
    else:
        final_path = input_path
        
    with open(final_path, 'w') as f:
        f.write(new_doc_content)
