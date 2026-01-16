"""Tests for array tokenization support (ISS-041)."""

import pytest
from livemathtex.parser.expression_tokenizer import ExpressionTokenizer, TokenType


class TestArrayLiteralTokenization:
    """Test tokenization of array literal syntax."""

    def test_simple_array(self):
        """Tokenize [1, 2, 3]."""
        tokens = ExpressionTokenizer("[1, 2, 3]").tokenize()
        # [, 1, ,, 2, ,, 3, ], EOF
        assert len(tokens) == 8
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[0].value == "["
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "1"
        assert tokens[2].type == TokenType.OPERATOR
        assert tokens[2].value == ","
        assert tokens[3].type == TokenType.NUMBER
        assert tokens[3].value == "2"
        assert tokens[4].type == TokenType.OPERATOR
        assert tokens[4].value == ","
        assert tokens[5].type == TokenType.NUMBER
        assert tokens[5].value == "3"
        assert tokens[6].type == TokenType.RBRACKET
        assert tokens[6].value == "]"
        assert tokens[7].type == TokenType.EOF

    def test_array_with_decimals(self):
        """Tokenize [15, 30.5, 34]."""
        tokens = ExpressionTokenizer("[15, 30.5, 34]").tokenize()
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].value == "15"
        assert tokens[3].value == "30.5"
        assert tokens[5].value == "34"
        assert tokens[6].type == TokenType.RBRACKET

    def test_array_with_unit(self):
        r"""Tokenize [15, 30.5]\ \text{mg}."""
        tokens = ExpressionTokenizer(r"[15, 30.5]\ \text{mg}").tokenize()
        # [, 15, ,, 30.5, ], \text{mg}, EOF
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[4].type == TokenType.RBRACKET
        assert tokens[5].type == TokenType.UNIT
        assert tokens[5].value == "mg"

    def test_empty_array(self):
        """Tokenize []."""
        tokens = ExpressionTokenizer("[]").tokenize()
        assert len(tokens) == 3  # [, ], EOF
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET


class TestArrayIndexTokenization:
    """Test tokenization of array index access syntax."""

    def test_variable_index(self):
        """Tokenize arr[0]."""
        tokens = ExpressionTokenizer("arr[0]").tokenize()
        # arr, [, 0, ], EOF
        assert len(tokens) == 5
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "arr"
        assert tokens[1].type == TokenType.LBRACKET
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "0"
        assert tokens[3].type == TokenType.RBRACKET
        assert tokens[4].type == TokenType.EOF

    def test_subscript_variable_index(self):
        """Tokenize gamma_{values}[0]."""
        tokens = ExpressionTokenizer("gamma_{values}[0]").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "gamma_{values}"
        assert tokens[1].type == TokenType.LBRACKET
        assert tokens[2].value == "0"
        assert tokens[3].type == TokenType.RBRACKET

    def test_index_expression(self):
        """Tokenize arr[i + 1]."""
        tokens = ExpressionTokenizer("arr[i + 1]").tokenize()
        # arr, [, i, +, 1, ], EOF
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[1].type == TokenType.LBRACKET
        assert tokens[2].type == TokenType.VARIABLE
        assert tokens[2].value == "i"
        assert tokens[3].type == TokenType.OPERATOR
        assert tokens[3].value == "+"
        assert tokens[4].type == TokenType.NUMBER
        assert tokens[5].type == TokenType.RBRACKET


class TestArrayInExpressions:
    """Test arrays in larger expressions."""

    def test_array_multiplication(self):
        r"""Tokenize V \cdot [1, 2]."""
        tokens = ExpressionTokenizer(r"V \cdot [1, 2]").tokenize()
        # V, \cdot, [, 1, ,, 2, ], EOF
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[1].type == TokenType.OPERATOR
        assert tokens[1].value == "\\cdot"
        assert tokens[2].type == TokenType.LBRACKET
        assert tokens[6].type == TokenType.RBRACKET

    def test_nested_brackets_not_allowed(self):
        """Verify [[1], [2]] tokenizes correctly."""
        # Nested arrays not supported in v1, but should tokenize
        tokens = ExpressionTokenizer("[[1], [2]]").tokenize()
        types = [t.type for t in tokens[:-1]]  # Exclude EOF
        assert types.count(TokenType.LBRACKET) == 3
        assert types.count(TokenType.RBRACKET) == 3
