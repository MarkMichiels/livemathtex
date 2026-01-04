from typing import List, Dict
from ..parser.models import Document, MathBlock, TextBlock, Calculation, Node

class MarkdownRenderer:
    """
    Reconstructs the Markdown document from the parsed AST,
    incorporating calculation results.
    """
    
    def render(self, document: Document, calculations: Dict[Node, str], metadata: Dict[str, str] = None) -> str:
        """
        Reconstruct document text from AST and calculated results.
        Injects/Updates metadata banner at the top if provided.
        """
        output = []
        
        # Meta banner construction
        if metadata:
            # Format: > *Updated: YYYY-MM-DD HH:MM:SS | Duration: 0.XXs*
            # Hidden marker to identify it: <!-- livemathtex-meta -->
            # But user wants visible info "bovenaan ook meta data ... die nuttig is".
            banner = f"> *Updated: {metadata.get('last_run')} | Duration: {metadata.get('duration')}* <!-- livemathtex-meta -->\n\n"
        else:
            banner = ""
            
        for i, node in enumerate(document.children):
            if isinstance(node, TextBlock):
                text = node.content
                import re
                text = re.sub(r'^> \*Updated:.*?<!-- livemathtex-meta -->\s*', '', text, flags=re.DOTALL)
                output.append(text)
            elif isinstance(node, MathBlock):
                if node in calculations:
                    new_inner = calculations[node] 
                    if node.is_display:
                        math_part = f"$${new_inner}$$"
                    else:
                        math_part = f"${new_inner}$"
                    
                    if node.unit_comment:
                        output.append(f"{math_part} <!-- [{node.unit_comment}] -->")
                    else:
                        output.append(math_part)
                else:
                    output.append(node.content or "")
                    
        full_text = "".join(output)
        return banner + full_text 

