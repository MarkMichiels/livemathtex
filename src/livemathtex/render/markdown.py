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

        Note: calculations dict values can be either:
        - str: The calculated result LaTeX (legacy format)
        - tuple[str, Optional[str]]: (result, inline_unit_hint) for ISS-013 support
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
                    calc_value = calculations[node]

                    # ISS-013: Support tuple format (result, inline_unit_hint)
                    if isinstance(calc_value, tuple):
                        new_inner, inline_unit_hint = calc_value
                    else:
                        new_inner = calc_value
                        inline_unit_hint = None

                    # Check if this is a value display (<!-- value:... --> syntax)
                    # Value display outputs the number in math mode, preserving the comment
                    # Input:  $ $ <!-- value:vel [\frac{m}{s}] :2 -->
                    # Output: $1.77$ <!-- value:vel [\frac{m}{s}] :2 -->
                    if node.value_comment:
                        # Output value in math mode (with dollar signs), preserve original comment
                        if node.is_display:
                            output.append(f"$${new_inner}$$ <!-- value:{node.value_comment} -->")
                        else:
                            output.append(f"${new_inner}$ <!-- value:{node.value_comment} -->")
                    else:
                        # Normal calculation: output LaTeX
                        if node.is_display:
                            math_part = f"$${new_inner}$$"
                        else:
                            math_part = f"${new_inner}$"

                        # ISS-013: Use inline_unit_hint if block doesn't have unit_comment
                        # This preserves inline [unit] syntax as HTML comment in output
                        effective_unit = node.unit_comment or inline_unit_hint

                        # Preserve comments: unit_comment and/or config_comment
                        if effective_unit and node.config_comment:
                            # Both unit and config: combine them
                            output.append(f"{math_part} <!-- [{effective_unit}] {node.config_comment} -->")
                        elif effective_unit:
                            output.append(f"{math_part} <!-- [{effective_unit}] -->")
                        elif node.config_comment:
                            output.append(f"{math_part} <!-- {node.config_comment} -->")
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
            values = metadata.get('values', 0)
            errors = metadata.get('errors', 0)
            warnings = metadata.get('warnings', 0)  # ISS-017: Track warnings separately

            # Build stats with descriptive names
            stats_parts = []
            if assigns > 0:
                stats_parts.append(f"{assigns} definition{'s' if assigns != 1 else ''}")
            if evals > 0:
                stats_parts.append(f"{evals} evaluation{'s' if evals != 1 else ''}")
            if symbolics > 0:
                stats_parts.append(f"{symbolics} symbolic")
            if values > 0:
                stats_parts.append(f"{values} value ref{'s' if values != 1 else ''}")
            stats_str = ", ".join(stats_parts) if stats_parts else "0 operations"

            # ISS-017: Build status string with both errors and warnings
            status_parts = []
            if errors == 0:
                status_parts.append("no errors")
            else:
                status_parts.append(f"{errors} error{'s' if errors != 1 else ''}")
            if warnings > 0:
                status_parts.append(f"{warnings} warning{'s' if warnings != 1 else ''}")
            status_str = ", ".join(status_parts)

            footer = f"\n\n---\n\n> *livemathtex: {metadata.get('last_run')} | {stats_str} | {status_str} | {metadata.get('duration')}* <!-- livemathtex-meta -->\n"
        else:
            footer = "\n"

        return full_text + footer
