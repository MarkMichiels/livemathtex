"""Tests for the expression parser.

This module tests ExpressionParser which converts tokens from ExpressionTokenizer
into an expression tree suitable for Pint evaluation.

TDD: RED phase - all tests should fail until parser is implemented.
"""

import pytest

from livemathtex.parser.expression_tokenizer import ExpressionTokenizer, Token, TokenType
from livemathtex.parser.expression_parser import (
    ExpressionParser,
    ExprNode,
    NumberNode,
    VariableNode,
    BinaryOpNode,
    UnaryOpNode,
    FracNode,
    UnitAttachNode,
    ParseError,
)


def parse(latex: str) -> ExprNode:
    """Helper to tokenize and parse a LaTeX expression."""
    tokens = ExpressionTokenizer(latex).tokenize()
    return ExpressionParser(tokens).parse()


# =============================================================================
# ExprNode Classes
# =============================================================================


class TestExprNodeClasses:
    """Test that all ExprNode dataclasses are defined correctly."""

    def test_number_node_fields(self):
        """NumberNode has value field."""
        node = NumberNode(3.14)
        assert node.value == 3.14

    def test_variable_node_fields(self):
        """VariableNode has name field."""
        node = VariableNode("x")
        assert node.name == "x"

    def test_binary_op_node_fields(self):
        """BinaryOpNode has op, left, right fields."""
        left = NumberNode(1)
        right = NumberNode(2)
        node = BinaryOpNode("+", left, right)
        assert node.op == "+"
        assert node.left == left
        assert node.right == right

    def test_unary_op_node_fields(self):
        """UnaryOpNode has op, operand fields."""
        operand = NumberNode(5)
        node = UnaryOpNode("-", operand)
        assert node.op == "-"
        assert node.operand == operand

    def test_frac_node_fields(self):
        """FracNode has numerator, denominator fields."""
        num = NumberNode(1)
        denom = NumberNode(2)
        node = FracNode(num, denom)
        assert node.numerator == num
        assert node.denominator == denom

    def test_unit_attach_node_fields(self):
        """UnitAttachNode has expr, unit fields."""
        expr = NumberNode(5)
        node = UnitAttachNode(expr, "kg")
        assert node.expr == expr
        assert node.unit == "kg"

    def test_node_equality(self):
        """Nodes with same values are equal."""
        assert NumberNode(5) == NumberNode(5)
        assert VariableNode("x") == VariableNode("x")
        assert NumberNode(5) != NumberNode(6)
        assert VariableNode("x") != VariableNode("y")


# =============================================================================
# Number Parsing
# =============================================================================


class TestNumberParsing:
    """Test parsing of numeric literals."""

    def test_integer(self):
        """Parse integer."""
        result = parse("5")
        assert isinstance(result, NumberNode)
        assert result.value == 5.0

    def test_decimal(self):
        """Parse decimal number."""
        result = parse("3.14")
        assert isinstance(result, NumberNode)
        assert result.value == 3.14

    def test_scientific_notation(self):
        """Parse scientific notation."""
        result = parse("1e6")
        assert isinstance(result, NumberNode)
        assert result.value == 1000000.0

    def test_scientific_notation_negative_exponent(self):
        """Parse scientific notation with negative exponent."""
        result = parse("2.5e-3")
        assert isinstance(result, NumberNode)
        assert result.value == 0.0025

    def test_zero(self):
        """Parse zero."""
        result = parse("0")
        assert isinstance(result, NumberNode)
        assert result.value == 0.0


# =============================================================================
# Variable Parsing
# =============================================================================


class TestVariableParsing:
    """Test parsing of variable names."""

    def test_single_letter(self):
        """Parse single letter variable."""
        result = parse("x")
        assert isinstance(result, VariableNode)
        assert result.name == "x"

    def test_subscript_braces(self):
        """Parse variable with subscript in braces."""
        result = parse("E_{26}")
        assert isinstance(result, VariableNode)
        assert result.name == "E_{26}"

    def test_subscript_multi_letter(self):
        """Parse multi-letter variable with subscript."""
        result = parse("PPE_{eff}")
        assert isinstance(result, VariableNode)
        assert result.name == "PPE_{eff}"

    def test_superscript_braces(self):
        """Parse superscript in braces as exponentiation.

        R^{2} parses as: R raised to the power 2 (BinaryOpNode)
        This is correct for evaluations where ^ means exponentiation.
        """
        result = parse("R^{2}")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "^"
        assert isinstance(result.left, VariableNode)
        assert result.left.name == "R"
        assert isinstance(result.right, NumberNode)
        assert result.right.value == 2.0

    def test_superscript_simple(self):
        """Parse simple superscript as exponentiation.

        x^2 parses as: x raised to the power 2 (BinaryOpNode)
        This is correct for evaluations where ^ means exponentiation.
        """
        result = parse("x^2")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "^"
        assert isinstance(result.left, VariableNode)
        assert result.left.name == "x"
        assert isinstance(result.right, NumberNode)
        assert result.right.value == 2.0

    def test_greek_letter(self):
        """Parse Greek letter."""
        result = parse(r"\alpha")
        assert isinstance(result, VariableNode)
        assert result.name == r"\alpha"

    def test_greek_letter_mu(self):
        """Parse mu (common in units)."""
        result = parse(r"\mu")
        assert isinstance(result, VariableNode)
        assert result.name == r"\mu"


# =============================================================================
# Unit Attachment
# =============================================================================


class TestUnitAttachment:
    """Test parsing of units attached to expressions."""

    def test_number_with_unit(self):
        """Parse number with unit."""
        result = parse(r"5 \text{kg}")
        assert isinstance(result, UnitAttachNode)
        assert isinstance(result.expr, NumberNode)
        assert result.expr.value == 5.0
        assert result.unit == "kg"

    def test_variable_with_unit(self):
        """Parse variable with unit."""
        result = parse(r"m \text{g}")
        assert isinstance(result, UnitAttachNode)
        assert isinstance(result.expr, VariableNode)
        assert result.expr.name == "m"
        assert result.unit == "g"

    def test_unit_mathrm(self):
        """Parse unit in mathrm."""
        result = parse(r"100 \mathrm{MWh}")
        assert isinstance(result, UnitAttachNode)
        assert result.unit == "MWh"

    def test_compound_unit(self):
        """Parse compound unit."""
        result = parse(r"10 \text{kg/m^3}")
        assert isinstance(result, UnitAttachNode)
        assert result.unit == "kg/m^3"


# =============================================================================
# Binary Operators
# =============================================================================


class TestBinaryOperators:
    """Test parsing of binary operators."""

    def test_addition(self):
        """Parse addition."""
        result = parse("a + b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "+"
        assert isinstance(result.left, VariableNode)
        assert isinstance(result.right, VariableNode)

    def test_subtraction(self):
        """Parse subtraction."""
        result = parse("a - b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "-"

    def test_multiplication_asterisk(self):
        """Parse multiplication with asterisk."""
        result = parse("a * b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "*"

    def test_multiplication_cdot(self):
        """Parse multiplication with cdot."""
        result = parse(r"a \cdot b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "*"

    def test_multiplication_times(self):
        """Parse multiplication with times."""
        result = parse(r"a \times b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "*"

    def test_division(self):
        """Parse division."""
        result = parse("a / b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "/"

    def test_power(self):
        """Parse power (from operator token, not variable superscript)."""
        # Note: x^2 as single token is a variable, x ^ 2 with spaces is power
        result = parse("a ^ b")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "^"


# =============================================================================
# Operator Precedence
# =============================================================================


class TestOperatorPrecedence:
    """Test correct operator precedence (PEMDAS)."""

    def test_add_then_multiply(self):
        """Multiplication has higher precedence than addition: a + b * c."""
        result = parse("a + b * c")
        # Should be: a + (b * c)
        assert isinstance(result, BinaryOpNode)
        assert result.op == "+"
        assert isinstance(result.left, VariableNode)
        assert result.left.name == "a"
        assert isinstance(result.right, BinaryOpNode)
        assert result.right.op == "*"

    def test_multiply_then_add(self):
        """a * b + c should be (a * b) + c."""
        result = parse("a * b + c")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "+"
        assert isinstance(result.left, BinaryOpNode)
        assert result.left.op == "*"
        assert isinstance(result.right, VariableNode)

    def test_power_right_associative(self):
        """Power is right associative: a ^ b ^ c = a ^ (b ^ c)."""
        result = parse("a ^ b ^ c")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "^"
        assert isinstance(result.left, VariableNode)
        assert result.left.name == "a"
        # Right side should be b ^ c
        assert isinstance(result.right, BinaryOpNode)
        assert result.right.op == "^"
        assert result.right.left.name == "b"
        assert result.right.right.name == "c"

    def test_power_higher_than_multiply(self):
        """a * b ^ c should be a * (b ^ c)."""
        result = parse("a * b ^ c")
        assert isinstance(result, BinaryOpNode)
        assert result.op == "*"
        assert isinstance(result.right, BinaryOpNode)
        assert result.right.op == "^"

    def test_full_precedence_chain(self):
        """a + b * c ^ d should nest correctly."""
        result = parse("a + b * c ^ d")
        # Should be: a + (b * (c ^ d))
        assert result.op == "+"
        assert result.left.name == "a"
        assert result.right.op == "*"
        assert result.right.left.name == "b"
        assert result.right.right.op == "^"

    def test_division_same_precedence_as_multiply(self):
        """Division has same precedence as multiplication, left associative."""
        result = parse("a / b * c")
        # Should be: (a / b) * c
        assert result.op == "*"
        assert result.left.op == "/"

    def test_subtraction_same_precedence_as_add(self):
        """Subtraction has same precedence as addition, left associative."""
        result = parse("a - b + c")
        # Should be: (a - b) + c
        assert result.op == "+"
        assert result.left.op == "-"


# =============================================================================
# Parentheses
# =============================================================================


class TestParentheses:
    """Test parentheses override precedence."""

    def test_parentheses_override_precedence(self):
        """(a + b) * c puts addition first."""
        result = parse("(a + b) * c")
        assert result.op == "*"
        assert result.left.op == "+"

    def test_latex_left_right_parens(self):
        r"""Parse \left( ... \right) parentheses."""
        result = parse(r"\left( a + b \right) * c")
        assert result.op == "*"
        assert result.left.op == "+"

    def test_nested_parentheses(self):
        """Parse nested parentheses."""
        result = parse("((a + b))")
        assert result.op == "+"

    def test_deeply_nested(self):
        """Parse deeply nested expression."""
        result = parse("(((a)))")
        assert isinstance(result, VariableNode)
        assert result.name == "a"

    def test_complex_parentheses(self):
        """Complex expression with multiple parentheses."""
        result = parse("(a + b) * (c + d)")
        assert result.op == "*"
        assert result.left.op == "+"
        assert result.right.op == "+"


# =============================================================================
# Fractions
# =============================================================================


class TestFractions:
    """Test parsing of LaTeX fractions."""

    def test_simple_fraction(self):
        """Parse simple fraction."""
        result = parse(r"\frac{a}{b}")
        assert isinstance(result, FracNode)
        assert isinstance(result.numerator, VariableNode)
        assert result.numerator.name == "a"
        assert isinstance(result.denominator, VariableNode)
        assert result.denominator.name == "b"

    def test_numeric_fraction(self):
        """Parse numeric fraction."""
        result = parse(r"\frac{1}{2}")
        assert isinstance(result, FracNode)
        assert result.numerator.value == 1.0
        assert result.denominator.value == 2.0

    def test_fraction_with_expressions(self):
        """Parse fraction with expressions in numerator/denominator."""
        result = parse(r"\frac{a + b}{c * d}")
        assert isinstance(result, FracNode)
        assert result.numerator.op == "+"
        assert result.denominator.op == "*"

    def test_nested_fractions(self):
        """Parse nested fractions."""
        result = parse(r"\frac{\frac{a}{b}}{c}")
        assert isinstance(result, FracNode)
        assert isinstance(result.numerator, FracNode)
        assert isinstance(result.denominator, VariableNode)

    def test_fraction_in_expression(self):
        """Fraction as part of larger expression."""
        result = parse(r"\frac{1}{2} + x")
        assert result.op == "+"
        assert isinstance(result.left, FracNode)
        assert isinstance(result.right, VariableNode)

    def test_fraction_times_variable(self):
        """Fraction multiplied by variable."""
        result = parse(r"\frac{1}{2} \cdot x")
        assert result.op == "*"
        assert isinstance(result.left, FracNode)


# =============================================================================
# Unary Minus
# =============================================================================


class TestUnaryMinus:
    """Test parsing of unary minus operator."""

    def test_negative_number(self):
        """Parse negative number."""
        result = parse("-5")
        assert isinstance(result, UnaryOpNode)
        assert result.op == "-"
        assert isinstance(result.operand, NumberNode)
        assert result.operand.value == 5.0

    def test_negative_variable(self):
        """Parse negative variable."""
        result = parse("-x")
        assert isinstance(result, UnaryOpNode)
        assert result.op == "-"
        assert isinstance(result.operand, VariableNode)

    def test_negative_parentheses(self):
        """Parse negative parenthesized expression."""
        result = parse("-(a + b)")
        assert isinstance(result, UnaryOpNode)
        assert result.op == "-"
        assert isinstance(result.operand, BinaryOpNode)
        assert result.operand.op == "+"

    def test_subtract_negative(self):
        """Parse a + -b (add negative)."""
        result = parse("a + -b")
        assert result.op == "+"
        assert isinstance(result.right, UnaryOpNode)
        assert result.right.op == "-"

    def test_double_negative(self):
        """Parse double negative."""
        result = parse("--x")
        assert isinstance(result, UnaryOpNode)
        assert isinstance(result.operand, UnaryOpNode)
        assert result.operand.operand.name == "x"

    def test_negative_in_multiplication(self):
        """Parse a * -b."""
        result = parse("a * -b")
        assert result.op == "*"
        assert isinstance(result.right, UnaryOpNode)


# =============================================================================
# Complex Expressions
# =============================================================================


class TestComplexExpressions:
    """Test parsing of complex real-world expressions."""

    def test_quadratic_formula_part(self):
        """Parse part of quadratic formula."""
        result = parse("a ^ 2 + b ^ 2")
        assert result.op == "+"
        # Note: these are variable tokens with ^2 as part of name
        # OR if a ^ 2 uses separate tokens, then BinaryOpNode
        # Depends on tokenizer output

    def test_fraction_times_expression(self):
        """Parse fraction times complex expression."""
        result = parse(r"\frac{1}{2} \cdot (a + b)")
        assert result.op == "*"
        assert isinstance(result.left, FracNode)
        assert isinstance(result.right, BinaryOpNode)

    def test_rate_calculation(self):
        """Parse typical rate calculation."""
        result = parse(r"10 \cdot 365")
        assert result.op == "*"
        assert result.left.value == 10.0
        assert result.right.value == 365.0

    def test_unit_conversion_pattern(self):
        """Parse pattern with units."""
        result = parse(r"m \cdot 1000")
        assert result.op == "*"
        assert result.left.name == "m"
        assert result.right.value == 1000.0


# =============================================================================
# Error Handling
# =============================================================================


class TestErrorHandling:
    """Test parser error handling."""

    def test_empty_expression(self):
        """Empty expression raises ParseError."""
        with pytest.raises(ParseError):
            parse("")

    def test_unclosed_parenthesis(self):
        """Unclosed parenthesis raises ParseError."""
        with pytest.raises(ParseError):
            parse("(a + b")

    def test_missing_operand_after_operator(self):
        """Missing operand after operator raises ParseError."""
        with pytest.raises(ParseError):
            parse("a +")

    def test_missing_operand_before_operator(self):
        """Missing operand before binary operator raises ParseError."""
        with pytest.raises(ParseError):
            parse("+ a")

    def test_incomplete_fraction(self):
        """Incomplete fraction raises ParseError."""
        with pytest.raises(ParseError):
            parse(r"\frac{a}")

    def test_error_has_position_info(self):
        """ParseError should include position information."""
        try:
            parse("(a +")
        except ParseError as e:
            # Error message should mention position or token
            assert "position" in str(e).lower() or "token" in str(e).lower() or "unexpected" in str(e).lower()


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_number(self):
        """Single number is valid expression."""
        result = parse("42")
        assert isinstance(result, NumberNode)

    def test_single_variable(self):
        """Single variable is valid expression."""
        result = parse("x")
        assert isinstance(result, VariableNode)

    def test_whitespace_ignored(self):
        """Whitespace between tokens is ignored."""
        result1 = parse("a + b")
        result2 = parse("a+b")
        # Both should produce same tree structure
        assert result1.op == result2.op == "+"

    def test_multiple_operators_in_row_error(self):
        """Multiple operators in a row should error."""
        with pytest.raises(ParseError):
            parse("a + + b")

    def test_only_operator_error(self):
        """Only an operator should error."""
        with pytest.raises(ParseError):
            parse("+")
