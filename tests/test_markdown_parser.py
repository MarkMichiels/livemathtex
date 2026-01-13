"""
Comprehensive tests for the hybrid markdown/LaTeX parser.

Tests cover:
1. Markdown-level: math block detection, code fence exclusion
2. Position accuracy: document offsets, inner content extraction
3. LaTeX parsing: pylatexenc nodes, position tracking
4. Position combination: absolute positions from combined layers
5. Edge cases: empty blocks, special characters, malformed LaTeX
"""

import pytest

from livemathtex.parser.markdown_parser import (
    MarkdownParser,
    ParsedMathBlock,
    build_line_offset_map,
    line_to_char_offset,
    parse_latex_content,
    extract_math_blocks,
    get_latex_node_positions,
)


# =============================================================================
# 1. Markdown-level tests
# =============================================================================

class TestMarkdownParser:
    """Test markdown-it-py integration."""

    def test_parse_returns_tokens(self):
        """Parser returns a list of tokens."""
        parser = MarkdownParser()
        tokens = parser.parse("# Hello\n$$x$$")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_parse_normalizes_line_endings(self):
        """Parser normalizes CRLF to LF."""
        parser = MarkdownParser()
        text_crlf = "# Hello\r\n$$x$$"
        text_lf = "# Hello\n$$x$$"
        tokens_crlf = parser.parse(text_crlf)
        tokens_lf = parser.parse(text_lf)
        # Should produce same structure
        assert len(tokens_crlf) == len(tokens_lf)


class TestMathBlockDetection:
    """Test math block extraction from markdown."""

    def test_single_inline_math(self):
        """Extract single inline $x$ block."""
        blocks = extract_math_blocks("Text $x$ more")
        assert len(blocks) == 1
        assert blocks[0].is_display is False
        assert blocks[0].inner_content == "x"

    def test_single_display_math(self):
        """Extract single display $$x$$ block."""
        blocks = extract_math_blocks("$$x$$")
        assert len(blocks) == 1
        assert blocks[0].is_display is True
        assert blocks[0].inner_content == "x"

    def test_multiline_display_math(self):
        """Extract multiline display block."""
        text = "$$\nx := 5\ny := 10\n$$"
        blocks = extract_math_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].is_display is True
        assert "x := 5" in blocks[0].inner_content
        assert "y := 10" in blocks[0].inner_content

    def test_multiple_math_blocks(self):
        """Extract multiple math blocks from document."""
        text = """# Title
$$a := 1$$

Some text with $inline$ math.

$$
b := 2
$$
"""
        blocks = extract_math_blocks(text)
        assert len(blocks) == 3
        assert blocks[0].is_display is True
        assert blocks[1].is_display is False
        assert blocks[2].is_display is True

    def test_code_fence_exclusion(self):
        """Math inside code fences should NOT be extracted."""
        text = """
```python
# This is code with $$x := 5$$ inside
```

$$y := 10$$
"""
        blocks = extract_math_blocks(text)
        assert len(blocks) == 1
        assert "y := 10" in blocks[0].inner_content

    def test_math_after_code_block(self):
        """Math block after code fence should be extracted."""
        text = """```
code
```

$$z := 20$$"""
        blocks = extract_math_blocks(text)
        assert len(blocks) == 1
        assert "z := 20" in blocks[0].inner_content


# =============================================================================
# 2. Position accuracy tests
# =============================================================================

class TestLineOffsetMap:
    """Test line offset map building."""

    def test_empty_text(self):
        """Empty text has single offset at 0."""
        offsets = build_line_offset_map("")
        assert offsets == [0]

    def test_single_line(self):
        """Single line without newline."""
        offsets = build_line_offset_map("hello")
        assert offsets == [0]

    def test_multiple_lines(self):
        """Multiple lines have correct offsets."""
        # "abc\ndef\nghi" = 3 chars + newline + 3 chars + newline + 3 chars
        offsets = build_line_offset_map("abc\ndef\nghi")
        assert offsets == [0, 4, 8]

    def test_line_to_char_conversion(self):
        """Line numbers convert to correct char offsets."""
        offsets = [0, 4, 8]
        assert line_to_char_offset(0, offsets) == 0
        assert line_to_char_offset(1, offsets) == 4
        assert line_to_char_offset(2, offsets) == 8

    def test_line_beyond_range(self):
        """Line beyond range returns last offset."""
        offsets = [0, 4, 8]
        assert line_to_char_offset(10, offsets) == 8


class TestDocumentPositions:
    """Test document-level position tracking."""

    def test_content_matches_slice(self):
        """text[start:end] should equal content."""
        text = "# Test\n$$x := 5$$\nMore text"
        blocks = extract_math_blocks(text)
        assert len(blocks) == 1
        b = blocks[0]
        assert text[b.doc_start_offset:b.doc_end_offset] == b.content

    def test_inner_content_without_delimiters(self):
        """inner_content should not include $$ delimiters."""
        text = "$$hello$$"
        blocks = extract_math_blocks(text)
        assert blocks[0].inner_content == "hello"
        assert blocks[0].content == "$$hello$$"

    def test_multiline_block_positions(self):
        """Multiline blocks have correct start/end."""
        text = "# Header\n$$\nx := 5\n$$\n"
        blocks = extract_math_blocks(text)
        b = blocks[0]
        assert text[b.doc_start_offset:b.doc_end_offset] == b.content
        assert "$$" in b.content
        assert "x := 5" in b.content

    def test_math_at_document_start(self):
        """Math at very start of document."""
        text = "$$x$$\ntext"
        blocks = extract_math_blocks(text)
        assert blocks[0].doc_start_offset == 0
        assert blocks[0].content == "$$x$$"

    def test_math_at_document_end(self):
        """Math at end of document (no trailing newline)."""
        # Display math needs blank line separation in markdown
        text = "text\n\n$$x$$"
        blocks = extract_math_blocks(text)
        assert len(blocks) == 1
        assert text[blocks[0].doc_start_offset:blocks[0].doc_end_offset] == "$$x$$"


# =============================================================================
# 3. LaTeX parsing tests
# =============================================================================

class TestLatexParsing:
    """Test pylatexenc integration."""

    def test_latex_nodes_populated(self):
        """latex_nodes should be populated for math blocks."""
        blocks = extract_math_blocks("$$x := 5$$")
        assert blocks[0].latex_nodes is not None
        assert len(blocks[0].latex_nodes) > 0

    def test_simple_expression(self):
        """Parse simple expression x := 5."""
        nodes = parse_latex_content("x := 5")
        assert len(nodes) > 0

    def test_macro_parsing(self):
        """Parse LaTeX macros like \\frac{a}{b}."""
        nodes = parse_latex_content(r"\frac{a}{b}")
        assert len(nodes) > 0
        # Should find the frac macro
        macro_names = [n.macroname for n in nodes if hasattr(n, 'macroname')]
        assert 'frac' in macro_names

    def test_text_macro(self):
        """Parse \\text{kg} macro."""
        nodes = parse_latex_content(r"\text{kg}")
        assert len(nodes) > 0
        macro_names = [n.macroname for n in nodes if hasattr(n, 'macroname')]
        assert 'text' in macro_names

    def test_malformed_latex_tolerant(self):
        """Malformed LaTeX should not crash with tolerant_parsing."""
        # Missing closing brace
        nodes = parse_latex_content(r"\frac{a}{b")
        # Should return something, not crash
        assert nodes is not None

    def test_empty_content(self):
        """Empty LaTeX content returns empty list."""
        nodes = parse_latex_content("")
        assert nodes == []


# =============================================================================
# 4. Position combination tests
# =============================================================================

class TestPositionCombination:
    """Test combining document and LaTeX positions."""

    def test_latex_position_extraction(self):
        """Extract positions from LaTeX nodes."""
        blocks = extract_math_blocks("$$x := 5$$")
        positions = get_latex_node_positions(blocks[0])
        assert len(positions) > 0

    def test_find_chars_position(self):
        """Find position of character nodes."""
        blocks = extract_math_blocks("$$x := 5$$")
        positions = get_latex_node_positions(blocks[0])
        # Should find 'chars' type nodes
        char_positions = [p for p in positions if p.node_type == 'chars']
        assert len(char_positions) > 0

    def test_absolute_position_calculation(self):
        """Verify absolute position = doc_offset + delimiter + latex_pos."""
        text = "# Header\n$$x := 5$$"
        blocks = extract_math_blocks(text)
        b = blocks[0]

        # The inner content starts after $$
        delimiter_len = 2
        inner_start = b.doc_start_offset + delimiter_len

        # Verify the inner content matches
        assert text[inner_start:inner_start + len(b.inner_content)] == b.inner_content


# =============================================================================
# 5. Edge cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_math_block(self):
        """Empty display math block $$$$."""
        blocks = extract_math_blocks("$$$$")
        assert len(blocks) == 1
        assert blocks[0].inner_content == ""

    def test_dollar_in_text(self):
        """Dollar signs in regular text (not math)."""
        # Single $ followed by space is not math
        text = "Price is $ 5 or $10"
        blocks = extract_math_blocks(text)
        # Depends on dollarmath parsing - might or might not match
        # The key is it shouldn't crash
        assert isinstance(blocks, list)

    def test_nested_braces(self):
        """Nested braces in LaTeX."""
        blocks = extract_math_blocks(r"$$\frac{\frac{a}{b}}{c}$$")
        assert len(blocks) == 1
        assert r"\frac" in blocks[0].inner_content

    def test_special_characters(self):
        """Special characters in math."""
        blocks = extract_math_blocks(r"$$\alpha + \beta = \gamma$$")
        assert len(blocks) == 1
        nodes = blocks[0].latex_nodes
        macro_names = [n.macroname for n in nodes if hasattr(n, 'macroname')]
        assert 'alpha' in macro_names or len(nodes) > 0

    def test_crlf_normalization(self):
        """CRLF line endings are normalized."""
        text = "$$\r\nx := 5\r\n$$"
        blocks = extract_math_blocks(text)
        assert len(blocks) == 1
        # Inner content should have LF, not CRLF
        assert '\r' not in blocks[0].inner_content

    def test_multiple_inline_same_line(self):
        """Multiple inline math on same line."""
        text = "Let $x = 1$ and $y = 2$ be values"
        blocks = extract_math_blocks(text)
        assert len(blocks) == 2
        assert blocks[0].inner_content == "x = 1"
        assert blocks[1].inner_content == "y = 2"


# =============================================================================
# Integration test
# =============================================================================

class TestIntegration:
    """Full integration test with realistic document."""

    def test_realistic_document(self):
        """Parse a realistic livemathtex document."""
        doc = """# Engineering Calculations

This document demonstrates unit-aware calculations.

## Variables

$$
g := 9.81
$$

The acceleration is $g == 9.81$.

## Calculation

```python
# This is NOT math: $$fake$$
```

$$
F := m \\cdot g
$$

Force calculation: $F == m \\cdot g$
"""
        blocks = extract_math_blocks(doc)

        # Should find 4 math blocks (not the one in code fence)
        assert len(blocks) == 4

        # Verify positions are valid
        for b in blocks:
            # Content slice should match
            assert doc[b.doc_start_offset:b.doc_end_offset] == b.content

            # LaTeX nodes should be populated
            assert b.latex_nodes is not None

        # First block should be display math with g := 9.81
        assert blocks[0].is_display is True
        assert "g := 9.81" in blocks[0].inner_content

        # Second block should be inline
        assert blocks[1].is_display is False
