"""Tests for array evaluation support (ISS-041)."""

import pytest
from livemathtex.parser.expression_tokenizer import ExpressionTokenizer
from livemathtex.parser.expression_parser import ExpressionParser
from livemathtex.engine.expression_evaluator import (
    evaluate_expression_tree,
    EvaluationError,
)
from livemathtex.engine.pint_backend import get_unit_registry


def parse(expr: str):
    """Helper to parse expression string."""
    tokens = ExpressionTokenizer(expr).tokenize()
    return ExpressionParser(tokens).parse()


class TestArrayEvaluation:
    """Test evaluation of array literals."""

    def test_simple_array(self):
        """Evaluate [1, 2, 3]."""
        ureg = get_unit_registry()
        tree = parse("[1, 2, 3]")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0].magnitude == 1.0
        assert result[1].magnitude == 2.0
        assert result[2].magnitude == 3.0

    def test_empty_array(self):
        """Evaluate []."""
        ureg = get_unit_registry()
        tree = parse("[]")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_array_with_unit(self):
        r"""Evaluate [15, 30.5]\ \text{mg}."""
        ureg = get_unit_registry()
        tree = parse(r"[15, 30.5]\ \text{mg}")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].magnitude == 15.0
        assert str(result[0].units) == "milligram"
        assert result[1].magnitude == 30.5
        assert str(result[1].units) == "milligram"

    def test_array_with_variables(self):
        """Evaluate [x, y] with x=1, y=2."""
        ureg = get_unit_registry()
        symbols = {
            "x": 1.0 * ureg.dimensionless,
            "y": 2.0 * ureg.dimensionless,
        }
        tree = parse("[x, y]")
        result = evaluate_expression_tree(tree, symbols, ureg)
        assert result[0].magnitude == 1.0
        assert result[1].magnitude == 2.0


class TestIndexAccess:
    """Test evaluation of array index access."""

    def test_array_variable_index(self):
        """Evaluate arr[0] with arr defined."""
        ureg = get_unit_registry()
        symbols = {
            "arr": [1.0 * ureg.m, 2.0 * ureg.m, 3.0 * ureg.m],
        }
        tree = parse("arr[0]")
        result = evaluate_expression_tree(tree, symbols, ureg)
        assert result.magnitude == 1.0
        assert str(result.units) == "meter"

    def test_array_last_element(self):
        """Evaluate arr[2] for 3-element array."""
        ureg = get_unit_registry()
        symbols = {
            "arr": [1.0 * ureg.kg, 2.0 * ureg.kg, 3.0 * ureg.kg],
        }
        tree = parse("arr[2]")
        result = evaluate_expression_tree(tree, symbols, ureg)
        assert result.magnitude == 3.0

    def test_literal_index(self):
        """Evaluate [10, 20, 30][1]."""
        ureg = get_unit_registry()
        tree = parse("[10, 20, 30][1]")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert result.magnitude == 20.0

    def test_index_out_of_bounds(self):
        """Evaluate arr[5] for 3-element array should raise error."""
        ureg = get_unit_registry()
        symbols = {
            "arr": [1.0 * ureg.m, 2.0 * ureg.m, 3.0 * ureg.m],
        }
        tree = parse("arr[5]")
        with pytest.raises(EvaluationError) as excinfo:
            evaluate_expression_tree(tree, symbols, ureg)
        assert "out of bounds" in str(excinfo.value)

    def test_index_non_array(self):
        """Evaluate x[0] where x is scalar should raise error."""
        ureg = get_unit_registry()
        symbols = {"x": 5.0 * ureg.m}
        tree = parse("x[0]")
        with pytest.raises(EvaluationError) as excinfo:
            evaluate_expression_tree(tree, symbols, ureg)
        assert "non-array" in str(excinfo.value).lower()


class TestArrayBroadcasting:
    """Test scalar-array and array-array operations."""

    def test_scalar_times_array(self):
        """Evaluate 2 * [1, 2, 3]."""
        ureg = get_unit_registry()
        tree = parse("2 * [1, 2, 3]")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0].magnitude == 2.0
        assert result[1].magnitude == 4.0
        assert result[2].magnitude == 6.0

    def test_array_times_scalar(self):
        """Evaluate [1, 2, 3] * 2."""
        ureg = get_unit_registry()
        tree = parse("[1, 2, 3] * 2")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert result[0].magnitude == 2.0
        assert result[1].magnitude == 4.0
        assert result[2].magnitude == 6.0

    def test_array_plus_array(self):
        """Evaluate [1, 2] + [3, 4]."""
        ureg = get_unit_registry()
        tree = parse("[1, 2] + [3, 4]")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert len(result) == 2
        assert result[0].magnitude == 4.0
        assert result[1].magnitude == 6.0

    def test_array_minus_array(self):
        """Evaluate [5, 7] - [1, 2]."""
        ureg = get_unit_registry()
        tree = parse("[5, 7] - [1, 2]")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert result[0].magnitude == 4.0
        assert result[1].magnitude == 5.0

    def test_array_div_scalar(self):
        """Evaluate [10, 20] / 2."""
        ureg = get_unit_registry()
        tree = parse("[10, 20] / 2")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert result[0].magnitude == 5.0
        assert result[1].magnitude == 10.0

    def test_array_size_mismatch(self):
        """Evaluate [1, 2] + [3, 4, 5] should raise error."""
        ureg = get_unit_registry()
        tree = parse("[1, 2] + [3, 4, 5]")
        with pytest.raises(EvaluationError) as excinfo:
            evaluate_expression_tree(tree, {}, ureg)
        assert "size mismatch" in str(excinfo.value).lower()

    def test_variable_times_array(self):
        r"""Evaluate V \cdot [1, 2] with V=10."""
        ureg = get_unit_registry()
        symbols = {"V": 10.0 * ureg.L}
        tree = parse(r"V \cdot [1, 2]")
        result = evaluate_expression_tree(tree, symbols, ureg)
        assert len(result) == 2
        assert result[0].magnitude == 10.0
        assert result[1].magnitude == 20.0
        assert str(result[0].units) == "liter"


class TestArrayWithUnits:
    """Test arrays with units in calculations."""

    def test_array_with_unit_times_scalar(self):
        r"""Evaluate [1, 2]\ \text{m} * 3."""
        ureg = get_unit_registry()
        tree = parse(r"[1, 2]\ \text{m} * 3")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert result[0].magnitude == 3.0
        assert result[1].magnitude == 6.0
        assert str(result[0].units) == "meter"

    def test_scalar_times_unit_array(self):
        r"""Evaluate 2 * [5, 10]\ \text{kg}."""
        ureg = get_unit_registry()
        tree = parse(r"2 * [5, 10]\ \text{kg}")
        result = evaluate_expression_tree(tree, {}, ureg)
        assert result[0].magnitude == 10.0
        assert result[1].magnitude == 20.0
        assert str(result[0].units) == "kilogram"
