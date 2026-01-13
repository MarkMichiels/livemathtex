"""Tests for calculation parser with character-level spans."""

import pytest
from livemathtex.parser.calculation_parser import (
    Span,
    ParsedCalculation,
    parse_calculation_line,
    parse_math_block_calculations,
)
from livemathtex.parser.markdown_parser import extract_math_blocks


class TestSpan:
    """Tests for Span dataclass."""

    def test_span_extract_returns_correct_substring(self):
        """Span.extract() returns correct substring."""
        text = "hello world"
        span = Span(0, 5)
        assert span.extract(text) == "hello"

    def test_span_extract_middle(self):
        """Span.extract() works for middle of string."""
        text = "hello world"
        span = Span(6, 11)
        assert span.extract(text) == "world"

    def test_span_extract_single_char(self):
        """Span.extract() works for single character."""
        text = "abc"
        span = Span(1, 2)
        assert span.extract(text) == "b"


class TestParseCalculationLine:
    """Tests for parse_calculation_line function."""

    # === Operator Tests ===

    def test_unit_definition_triple_equals(self):
        """=== operator parsed correctly."""
        calc = parse_calculation_line("kWh === 3600000 * J", 0)
        assert calc.operation == "==="
        assert calc.lhs == "kWh"
        assert calc.rhs == "3600000 * J"

    def test_simple_assignment(self):
        """Simple := assignment parsed correctly."""
        calc = parse_calculation_line("x := 5", 0)
        assert calc.operation == ":="
        assert calc.lhs == "x"
        assert calc.rhs == "5"

    def test_evaluation(self):
        """== evaluation parsed correctly."""
        calc = parse_calculation_line("x + y == 15", 0)
        assert calc.operation == "=="
        assert calc.lhs == "x + y"
        assert calc.result == "15"

    def test_symbolic(self):
        """=> symbolic parsed correctly."""
        calc = parse_calculation_line("\\frac{a}{b} => simplified", 0)
        assert calc.operation == "=>"
        assert calc.lhs == "\\frac{a}{b}"
        assert calc.result == "simplified"

    def test_combined_assignment_eval(self):
        """Combined := and == parsed correctly."""
        calc = parse_calculation_line("x := 5 == 5", 0)
        assert calc.operation == ":=_=="
        assert calc.lhs == "x"
        assert calc.rhs == "5"
        assert calc.result == "5"

    # === Position Accuracy Tests ===

    def test_operator_span_points_to_operator(self):
        """Operator span points to exact operator position."""
        line = "x := 5"
        calc = parse_calculation_line(line, 0)
        assert line[calc.operator_span.start:calc.operator_span.end] == ":="

    def test_lhs_span_correct(self):
        """LHS span correctly delimits content."""
        line = "variable := value"
        calc = parse_calculation_line(line, 0)
        assert line[calc.lhs_span.start:calc.lhs_span.end] == "variable"

    def test_rhs_span_correct(self):
        """RHS span correctly delimits content."""
        line = "x := some_expression"
        calc = parse_calculation_line(line, 0)
        assert line[calc.rhs_span.start:calc.rhs_span.end] == "some_expression"

    def test_spans_with_offset(self):
        """Spans account for line_start_offset."""
        calc = parse_calculation_line("x := 5", 100)
        assert calc.operator_span.start == 102  # 100 + 2 (after "x ")
        assert calc.lhs_span.start == 100

    def test_triple_equals_operator_span(self):
        """=== operator span is 3 characters."""
        line = "kWh === J"
        calc = parse_calculation_line(line, 0)
        assert calc.operator_span.end - calc.operator_span.start == 3
        assert line[calc.operator_span.start:calc.operator_span.end] == "==="

    def test_eval_result_span(self):
        """Result span for == is correct."""
        line = "x == 42"
        calc = parse_calculation_line(line, 0)
        assert line[calc.result_span.start:calc.result_span.end] == "42"

    # === Unit Hint Tests ===

    def test_inline_unit_hint_extracted(self):
        """Inline [unit] hint extracted."""
        calc = parse_calculation_line("x == 5 [m/s]", 0)
        assert calc.unit_hint == "m/s"
        assert calc.result == "5"

    def test_unit_hint_span_correct(self):
        """Unit hint span is accurate."""
        line = "x == 5 [m/s]"
        calc = parse_calculation_line(line, 0)
        assert line[calc.unit_hint_span.start:calc.unit_hint_span.end] == "[m/s]"

    def test_comment_unit_passed_through(self):
        """Unit from HTML comment is passed through."""
        calc = parse_calculation_line("x == 5", 0, unit_comment="kg")
        assert calc.unit_hint == "kg"

    def test_inline_unit_takes_precedence_over_comment(self):
        """Inline [unit] does NOT override comment (comment wins)."""
        # Based on implementation: comment takes precedence (if unit_match and not unit_hint)
        calc = parse_calculation_line("x == 5 [m/s]", 0, unit_comment="kg")
        assert calc.unit_hint == "kg"  # Comment wins

    def test_combined_assignment_with_unit_hint(self):
        """Combined :=_== with unit hint."""
        calc = parse_calculation_line("x := 5 == 5 [m]", 0)
        assert calc.operation == ":=_=="
        assert calc.unit_hint == "m"
        assert calc.result == "5"

    # === Edge Cases ===

    def test_empty_line_returns_none(self):
        """Empty line returns None."""
        assert parse_calculation_line("", 0) is None
        assert parse_calculation_line("   ", 0) is None

    def test_no_operator_returns_none(self):
        """Line without operators returns None."""
        assert parse_calculation_line("\\frac{1}{2}", 0) is None
        assert parse_calculation_line("x + y", 0) is None

    def test_bare_equals_returns_none(self):
        """Bare = without valid operators returns None (no parseable operators)."""
        # x = 5 has no valid operators (===, :=, ==, =>), so returns None
        calc = parse_calculation_line("x = 5", 0)
        assert calc is None

    def test_bare_equals_with_valid_operator_creates_error(self):
        """Bare = alongside valid operator creates ERROR."""
        # This has := but also bare = later
        calc = parse_calculation_line("x := y = 5", 0)
        assert calc.operation == "ERROR"
        assert "Invalid operator" in calc.error_message

    def test_whitespace_handling(self):
        """Whitespace around operators handled correctly."""
        calc = parse_calculation_line("  x  :=  5  ", 0)
        assert calc.lhs == "x"
        assert calc.rhs == "5"

    def test_complex_expression(self):
        """Complex expressions parsed correctly."""
        calc = parse_calculation_line("\\frac{x^2}{y} + z := a * b", 0)
        assert calc.operation == ":="
        assert calc.lhs == "\\frac{x^2}{y} + z"
        assert calc.rhs == "a * b"


class TestParseMathBlockCalculations:
    """Tests for parse_math_block_calculations function."""

    def test_single_calculation_display_block(self):
        """Single calculation in display block."""
        text = "$$x := 5$$"
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])
        assert len(calcs) == 1
        assert calcs[0].operation == ":="

    def test_multiline_block(self):
        """Multiline block with multiple calculations."""
        text = """$$
x := 5
y := x + 3 == 8
$$"""
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])
        assert len(calcs) == 2
        assert calcs[0].operation == ":="
        assert calcs[1].operation == ":=_=="

    def test_inline_math_single_delimiter(self):
        """Inline math with single $ delimiters."""
        text = "Value is $x := 5$ here"
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])
        assert len(calcs) == 1

    def test_mixed_calc_and_display(self):
        """Block with mix of calculations and pure display."""
        text = """$$
\\text{Header}
x := 5
\\frac{1}{2}
y == 10
$$"""
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])
        # Only lines with operators are parsed
        assert len(calcs) == 2
        assert calcs[0].lhs == "x"
        assert calcs[1].lhs == "y"

    def test_value_comment_creates_value_operation(self):
        """value_comment creates special value operation."""
        text = "$$P_{total}$$"
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0], value_comment="P_total [kW]")
        assert len(calcs) == 1
        assert calcs[0].operation == "value"
        assert calcs[0].lhs == "P_total"
        assert calcs[0].unit_hint == "kW"

    def test_unit_comment_passed_to_calculations(self):
        """unit_comment is passed to individual calculations."""
        text = "$$x := 5$$"
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0], unit_comment="m/s")
        assert calcs[0].unit_hint == "m/s"

    # === Position Integration Tests ===

    def test_spans_are_document_relative(self):
        """Spans are relative to full document, not just block."""
        text = "# Header\n\n$$x := 5$$"
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])

        # Extract from full document using spans
        assert text[calcs[0].lhs_span.start:calcs[0].lhs_span.end] == "x"
        assert text[calcs[0].rhs_span.start:calcs[0].rhs_span.end] == "5"

    def test_multiline_spans_correct(self):
        """Each line in multiline block has correct document offsets."""
        text = """# Test
$$
a := 1
b := 2
$$"""
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])

        # Verify we can extract correct content from document
        assert text[calcs[0].lhs_span.start:calcs[0].lhs_span.end] == "a"
        assert text[calcs[1].lhs_span.start:calcs[1].lhs_span.end] == "b"


class TestIntegration:
    """Integration tests with full documents."""

    def test_full_document_multiple_blocks(self):
        """Full document with multiple math blocks."""
        text = """# Calculations

First block:
$$
x := 10
y := 20
$$

Second block:
$$z := x + y == 30$$
"""
        blocks = extract_math_blocks(text)
        assert len(blocks) == 2

        calcs1 = parse_math_block_calculations(blocks[0])
        calcs2 = parse_math_block_calculations(blocks[1])

        assert len(calcs1) == 2
        assert len(calcs2) == 1
        assert calcs2[0].operation == ":=_=="

    def test_all_operators_in_document(self):
        """Document using all operator types."""
        text = """$$
kWh === 3600000 * J
E := 100
P == 50 [W]
result => simplified
total := E + P == 150
$$"""
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])

        operations = [c.operation for c in calcs]
        assert "===" in operations
        assert ":=" in operations
        assert "==" in operations
        assert "=>" in operations
        assert ":=_==" in operations

    def test_span_extraction_roundtrip(self):
        """All spans extract back to original content."""
        text = """$$
variable_name := complex_expression
result == 42 [kg]
$$"""
        blocks = extract_math_blocks(text)
        calcs = parse_math_block_calculations(blocks[0])

        # First calculation
        assert calcs[0].lhs_span.extract(text) == "variable_name"
        assert calcs[0].rhs_span.extract(text) == "complex_expression"

        # Second calculation
        assert calcs[1].lhs_span.extract(text) == "result"
        assert calcs[1].result_span.extract(text) == "42"
        assert calcs[1].unit_hint_span.extract(text) == "[kg]"
