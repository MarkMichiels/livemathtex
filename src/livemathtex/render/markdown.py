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
        Injects/Updates metadata footer at the bottom if provided.
        """
        import re
        output = []

        for i, node in enumerate(document.children):
            if isinstance(node, TextBlock):
                text = node.content
                # Remove old top-banner style metadata
                text = re.sub(r'^> \*Updated:.*?<!-- livemathtex-meta -->\s*', '', text, flags=re.DOTALL)
                # Remove old bottom-banner style metadata
                text = re.sub(r'\n*---\n\n> \*livemathtex:.*?<!-- livemathtex-meta -->\s*$', '', text, flags=re.DOTALL)
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

        full_text = "".join(output).rstrip()

        # Meta footer construction at bottom
        if metadata:
            assigns = metadata.get('assigns', 0)
            evals = metadata.get('evals', 0)
            symbolics = metadata.get('symbolics', 0)
            errors = metadata.get('errors', 0)

            # Build stats with descriptive names
            stats_parts = []
            if assigns > 0:
                stats_parts.append(f"{assigns} definition{'s' if assigns != 1 else ''}")
            if evals > 0:
                stats_parts.append(f"{evals} evaluation{'s' if evals != 1 else ''}")
            if symbolics > 0:
                stats_parts.append(f"{symbolics} symbolic")
            stats_str = ", ".join(stats_parts) if stats_parts else "0 operations"

            error_str = "no errors" if errors == 0 else f"{errors} error{'s' if errors != 1 else ''}"
            footer = f"\n\n---\n\n> *livemathtex: {metadata.get('last_run')} | {stats_str} | {error_str} | {metadata.get('duration')}* <!-- livemathtex-meta -->\n"
        else:
            footer = "\n"

        return full_text + footer
