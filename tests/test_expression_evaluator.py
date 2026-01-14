"""Tests for the expression evaluator.

This module tests evaluate_expression_tree() which evaluates ExprNode trees
using Pint for unit-aware calculations.

TDD: RED phase - all tests should fail until evaluator is implemented.
"""

import pytest
import pint

from livemathtex.parser.expression_tokenizer import ExpressionTokenizer
from livemathtex.parser.expression_parser import ExpressionParser
from livemathtex.engine.expression_evaluator import (
    evaluate_expression_tree,
    EvaluationError,
)
from livemathtex.engine.pint_backend import get_unit_registry


@pytest.fixture
def ureg():
    """Get unit registry for tests."""
    return get_unit_registry()


def evaluate(latex: str, symbols: dict = None, ureg: pint.UnitRegistry = None):
    """Helper to tokenize, parse, and evaluate a LaTeX expression."""
    if ureg is None:
        ureg = get_unit_registry()
    if symbols is None:
        symbols = {}
    tokens = ExpressionTokenizer(latex).tokenize()
    tree = ExpressionParser(tokens).parse()
    return evaluate_expression_tree(tree, symbols, ureg)


# =============================================================================
# Number Evaluation
# =============================================================================


class TestNumberEvaluation:
    """Test evaluation of numeric literals."""

    def test_integer(self, ureg):
        """Evaluate integer literal."""
        result = evaluate("5", ureg=ureg)
        assert isinstance(result, pint.Quantity)
        assert result.magnitude == 5.0
        assert result.dimensionless

    def test_decimal(self, ureg):
        """Evaluate decimal literal."""
        result = evaluate("3.14", ureg=ureg)
        assert result.magnitude == pytest.approx(3.14)
        assert result.dimensionless

    def test_scientific_notation(self, ureg):
        """Evaluate scientific notation."""
        result = evaluate("1e6", ureg=ureg)
        assert result.magnitude == 1000000.0
        assert result.dimensionless

    def test_scientific_notation_negative_exp(self, ureg):
        """Evaluate scientific notation with negative exponent."""
        result = evaluate("2.5e-3", ureg=ureg)
        assert result.magnitude == pytest.approx(0.0025)

    def test_zero(self, ureg):
        """Evaluate zero."""
        result = evaluate("0", ureg=ureg)
        assert result.magnitude == 0.0


# =============================================================================
# Variable Lookup
# =============================================================================


class TestVariableLookup:
    """Test variable lookup in symbol table."""

    def test_simple_variable(self, ureg):
        """Look up simple variable."""
        symbols = {"x": 5.0 * ureg.dimensionless}
        result = evaluate("x", symbols, ureg)
        assert result.magnitude == 5.0

    def test_variable_with_unit(self, ureg):
        """Look up variable with unit."""
        symbols = {"m": 10 * ureg.kg}
        result = evaluate("m", symbols, ureg)
        assert result.magnitude == 10
        assert result.units == ureg.kg

    def test_subscript_variable(self, ureg):
        """Look up subscript variable (E_{26})."""
        symbols = {"E_{26}": 100 * ureg.kJ}
        result = evaluate("E_{26}", symbols, ureg)
        assert result.magnitude == 100
        assert result.units == ureg.kJ

    def test_multi_letter_variable(self, ureg):
        """Look up multi-letter variable with subscript."""
        symbols = {"PPE_{eff}": 0.85 * ureg.dimensionless}
        result = evaluate("PPE_{eff}", symbols, ureg)
        assert result.magnitude == pytest.approx(0.85)

    def test_greek_letter(self, ureg):
        """Look up Greek letter variable."""
        symbols = {r"\alpha": 0.5 * ureg.dimensionless}
        result = evaluate(r"\alpha", symbols, ureg)
        assert result.magnitude == 0.5

    def test_undefined_variable(self, ureg):
        """Undefined variable raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            evaluate("x", {}, ureg)
        assert "undefined" in str(exc_info.value).lower() or "x" in str(exc_info.value)


# =============================================================================
# Binary Operations
# =============================================================================


class TestBinaryOperations:
    """Test binary operations."""

    def test_addition(self, ureg):
        """Evaluate addition."""
        symbols = {
            "a": 3 * ureg.dimensionless,
            "b": 2 * ureg.dimensionless,
        }
        result = evaluate("a + b", symbols, ureg)
        assert result.magnitude == 5.0

    def test_addition_with_units(self, ureg):
        """Evaluate addition with compatible units."""
        symbols = {
            "a": 3 * ureg.kg,
            "b": 2 * ureg.kg,
        }
        result = evaluate("a + b", symbols, ureg)
        assert result.magnitude == 5.0
        assert result.units == ureg.kg

    def test_subtraction(self, ureg):
        """Evaluate subtraction."""
        symbols = {
            "a": 5 * ureg.dimensionless,
            "b": 2 * ureg.dimensionless,
        }
        result = evaluate("a - b", symbols, ureg)
        assert result.magnitude == 3.0

    def test_multiplication(self, ureg):
        """Evaluate multiplication."""
        symbols = {
            "a": 3 * ureg.dimensionless,
            "b": 4 * ureg.dimensionless,
        }
        result = evaluate("a * b", symbols, ureg)
        assert result.magnitude == 12.0

    def test_multiplication_units(self, ureg):
        """Evaluate multiplication producing new units."""
        symbols = {
            "m": 10 * ureg.kg,
            "v": 5 * ureg("m/s"),
        }
        result = evaluate(r"m \cdot v", symbols, ureg)
        assert result.magnitude == 50.0
        # Should be kg⋅m/s (momentum)
        assert result.dimensionality == ureg("kg * m / s").dimensionality

    def test_multiplication_cdot(self, ureg):
        """Multiplication with \\cdot operator."""
        symbols = {"a": 2 * ureg.dimensionless, "b": 3 * ureg.dimensionless}
        result = evaluate(r"a \cdot b", symbols, ureg)
        assert result.magnitude == 6.0

    def test_multiplication_times(self, ureg):
        """Multiplication with \\times operator."""
        symbols = {"a": 2 * ureg.dimensionless, "b": 3 * ureg.dimensionless}
        result = evaluate(r"a \times b", symbols, ureg)
        assert result.magnitude == 6.0

    def test_division(self, ureg):
        """Evaluate division."""
        symbols = {
            "a": 10 * ureg.dimensionless,
            "b": 2 * ureg.dimensionless,
        }
        result = evaluate("a / b", symbols, ureg)
        assert result.magnitude == 5.0

    def test_division_units(self, ureg):
        """Evaluate division with units."""
        symbols = {
            "d": 100 * ureg.m,
            "t": 10 * ureg.s,
        }
        result = evaluate("d / t", symbols, ureg)
        assert result.magnitude == 10.0
        assert result.dimensionality == ureg("m/s").dimensionality

    def test_power(self, ureg):
        """Evaluate power with dimensionless exponent."""
        symbols = {"a": 2 * ureg.dimensionless}
        result = evaluate("a ^ 3", symbols, ureg)
        assert result.magnitude == 8.0

    def test_power_unit_base(self, ureg):
        """Evaluate power with unit base."""
        symbols = {"L": 3 * ureg.m}
        result = evaluate("L ^ 2", symbols, ureg)
        assert result.magnitude == 9.0
        assert result.dimensionality == ureg("m^2").dimensionality


# =============================================================================
# Unit Attachment
# =============================================================================


class TestUnitAttachment:
    """Test unit attachment to expressions."""

    def test_number_with_unit(self, ureg):
        """Attach unit to number."""
        result = evaluate(r"5 \text{kg}", ureg=ureg)
        assert result.magnitude == 5.0
        assert result.units == ureg.kg

    def test_number_with_compound_unit(self, ureg):
        """Attach compound unit."""
        result = evaluate(r"10 \text{m/s}", ureg=ureg)
        assert result.magnitude == 10.0
        assert result.dimensionality == ureg("m/s").dimensionality

    def test_number_with_power_unit(self, ureg):
        """Attach unit with power."""
        result = evaluate(r"1000 \text{kg/m^3}", ureg=ureg)
        assert result.magnitude == 1000.0
        assert result.dimensionality == ureg("kg/m^3").dimensionality

    def test_mathrm_unit(self, ureg):
        """Unit in mathrm wrapper."""
        result = evaluate(r"100 \mathrm{MWh}", ureg=ureg)
        assert result.magnitude == 100.0

    def test_variable_with_unit(self, ureg):
        """Variable followed by unit (rare but valid)."""
        # This would be: m \text{kg} where m is dimensionless multiplier
        symbols = {"m": 2 * ureg.dimensionless}
        result = evaluate(r"m \text{kg}", symbols, ureg)
        assert result.magnitude == 2.0
        assert result.units == ureg.kg


# =============================================================================
# Fractions
# =============================================================================


class TestFractions:
    """Test fraction evaluation."""

    def test_numeric_fraction(self, ureg):
        """Evaluate numeric fraction."""
        result = evaluate(r"\frac{1}{2}", ureg=ureg)
        assert result.magnitude == 0.5

    def test_variable_fraction(self, ureg):
        """Evaluate variable fraction."""
        symbols = {
            "a": 10 * ureg.dimensionless,
            "b": 2 * ureg.dimensionless,
        }
        result = evaluate(r"\frac{a}{b}", symbols, ureg)
        assert result.magnitude == 5.0

    def test_fraction_with_units(self, ureg):
        """Evaluate fraction producing units."""
        symbols = {
            "m": 100 * ureg.kg,
            "V": 10 * ureg("m^3"),
        }
        result = evaluate(r"\frac{m}{V}", symbols, ureg)
        assert result.magnitude == 10.0
        assert result.dimensionality == ureg("kg/m^3").dimensionality


# =============================================================================
# Unary Minus
# =============================================================================


class TestUnaryMinus:
    """Test unary minus evaluation."""

    def test_negative_number(self, ureg):
        """Evaluate negative number."""
        result = evaluate("-5", ureg=ureg)
        assert result.magnitude == -5.0

    def test_negative_variable(self, ureg):
        """Evaluate negative variable."""
        symbols = {"x": 3 * ureg.dimensionless}
        result = evaluate("-x", symbols, ureg)
        assert result.magnitude == -3.0

    def test_double_negative(self, ureg):
        """Evaluate double negative."""
        symbols = {"x": 5 * ureg.dimensionless}
        result = evaluate("--x", symbols, ureg)
        assert result.magnitude == 5.0

    def test_subtract_negative(self, ureg):
        """Evaluate a + -b."""
        symbols = {
            "a": 5 * ureg.dimensionless,
            "b": 3 * ureg.dimensionless,
        }
        result = evaluate("a + -b", symbols, ureg)
        assert result.magnitude == 2.0


# =============================================================================
# Complex Expressions
# =============================================================================


class TestComplexExpressions:
    """Test complex real-world expressions."""

    def test_fraction_times_variable(self, ureg):
        """Evaluate \\frac{1}{2} \\cdot m."""
        symbols = {"m": 10 * ureg.kg}
        result = evaluate(r"\frac{1}{2} \cdot m", symbols, ureg)
        assert result.magnitude == 5.0
        assert result.units == ureg.kg

    def test_precedence_in_expression(self, ureg):
        """Verify precedence: a + b * c."""
        symbols = {
            "a": 1 * ureg.dimensionless,
            "b": 2 * ureg.dimensionless,
            "c": 3 * ureg.dimensionless,
        }
        result = evaluate("a + b * c", symbols, ureg)
        assert result.magnitude == 7.0  # 1 + (2*3) = 7

    def test_rate_times_time(self, ureg):
        """Evaluate rate × time calculation."""
        # Use single letters (r, t) since multi-letter names need subscripts
        symbols = {
            "r": 100 * ureg("kg/day"),
            "t": 365 * ureg.day,
        }
        result = evaluate(r"r \cdot t", symbols, ureg)
        # 100 kg/day * 365 day = 36500 kg
        assert result.magnitude == pytest.approx(36500)
        assert result.dimensionality == ureg.kg.dimensionality

    def test_parenthesized_expression(self, ureg):
        """Evaluate (a + b) * c."""
        symbols = {
            "a": 1 * ureg.dimensionless,
            "b": 2 * ureg.dimensionless,
            "c": 3 * ureg.dimensionless,
        }
        result = evaluate("(a + b) * c", symbols, ureg)
        assert result.magnitude == 9.0  # (1+2)*3 = 9


# =============================================================================
# Dimension Checking
# =============================================================================


class TestDimensionChecking:
    """Test that dimension mismatches are handled correctly."""

    def test_incompatible_addition(self, ureg):
        """Adding incompatible units raises DimensionalityError."""
        symbols = {
            "m": 5 * ureg.kg,
            "L": 3 * ureg.m,
        }
        with pytest.raises(pint.DimensionalityError):
            evaluate("m + L", symbols, ureg)

    def test_dimensionless_exponent_required(self, ureg):
        """Exponent must be dimensionless."""
        symbols = {
            "a": 2 * ureg.dimensionless,
            "n": 3 * ureg.kg,  # Not dimensionless!
        }
        # This should raise an error - exponent has units
        with pytest.raises((EvaluationError, pint.DimensionalityError)):
            evaluate("a ^ n", symbols, ureg)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_multiply_by_zero(self, ureg):
        """Multiply by zero."""
        symbols = {"x": 5 * ureg.kg}
        result = evaluate("x * 0", symbols, ureg)
        assert result.magnitude == 0.0

    def test_add_zero(self, ureg):
        """Add zero."""
        symbols = {"x": 5 * ureg.dimensionless}
        result = evaluate("x + 0", symbols, ureg)
        assert result.magnitude == 5.0

    def test_power_of_one(self, ureg):
        """Power of one."""
        symbols = {"x": 5 * ureg.kg}
        result = evaluate("x ^ 1", symbols, ureg)
        assert result.magnitude == 5.0
        assert result.units == ureg.kg

    def test_power_of_zero(self, ureg):
        """Power of zero."""
        symbols = {"x": 5 * ureg.kg}
        result = evaluate("x ^ 0", symbols, ureg)
        assert result.magnitude == 1.0

    def test_nested_parentheses(self, ureg):
        """Nested parentheses."""
        symbols = {"x": 2 * ureg.dimensionless}
        result = evaluate("((x + 1) * 2)", symbols, ureg)
        assert result.magnitude == 6.0  # ((2+1)*2)


# =============================================================================
# Integration with Tokenizer/Parser
# =============================================================================


class TestIntegration:
    """Test full pipeline integration."""

    def test_full_pipeline_simple(self, ureg):
        """Test complete tokenize → parse → evaluate pipeline."""
        symbols = {"m": 10 * ureg.kg, "a": 2 * ureg("m/s^2")}
        result = evaluate(r"m \cdot a", symbols, ureg)
        # F = ma, should be 20 N (kg⋅m/s²)
        assert result.magnitude == 20.0
        assert result.dimensionality == ureg.N.dimensionality

    def test_full_pipeline_with_unit(self, ureg):
        """Test pipeline with explicit unit."""
        result = evaluate(r"9.8 \text{m/s^2}", ureg=ureg)
        assert result.magnitude == pytest.approx(9.8)
        assert result.dimensionality == ureg("m/s^2").dimensionality
