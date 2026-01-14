"""
Expression tree evaluator for LiveMathTeX.

Evaluates ExprNode trees directly using Pint for unit-aware calculations.
This is the direct replacement for evaluate_sympy_ast_with_pint() that
eliminates the SymPy dependency.

Key features:
- Walks expression tree and evaluates with Pint
- Proper unit handling and dimension checking
- Variable lookup with name normalization
- Clear error messages for undefined variables
"""

import math
from typing import Dict

import pint

from livemathtex.parser.expression_parser import (
    ExprNode,
    NumberNode,
    VariableNode,
    BinaryOpNode,
    UnaryOpNode,
    FracNode,
    UnitAttachNode,
)
from livemathtex.engine.pint_backend import get_unit_registry

# Mathematical constants - mapped to their values
# The tokenizer produces '\pi' for Greek pi, and 'e' for Euler's number
# Note: 'e' alone is treated as Euler's number; use subscript (e_1) for variables
MATH_CONSTANTS = {
    r"\pi": math.pi,
    "\\pi": math.pi,
    "e": math.e,  # Euler's number (standalone 'e')
}


class EvaluationError(Exception):
    """Error during expression evaluation."""

    pass


def evaluate_expression_tree(
    node: ExprNode,
    symbols: Dict[str, pint.Quantity],
    ureg: pint.UnitRegistry = None,
) -> pint.Quantity:
    """
    Evaluate an expression tree using Pint for unit-aware calculations.

    This walks the ExprNode tree from the parser and evaluates it directly
    with Pint, without any SymPy involvement.

    Args:
        node: Root node of expression tree (from ExpressionParser)
        symbols: Dict mapping variable names to Pint Quantities
        ureg: Pint UnitRegistry (uses global if not provided)

    Returns:
        Pint Quantity with evaluated result

    Raises:
        EvaluationError: If variable not found or evaluation fails
        pint.DimensionalityError: If units are incompatible

    Examples:
        >>> ureg = get_unit_registry()
        >>> symbols = {'m': 10 * ureg.kg, 'a': 2 * ureg('m/s^2')}
        >>> tokens = ExpressionTokenizer(r"m \\cdot a").tokenize()
        >>> tree = ExpressionParser(tokens).parse()
        >>> result = evaluate_expression_tree(tree, symbols, ureg)
        >>> # result is 20 kg⋅m/s² (20 N)
    """
    if ureg is None:
        ureg = get_unit_registry()

    return _eval_node(node, symbols, ureg)


def _eval_node(
    node: ExprNode,
    symbols: Dict[str, pint.Quantity],
    ureg: pint.UnitRegistry,
) -> pint.Quantity:
    """Recursively evaluate an expression node."""

    # NumberNode: numeric literal
    if isinstance(node, NumberNode):
        return node.value * ureg.dimensionless

    # VariableNode: lookup in symbol table
    if isinstance(node, VariableNode):
        return _lookup_variable(node.name, symbols, ureg)

    # BinaryOpNode: evaluate operands and apply operator
    if isinstance(node, BinaryOpNode):
        left = _eval_node(node.left, symbols, ureg)
        right = _eval_node(node.right, symbols, ureg)
        return _apply_binary_op(node.op, left, right, ureg)

    # UnaryOpNode: evaluate operand and apply operator
    if isinstance(node, UnaryOpNode):
        operand = _eval_node(node.operand, symbols, ureg)
        if node.op == "-":
            return -operand
        raise EvaluationError(f"Unknown unary operator: {node.op}")

    # FracNode: evaluate as division
    if isinstance(node, FracNode):
        numerator = _eval_node(node.numerator, symbols, ureg)
        denominator = _eval_node(node.denominator, symbols, ureg)
        return numerator / denominator

    # UnitAttachNode: evaluate expression and multiply by unit
    if isinstance(node, UnitAttachNode):
        expr_value = _eval_node(node.expr, symbols, ureg)
        try:
            unit = ureg(node.unit)
            # If expression already has units, multiply; if dimensionless, convert
            if expr_value.dimensionless:
                return expr_value.magnitude * unit
            else:
                return expr_value * unit
        except pint.UndefinedUnitError:
            raise EvaluationError(f"Unknown unit: {node.unit}")

    raise EvaluationError(f"Unknown node type: {type(node).__name__}")


def _lookup_variable(
    name: str,
    symbols: Dict[str, pint.Quantity],
    ureg: pint.UnitRegistry,
) -> pint.Quantity:
    """
    Look up a variable in the symbol table or mathematical constants.

    Tries multiple name formats to handle LaTeX variations:
    - Mathematical constants (pi, e)
    - Exact match (E_{26})
    - Normalized (E_26)
    - Without braces

    Args:
        name: Variable name from parser (may include LaTeX formatting)
        symbols: Symbol table mapping names to Pint Quantities
        ureg: Pint UnitRegistry

    Returns:
        Pint Quantity for the variable

    Raises:
        EvaluationError: If variable not found
    """
    # Check mathematical constants first
    if name in MATH_CONSTANTS:
        return MATH_CONSTANTS[name] * ureg.dimensionless

    # Try exact match
    if name in symbols:
        return symbols[name]

    # Try normalized name (remove braces from subscripts/superscripts)
    normalized = name.replace("{", "").replace("}", "")
    if normalized in symbols:
        return symbols[normalized]

    # Try adding braces if name has underscore or caret
    if "_" in name and "{" not in name:
        # x_1 -> x_{1}
        parts = name.split("_", 1)
        braced = f"{parts[0]}_{{{parts[1]}}}"
        if braced in symbols:
            return symbols[braced]

    if "^" in name and "{" not in name:
        # x^2 -> x^{2}
        parts = name.split("^", 1)
        braced = f"{parts[0]}^{{{parts[1]}}}"
        if braced in symbols:
            return symbols[braced]

    raise EvaluationError(f"Undefined variable: {name}")


def _apply_binary_op(
    op: str,
    left: pint.Quantity,
    right: pint.Quantity,
    ureg: pint.UnitRegistry,
) -> pint.Quantity:
    """
    Apply a binary operator to two Pint Quantities.

    Args:
        op: Operator string ("+", "-", "*", "/", "^")
        left: Left operand
        right: Right operand
        ureg: Pint UnitRegistry

    Returns:
        Result as Pint Quantity

    Raises:
        EvaluationError: If operator is unknown or invalid
        pint.DimensionalityError: If dimensions are incompatible
    """
    if op == "+":
        return left + right

    if op == "-":
        return left - right

    if op == "*":
        return left * right

    if op == "/":
        return left / right

    if op == "^":
        # Exponent must be dimensionless
        if isinstance(right, pint.Quantity):
            if right.dimensionless:
                exp = float(right.magnitude)
            else:
                raise EvaluationError(
                    f"Exponent must be dimensionless, got: {right.units}"
                )
        else:
            exp = float(right)
        return left**exp

    raise EvaluationError(f"Unknown operator: {op}")
