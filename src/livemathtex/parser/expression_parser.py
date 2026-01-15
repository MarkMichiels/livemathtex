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
from livemathtex.engine.pint_backend import is_pint_unit


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


@dataclass
class SqrtNode(ExprNode):
    """Square root node (\\sqrt{expr})."""

    operand: ExprNode


@dataclass
class FuncNode(ExprNode):
    """Math function node (\\ln{expr}, \\sin{expr}, etc.)."""

    func: str  # Function name without backslash (ln, sin, cos, etc.)
    operand: ExprNode


@dataclass
class FunctionCallNode(ExprNode):
    """User-defined function call (f(x), PPE_{eff}(0.90), etc.)."""

    name: str  # Function name
    args: List[ExprNode]  # Arguments


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

        # Variable or function call
        if self._check(TokenType.VARIABLE):
            token = self._advance()
            var_name = token.value

            # Check if this is a function call (variable followed by parentheses)
            if self._check(TokenType.LPAREN):
                # This is a user-defined function call like f(x) or PPE_{eff}(0.90)
                self._advance()  # consume '('
                args = []

                # Parse arguments (comma-separated expressions)
                if not self._check(TokenType.RPAREN):
                    args.append(self._expression())
                    while self._match_operator(","):
                        args.append(self._expression())

                if not self._check(TokenType.RPAREN):
                    raise ParseError(
                        f"Expected ')' after function arguments at position "
                        f"{self._current().start}"
                    )
                self._advance()  # consume ')'

                node = FunctionCallNode(var_name, args)
                return self._maybe_attach_unit(node)

            # Just a variable
            node = VariableNode(var_name)
            return self._maybe_attach_unit(node)

        # Standalone unit (rare but possible)
        if self._check(TokenType.UNIT):
            token = self._advance()
            return UnitAttachNode(NumberNode(1.0), token.value)

        # Fraction
        if self._check(TokenType.FRAC):
            return self._parse_fraction()

        # Square root
        if self._check(TokenType.SQRT):
            return self._parse_sqrt()

        # Math functions (ln, sin, cos, etc.)
        if self._check(TokenType.FUNC):
            return self._parse_func()

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

    def _parse_sqrt(self) -> ExprNode:
        r"""Parse \sqrt{expr}."""
        self._advance()  # consume SQRT token

        # Expect opening brace
        if not self._check(TokenType.LBRACE):
            raise ParseError(
                f"Expected '{{' after \\sqrt at position {self._current().start}"
            )
        self._advance()  # consume '{'

        operand = self._expression()

        if not self._check(TokenType.RBRACE):
            raise ParseError(
                f"Expected '}}' after sqrt argument at position "
                f"{self._current().start}"
            )
        self._advance()  # consume '}'

        node = SqrtNode(operand)
        return self._maybe_attach_unit(node)

    def _parse_func(self) -> ExprNode:
        r"""Parse \ln{expr}, \sin{expr}, etc."""
        token = self._advance()  # consume FUNC token
        # Extract function name (strip backslash)
        func_name = token.value.lstrip("\\")

        # Expect opening brace (or parenthesis)
        if self._check(TokenType.LBRACE):
            self._advance()  # consume '{'
            operand = self._expression()
            if not self._check(TokenType.RBRACE):
                raise ParseError(
                    f"Expected '}}' after \\{func_name} argument at position "
                    f"{self._current().start}"
                )
            self._advance()  # consume '}'
        elif self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            operand = self._expression()
            if not self._check(TokenType.RPAREN):
                raise ParseError(
                    f"Expected ')' after \\{func_name} argument at position "
                    f"{self._current().start}"
                )
            self._advance()  # consume ')'
        else:
            # Function followed by just a primary (e.g., \sin x)
            operand = self._primary()

        node = FuncNode(func_name, operand)
        return self._maybe_attach_unit(node)

    def _maybe_attach_unit(self, node: ExprNode) -> ExprNode:
        r"""Check if next token is a unit and attach it to the expression.

        Handles:
        - Explicit UNIT tokens: \text{kg}, \mathrm{kW}
        - Bare variable tokens that are valid Pint units: kg, kW, m, s
        - Unit fractions: \frac{g}{d}, \frac{m^3}{h}

        This enables the common LaTeX patterns:
        - 100\ m (number backslash-space unit)
        - 49020\ \frac{g}{d} (number backslash-space unit fraction)
        """
        # Check for explicit UNIT token (\text{kg}, \mathrm{kW})
        if self._check(TokenType.UNIT):
            unit_token = self._advance()
            return UnitAttachNode(node, unit_token.value)

        # Check for bare variable that is a valid Pint unit
        # This handles the pattern: 100\ m, 5\ kg, 1000\ kW
        if self._check(TokenType.VARIABLE):
            var_token = self._current()
            if is_pint_unit(var_token.value):
                self._advance()
                return UnitAttachNode(node, var_token.value)

        # Check for unit fraction: \frac{numerator_unit}{denominator_unit}
        # This handles: 49020\ \frac{g}{d}, 50\ \frac{m^3}{h}
        if self._check(TokenType.FRAC):
            unit_str = self._try_parse_unit_fraction()
            if unit_str:
                return UnitAttachNode(node, unit_str)

        return node

    def _try_parse_unit_fraction(self) -> Optional[str]:
        r"""Try to parse \frac{num}{denom} as a unit string.

        Returns the unit string like "g/d" or "m**3/h" if valid,
        or None if this is not a unit fraction.

        Does NOT consume tokens if parsing fails (backtracks).
        """
        # Save position for backtracking
        saved_pos = self.pos

        # Consume FRAC
        self._advance()

        # Expect opening brace for numerator
        if not self._check(TokenType.LBRACE):
            self.pos = saved_pos
            return None
        self._advance()

        # Parse numerator content (should be unit-like)
        num_parts = []
        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            token = self._current()
            if token.type == TokenType.VARIABLE:
                num_parts.append(token.value)
            elif token.type == TokenType.UNIT:
                num_parts.append(token.value)
            elif token.type == TokenType.OPERATOR and token.value == "^":
                num_parts.append("**")
            elif token.type == TokenType.LBRACE:
                # Handle nested braces like m^{3}
                self._advance()
                while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
                    inner = self._current()
                    if inner.type == TokenType.NUMBER:
                        num_parts.append(inner.value)
                    elif inner.type == TokenType.VARIABLE:
                        num_parts.append(inner.value)
                    elif inner.type == TokenType.OPERATOR:
                        num_parts.append(inner.value)
                    self._advance()
                # Consume closing brace
                if self._check(TokenType.RBRACE):
                    self._advance()
                continue  # Don't advance again
            elif token.type == TokenType.NUMBER:
                num_parts.append(token.value)
            else:
                # Unknown token in numerator
                self.pos = saved_pos
                return None
            self._advance()

        # Consume closing brace of numerator
        if not self._check(TokenType.RBRACE):
            self.pos = saved_pos
            return None
        self._advance()

        # Expect opening brace for denominator
        if not self._check(TokenType.LBRACE):
            self.pos = saved_pos
            return None
        self._advance()

        # Parse denominator content
        denom_parts = []
        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            token = self._current()
            if token.type == TokenType.VARIABLE:
                denom_parts.append(token.value)
            elif token.type == TokenType.UNIT:
                denom_parts.append(token.value)
            elif token.type == TokenType.OPERATOR and token.value == "^":
                denom_parts.append("**")
            elif token.type == TokenType.LBRACE:
                # Handle nested braces
                self._advance()
                while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
                    inner = self._current()
                    if inner.type == TokenType.NUMBER:
                        denom_parts.append(inner.value)
                    elif inner.type == TokenType.VARIABLE:
                        denom_parts.append(inner.value)
                    elif inner.type == TokenType.OPERATOR:
                        denom_parts.append(inner.value)
                    self._advance()
                if self._check(TokenType.RBRACE):
                    self._advance()
                continue
            elif token.type == TokenType.NUMBER:
                denom_parts.append(token.value)
            else:
                self.pos = saved_pos
                return None
            self._advance()

        # Consume closing brace of denominator
        if not self._check(TokenType.RBRACE):
            self.pos = saved_pos
            return None
        self._advance()

        # Build unit string
        if not num_parts or not denom_parts:
            self.pos = saved_pos
            return None

        numerator = "".join(num_parts)
        denominator = "".join(denom_parts)

        # Check if result is a valid unit
        unit_str = f"{numerator}/{denominator}"
        if is_pint_unit(unit_str):
            return unit_str

        # Also try with original variable names as units (single letters)
        # This handles cases like g/d where g and d are single-letter units
        if is_pint_unit(numerator) or is_pint_unit(denominator):
            return unit_str

        # Fallback: if it looks like a unit pattern, accept it
        # The evaluator will validate later
        if len(numerator) <= 3 and len(denominator) <= 3:
            return unit_str

        self.pos = saved_pos
        return None

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
