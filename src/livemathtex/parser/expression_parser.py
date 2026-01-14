"""
LaTeX expression parser for LiveMathTeX.

Converts tokens from ExpressionTokenizer into an expression tree suitable
for direct Pint evaluation. Uses recursive descent parsing with proper
operator precedence (PEMDAS).

Key design principles:
- No implicit multiplication (explicit operators required)
- Right associativity for exponentiation (a^b^c = a^(b^c))
- Standard precedence: (), ^, */, +-
"""

from dataclasses import dataclass
from typing import List, Optional

from livemathtex.parser.expression_tokenizer import Token, TokenType


class ParseError(Exception):
    """Error during expression parsing."""

    pass


# =============================================================================
# Expression Node Types
# =============================================================================


@dataclass
class ExprNode:
    """Base class for expression tree nodes."""

    pass


@dataclass
class NumberNode(ExprNode):
    """Numeric literal node."""

    value: float


@dataclass
class VariableNode(ExprNode):
    """Variable reference node."""

    name: str  # LaTeX name as-is (E_{26}, \alpha, etc.)


@dataclass
class BinaryOpNode(ExprNode):
    """Binary operation node."""

    op: str  # "+", "-", "*", "/", "^"
    left: ExprNode
    right: ExprNode


@dataclass
class UnaryOpNode(ExprNode):
    """Unary operation node (negation)."""

    op: str  # "-"
    operand: ExprNode


@dataclass
class FracNode(ExprNode):
    """LaTeX fraction node (\\frac{num}{denom})."""

    numerator: ExprNode
    denominator: ExprNode


@dataclass
class UnitAttachNode(ExprNode):
    """Expression with unit attached."""

    expr: ExprNode
    unit: str  # Unit string without \\text{} wrapper


# =============================================================================
# Expression Parser
# =============================================================================


class ExpressionParser:
    """
    Parse tokens into an expression tree.

    Uses recursive descent with the following precedence (lowest to highest):
    1. Addition, subtraction (+, -)
    2. Multiplication, division (*, /, \\cdot, \\times)
    3. Exponentiation (^) - right associative
    4. Unary minus (-)
    5. Primary (numbers, variables, parentheses, fractions)

    Grammar (pseudo-BNF):
        expression  -> additive
        additive    -> multiplicative (('+' | '-') multiplicative)*
        multiplicative -> power (('*' | '/' | '\\cdot' | '\\times') power)*
        power       -> unary ('^' power)?  # right associative
        unary       -> '-' unary | primary
        primary     -> NUMBER | VARIABLE | UNIT | '(' expression ')' | FRAC '{' expr '}' '{' expr '}'
    """

    def __init__(self, tokens: List[Token]):
        """Initialize parser with token list.

        Args:
            tokens: List of tokens from ExpressionTokenizer (must end with EOF)
        """
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ExprNode:
        """Parse tokens into expression tree.

        Returns:
            Root node of expression tree.

        Raises:
            ParseError: If expression is invalid.
        """
        if self._check(TokenType.EOF):
            raise ParseError("Empty expression")

        result = self._expression()

        # After parsing, should only have EOF left (or unit attachment)
        if not self._check(TokenType.EOF):
            token = self._current()
            raise ParseError(
                f"Unexpected token after expression: {token.type.value} "
                f"'{token.value}' at position {token.start}"
            )

        return result

    # -------------------------------------------------------------------------
    # Recursive Descent Methods
    # -------------------------------------------------------------------------

    def _expression(self) -> ExprNode:
        """Parse expression (entry point)."""
        return self._additive()

    def _additive(self) -> ExprNode:
        """Parse additive expression (lowest precedence binary ops)."""
        left = self._multiplicative()

        while self._match_operator("+", "-"):
            op = self._previous().value
            right = self._multiplicative()
            left = BinaryOpNode(op, left, right)

        return left

    def _multiplicative(self) -> ExprNode:
        """Parse multiplicative expression."""
        left = self._power()

        while self._match_operator("*", "/", "\\cdot", "\\times"):
            op_token = self._previous().value
            # Normalize cdot and times to *
            op = "*" if op_token in ("\\cdot", "\\times") else op_token
            right = self._power()
            left = BinaryOpNode(op, left, right)

        return left

    def _power(self) -> ExprNode:
        """Parse power expression (right associative)."""
        left = self._unary()

        if self._match_operator("^"):
            # Right associative: recursively parse the right side
            right = self._power()
            left = BinaryOpNode("^", left, right)

        return left

    def _unary(self) -> ExprNode:
        """Parse unary expression (unary minus)."""
        if self._match_operator("-"):
            operand = self._unary()  # Allow chained: --x
            return UnaryOpNode("-", operand)

        return self._primary()

    def _primary(self) -> ExprNode:
        """Parse primary expression (atoms)."""
        # Number
        if self._check(TokenType.NUMBER):
            token = self._advance()
            node = NumberNode(float(token.value))
            return self._maybe_attach_unit(node)

        # Variable
        if self._check(TokenType.VARIABLE):
            token = self._advance()
            node = VariableNode(token.value)
            return self._maybe_attach_unit(node)

        # Standalone unit (rare but possible)
        if self._check(TokenType.UNIT):
            token = self._advance()
            return UnitAttachNode(NumberNode(1.0), token.value)

        # Fraction
        if self._check(TokenType.FRAC):
            return self._parse_fraction()

        # Parenthesized expression
        if self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            expr = self._expression()
            if not self._check(TokenType.RPAREN):
                raise ParseError(
                    f"Expected closing parenthesis at position {self._current().start}"
                )
            self._advance()  # consume ')'
            return self._maybe_attach_unit(expr)

        # Braced expression (LaTeX grouping, e.g., ^{x+1})
        if self._check(TokenType.LBRACE):
            self._advance()  # consume '{'
            expr = self._expression()
            if not self._check(TokenType.RBRACE):
                raise ParseError(
                    f"Expected closing brace at position {self._current().start}"
                )
            self._advance()  # consume '}'
            return self._maybe_attach_unit(expr)

        # Unexpected token
        if self._check(TokenType.EOF):
            raise ParseError("Unexpected end of expression")

        token = self._current()
        raise ParseError(
            f"Unexpected token: {token.type.value} '{token.value}' "
            f"at position {token.start}"
        )

    def _parse_fraction(self) -> ExprNode:
        """Parse \\frac{numerator}{denominator}."""
        self._advance()  # consume FRAC token

        # Expect opening brace for numerator
        if not self._check(TokenType.LBRACE):
            raise ParseError(
                f"Expected '{{' after \\frac at position {self._current().start}"
            )
        self._advance()  # consume '{'

        numerator = self._expression()

        if not self._check(TokenType.RBRACE):
            raise ParseError(
                f"Expected '}}' after fraction numerator at position "
                f"{self._current().start}"
            )
        self._advance()  # consume '}'

        # Expect opening brace for denominator
        if not self._check(TokenType.LBRACE):
            raise ParseError(
                f"Expected '{{' for fraction denominator at position "
                f"{self._current().start}"
            )
        self._advance()  # consume '{'

        denominator = self._expression()

        if not self._check(TokenType.RBRACE):
            raise ParseError(
                f"Expected '}}' after fraction denominator at position "
                f"{self._current().start}"
            )
        self._advance()  # consume '}'

        node = FracNode(numerator, denominator)
        return self._maybe_attach_unit(node)

    def _maybe_attach_unit(self, node: ExprNode) -> ExprNode:
        """Check if next token is a unit and attach it to the expression."""
        if self._check(TokenType.UNIT):
            unit_token = self._advance()
            return UnitAttachNode(node, unit_token.value)
        return node

    # -------------------------------------------------------------------------
    # Token Helper Methods
    # -------------------------------------------------------------------------

    def _current(self) -> Token:
        """Get current token without consuming it."""
        return self.tokens[self.pos]

    def _previous(self) -> Token:
        """Get previously consumed token."""
        return self.tokens[self.pos - 1]

    def _advance(self) -> Token:
        """Consume and return current token."""
        token = self.tokens[self.pos]
        if not self._check(TokenType.EOF):
            self.pos += 1
        return token

    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        return self._current().type == token_type

    def _match_operator(self, *values: str) -> bool:
        """Check if current token is an operator with given value(s).

        If match, consumes the token and returns True.
        """
        if self._check(TokenType.OPERATOR):
            if self._current().value in values:
                self._advance()
                return True
        return False
