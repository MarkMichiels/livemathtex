"""Tests for array parsing support (ISS-041)."""

import pytest
from livemathtex.parser.expression_tokenizer import ExpressionTokenizer
from livemathtex.parser.expression_parser import (
    ExpressionParser,
    ArrayNode,
    IndexNode,
    NumberNode,
    VariableNode,
    BinaryOpNode,
    UnitAttachNode,
    ParseError,
)


class TestArrayLiteralParsing:
    """Test parsing of array literal syntax."""

    def test_simple_array(self):
        """Parse [1, 2, 3]."""
        tokens = ExpressionTokenizer("[1, 2, 3]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, ArrayNode)
        assert len(tree.elements) == 3
        assert all(isinstance(e, NumberNode) for e in tree.elements)
        assert tree.elements[0].value == 1.0
        assert tree.elements[1].value == 2.0
        assert tree.elements[2].value == 3.0

    def test_array_with_decimals(self):
        """Parse [15, 30.5, 34]."""
        tokens = ExpressionTokenizer("[15, 30.5, 34]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, ArrayNode)
        assert tree.elements[1].value == 30.5

    def test_empty_array(self):
        """Parse []."""
        tokens = ExpressionTokenizer("[]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, ArrayNode)
        assert len(tree.elements) == 0

    def test_single_element_array(self):
        """Parse [42]."""
        tokens = ExpressionTokenizer("[42]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, ArrayNode)
        assert len(tree.elements) == 1
        assert tree.elements[0].value == 42.0

    def test_array_with_unit(self):
        r"""Parse [15, 30.5]\ \text{mg}."""
        tokens = ExpressionTokenizer(r"[15, 30.5]\ \text{mg}").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, UnitAttachNode)
        assert isinstance(tree.expr, ArrayNode)
        assert tree.unit == "mg"
        assert len(tree.expr.elements) == 2

    def test_array_with_expressions(self):
        """Parse [1 + 2, 3 * 4]."""
        tokens = ExpressionTokenizer("[1 + 2, 3 * 4]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, ArrayNode)
        assert len(tree.elements) == 2
        assert isinstance(tree.elements[0], BinaryOpNode)
        assert tree.elements[0].op == "+"
        assert isinstance(tree.elements[1], BinaryOpNode)
        assert tree.elements[1].op == "*"

    def test_array_with_variables(self):
        """Parse [x, y, z]."""
        tokens = ExpressionTokenizer("[x, y, z]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, ArrayNode)
        assert len(tree.elements) == 3
        assert all(isinstance(e, VariableNode) for e in tree.elements)


class TestIndexAccessParsing:
    """Test parsing of array index access syntax."""

    def test_variable_index(self):
        """Parse arr[0]."""
        tokens = ExpressionTokenizer("arr[0]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, IndexNode)
        assert isinstance(tree.array, VariableNode)
        assert tree.array.name == "arr"
        assert isinstance(tree.index, NumberNode)
        assert tree.index.value == 0.0

    def test_subscript_variable_index(self):
        """Parse gamma_{values}[0]."""
        tokens = ExpressionTokenizer("gamma_{values}[0]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, IndexNode)
        assert isinstance(tree.array, VariableNode)
        assert tree.array.name == "gamma_{values}"

    def test_index_with_expression(self):
        """Parse arr[i + 1]."""
        tokens = ExpressionTokenizer("arr[i + 1]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, IndexNode)
        assert isinstance(tree.index, BinaryOpNode)
        assert tree.index.op == "+"

    def test_chained_index(self):
        """Parse arr[0][1]."""
        tokens = ExpressionTokenizer("arr[0][1]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, IndexNode)
        assert isinstance(tree.array, IndexNode)
        assert tree.index.value == 1.0
        assert tree.array.index.value == 0.0

    def test_literal_index(self):
        """Parse [1, 2, 3][0]."""
        tokens = ExpressionTokenizer("[1, 2, 3][0]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, IndexNode)
        assert isinstance(tree.array, ArrayNode)
        assert tree.index.value == 0.0


class TestArrayInExpressions:
    """Test arrays in larger expressions."""

    def test_scalar_times_array(self):
        r"""Parse V \cdot [1, 2, 3]."""
        tokens = ExpressionTokenizer(r"V \cdot [1, 2, 3]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, BinaryOpNode)
        assert tree.op == "*"
        assert isinstance(tree.left, VariableNode)
        assert isinstance(tree.right, ArrayNode)

    def test_array_times_scalar(self):
        """Parse [1, 2, 3] * 2."""
        tokens = ExpressionTokenizer("[1, 2, 3] * 2").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, BinaryOpNode)
        assert tree.op == "*"
        assert isinstance(tree.left, ArrayNode)
        assert isinstance(tree.right, NumberNode)

    def test_array_plus_array(self):
        """Parse [1, 2] + [3, 4]."""
        tokens = ExpressionTokenizer("[1, 2] + [3, 4]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, BinaryOpNode)
        assert tree.op == "+"
        assert isinstance(tree.left, ArrayNode)
        assert isinstance(tree.right, ArrayNode)

    def test_index_in_expression(self):
        """Parse arr[0] + arr[1]."""
        tokens = ExpressionTokenizer("arr[0] + arr[1]").tokenize()
        tree = ExpressionParser(tokens).parse()
        assert isinstance(tree, BinaryOpNode)
        assert tree.op == "+"
        assert isinstance(tree.left, IndexNode)
        assert isinstance(tree.right, IndexNode)


class TestArrayParseErrors:
    """Test error handling for malformed array syntax."""

    def test_unclosed_bracket(self):
        """Parse [1, 2, 3 should raise error."""
        tokens = ExpressionTokenizer("[1, 2, 3").tokenize()
        with pytest.raises(ParseError) as excinfo:
            ExpressionParser(tokens).parse()
        assert "]" in str(excinfo.value)

    def test_unclosed_index(self):
        """Parse arr[0 should raise error."""
        tokens = ExpressionTokenizer("arr[0").tokenize()
        with pytest.raises(ParseError) as excinfo:
            ExpressionParser(tokens).parse()
        assert "]" in str(excinfo.value)
