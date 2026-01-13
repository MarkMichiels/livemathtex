"""
Hybrid markdown/LaTeX parser for LiveMathTeX.

Two-layer parsing approach:
1. markdown-it-py + dollarmath_plugin: Document structure, math block boundaries
2. pylatexenc LatexWalker: Character-level positions within LaTeX content

This provides robust handling of code fences and precise position tracking
for operators and expressions within math blocks.
"""

from dataclasses import dataclass
from typing import Any, List, Optional

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from pylatexenc.latexwalker import LatexWalker


@dataclass
class LaTeXPosition:
    """Position of a LaTeX element within a math block."""
    pos: int           # Start position within LaTeX content
    pos_end: int       # End position within LaTeX content
    node_type: str     # 'chars', 'macro', 'group', etc.
    content: str       # The actual content


@dataclass
class ParsedMathBlock:
    """Math block with document and LaTeX-level positions."""
    content: str              # Full content including $$
    inner_content: str        # Content without delimiters
    is_display: bool
    doc_start_offset: int     # Character offset in document
    doc_end_offset: int       # End offset in document
    start_line: int           # 0-indexed line number
    end_line: int             # 0-indexed (exclusive)
    latex_nodes: List[Any]    # pylatexenc nodes with positions


class MarkdownParser:
    """Two-layer parser: markdown-it-py + pylatexenc."""

    def __init__(self):
        """Initialize the markdown parser with dollarmath plugin."""
        self.md = MarkdownIt().use(
            dollarmath_plugin,
            allow_space=True,
            allow_digits=True
        )

    def parse(self, text: str) -> List[Any]:
        """Parse markdown and return token stream.

        Args:
            text: Raw markdown text

        Returns:
            List of markdown-it-py tokens
        """
        # Normalize line endings
        text = text.replace('\r\n', '\n')
        return self.md.parse(text)


def build_line_offset_map(text: str) -> List[int]:
    """Build cumulative character offsets for each line start.

    Args:
        text: Document text (should have normalized line endings)

    Returns:
        List where index i gives the character offset where line i starts.
        Line numbers are 0-indexed.

    Example:
        >>> build_line_offset_map("abc\\ndef\\nghi")
        [0, 4, 8]
        # Line 0 starts at char 0, line 1 at char 4, line 2 at char 8
    """
    offsets = [0]
    for i, char in enumerate(text):
        if char == '\n':
            offsets.append(i + 1)
    return offsets


def line_to_char_offset(line: int, line_offsets: List[int]) -> int:
    """Convert 0-indexed line number to character offset.

    Args:
        line: 0-indexed line number
        line_offsets: List from build_line_offset_map()

    Returns:
        Character offset of the start of that line
    """
    if line < len(line_offsets):
        return line_offsets[line]
    return line_offsets[-1] if line_offsets else 0


def parse_latex_content(latex: str) -> List[Any]:
    """Parse LaTeX string and return nodes with positions.

    Uses tolerant_parsing=True to handle incomplete/malformed LaTeX
    without crashing.

    Args:
        latex: LaTeX content (without $$ delimiters)

    Returns:
        List of pylatexenc LatexNode objects with pos/pos_end attributes
    """
    walker = LatexWalker(latex, tolerant_parsing=True)
    nodes, _, _ = walker.get_latex_nodes()
    return nodes if nodes else []


def extract_math_blocks(text: str) -> List[ParsedMathBlock]:
    """Extract all math blocks with full position information.

    This is the main entry point for the hybrid parser. It:
    1. Normalizes line endings
    2. Parses with markdown-it-py to find math blocks
    3. Builds line offset map for position conversion
    4. For each math block, parses LaTeX content with pylatexenc
    5. Returns blocks with both document and LaTeX-level positions

    Args:
        text: Raw markdown document

    Returns:
        List of ParsedMathBlock with complete position information
    """
    # 1. Normalize line endings
    text = text.replace('\r\n', '\n')

    # 2. Parse with markdown-it-py
    parser = MarkdownParser()
    tokens = parser.parse(text)

    # 3. Build line offset map
    line_offsets = build_line_offset_map(text)

    # 4. Extract math blocks
    blocks: List[ParsedMathBlock] = []

    for token in tokens:
        # math_block = display math ($$...$$)
        # math_inline = inline math ($...$)
        if token.type not in ('math_block', 'math_inline'):
            continue

        # Token.map gives [start_line, end_line) - end is exclusive
        # May be None for inline math
        if token.map:
            start_line = token.map[0]
            end_line = token.map[1]
        else:
            # For inline math without map, estimate from content position
            # This is a fallback - dollarmath usually provides map
            start_line = 0
            end_line = 1

        # Calculate document character offsets
        doc_start_offset = line_to_char_offset(start_line, line_offsets)

        # For display math blocks, we need to find the actual $$ position
        # markdown-it-py's token.content is the inner content (without $$)
        inner_content = token.content

        # Determine delimiter and reconstruct full content
        is_display = token.type == 'math_block'
        delimiter = '$$' if is_display else '$'
        delimiter_len = len(delimiter)

        # Find the actual position of this math block in the text
        # Start from the line offset and search for the delimiter
        search_start = doc_start_offset
        actual_start = text.find(delimiter, search_start)

        if actual_start == -1:
            # Fallback: use line offset
            actual_start = doc_start_offset

        # Calculate end position
        if is_display:
            # Display math: $$content$$
            # The content may span multiple lines, need to find closing $$
            content_start = actual_start + delimiter_len
            closing_pos = text.find('$$', content_start)
            if closing_pos != -1:
                actual_end = closing_pos + delimiter_len
            else:
                actual_end = actual_start + delimiter_len + len(inner_content) + delimiter_len
        else:
            # Inline math: $content$
            actual_end = actual_start + delimiter_len + len(inner_content) + delimiter_len

        full_content = text[actual_start:actual_end]

        # 5. Parse LaTeX content with pylatexenc
        latex_nodes = parse_latex_content(inner_content)

        blocks.append(ParsedMathBlock(
            content=full_content,
            inner_content=inner_content,
            is_display=is_display,
            doc_start_offset=actual_start,
            doc_end_offset=actual_end,
            start_line=start_line,
            end_line=end_line,
            latex_nodes=latex_nodes
        ))

    return blocks


def get_latex_node_positions(block: ParsedMathBlock) -> List[LaTeXPosition]:
    """Extract position information from LaTeX nodes in a math block.

    Args:
        block: A ParsedMathBlock with latex_nodes populated

    Returns:
        List of LaTeXPosition objects with absolute document positions
    """
    positions: List[LaTeXPosition] = []

    # Offset to add to LaTeX positions to get document positions
    # Account for opening delimiter
    delimiter_len = 2 if block.is_display else 1
    base_offset = block.doc_start_offset + delimiter_len

    def extract_from_node(node: Any) -> None:
        """Recursively extract positions from node and children."""
        if node is None:
            return

        # Get node type name
        node_type = type(node).__name__.replace('Latex', '').replace('Node', '').lower()

        # Get position attributes
        pos = getattr(node, 'pos', None)
        pos_end = getattr(node, 'pos_end', None)

        # Handle older pylatexenc that uses 'len' instead of 'pos_end'
        if pos_end is None and pos is not None:
            node_len = getattr(node, 'len', None)
            if node_len is not None:
                pos_end = pos + node_len

        if pos is not None and pos_end is not None:
            # Get content - different nodes have different attributes
            content = ''
            if hasattr(node, 'chars'):
                content = node.chars
            elif hasattr(node, 'macroname'):
                content = '\\' + node.macroname
            elif hasattr(node, 'latex_verbatim'):
                content = node.latex_verbatim()

            positions.append(LaTeXPosition(
                pos=pos,
                pos_end=pos_end,
                node_type=node_type,
                content=content
            ))

        # Recurse into children
        if hasattr(node, 'nodelist') and node.nodelist:
            for child in node.nodelist:
                extract_from_node(child)
        if hasattr(node, 'nodeargd') and node.nodeargd:
            if hasattr(node.nodeargd, 'argnlist') and node.nodeargd.argnlist:
                for arg in node.nodeargd.argnlist:
                    if arg is not None:
                        if hasattr(arg, 'nodelist') and arg.nodelist:
                            for child in arg.nodelist:
                                extract_from_node(child)

    for node in block.latex_nodes:
        extract_from_node(node)

    return positions
