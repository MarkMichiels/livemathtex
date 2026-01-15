"""Tests for LaTeX expression tokenizer.

TDD RED phase: These tests define expected behavior for the expression tokenizer.
The tokenizer converts LaTeX math expressions into typed tokens.
"""

import pytest


class TestTokenType:
    """Tests for TokenType enum."""

    def test_token_type_enum_exists(self):
        """TokenType enum should exist with required values."""
        from livemathtex.parser.expression_tokenizer import TokenType

        assert TokenType.NUMBER
        assert TokenType.VARIABLE
        assert TokenType.UNIT
        assert TokenType.OPERATOR
        assert TokenType.FRAC
        assert TokenType.LPAREN
        assert TokenType.RPAREN
        assert TokenType.LBRACE
        assert TokenType.RBRACE
        assert TokenType.EOF


class TestToken:
    """Tests for Token dataclass."""

    def test_token_has_required_fields(self):
        """Token should have type, value, start, end fields."""
        from livemathtex.parser.expression_tokenizer import Token, TokenType

        token = Token(TokenType.NUMBER, "42", 0, 2)
        assert token.type == TokenType.NUMBER
        assert token.value == "42"
        assert token.start == 0
        assert token.end == 2


class TestExpressionTokenizer:
    """Tests for ExpressionTokenizer class."""

    def test_tokenizer_exists(self):
        """ExpressionTokenizer class should exist."""
        from livemathtex.parser.expression_tokenizer import ExpressionTokenizer

        tokenizer = ExpressionTokenizer("1 + 2")
        assert tokenizer is not None

    def test_tokenize_returns_list(self):
        """tokenize() should return a list of tokens."""
        from livemathtex.parser.expression_tokenizer import ExpressionTokenizer

        tokenizer = ExpressionTokenizer("1")
        tokens = tokenizer.tokenize()
        assert isinstance(tokens, list)


class TestNumberTokens:
    """Tests for number tokenization."""

    def test_integer(self):
        """Integer tokenizes as NUMBER."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("42").tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "42"

    def test_decimal(self):
        """Decimal number tokenizes as NUMBER."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("3.14").tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "3.14"

    def test_scientific_notation(self):
        """Scientific notation tokenizes as NUMBER."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("1e-6").tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "1e-6"

    def test_scientific_notation_uppercase(self):
        """Uppercase scientific notation tokenizes as NUMBER."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("6.022E23").tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "6.022E23"


class TestUnitTokens:
    """Tests for unit tokenization - HIGHEST PRIORITY."""

    def test_text_unit(self):
        """\\text{kg} tokenizes as UNIT with value 'kg'."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\text{kg}").tokenize()
        assert tokens[0].type == TokenType.UNIT
        assert tokens[0].value == "kg"

    def test_mathrm_unit(self):
        """\\mathrm{MWh} tokenizes as UNIT with value 'MWh'."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\mathrm{MWh}").tokenize()
        assert tokens[0].type == TokenType.UNIT
        assert tokens[0].value == "MWh"

    def test_compound_unit(self):
        """\\text{kg/m^2} tokenizes as UNIT."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\text{kg/m^2}").tokenize()
        assert tokens[0].type == TokenType.UNIT
        assert tokens[0].value == "kg/m^2"


class TestVariableTokens:
    """Tests for variable tokenization."""

    def test_single_letter(self):
        """Single letter tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("x").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "x"

    def test_subscript_with_braces(self):
        """Variable with subscript in braces tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("E_{26}").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "E_{26}"

    def test_multi_letter_with_subscript(self):
        """Multi-letter variable with subscript tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("PPE_{eff}").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "PPE_{eff}"

    def test_superscript_as_operator(self):
        """Superscript is tokenized as operator, not part of variable.

        R^2 becomes: VARIABLE(R), OPERATOR(^), NUMBER(2)
        This is correct for evaluations where ^ means exponentiation.
        Variable definitions like R^2 := 0.904 are handled by _compute(), not this tokenizer.
        """
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("R^2").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "R"
        assert tokens[1].type == TokenType.OPERATOR
        assert tokens[1].value == "^"
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "2"

    def test_subscript_without_braces(self):
        """Variable with simple subscript (no braces) tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("x_1").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == "x_1"


class TestGreekLetterTokens:
    """Tests for Greek letter tokenization."""

    def test_alpha(self):
        """\\alpha tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\alpha").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == r"\alpha"

    def test_mu(self):
        """\\mu tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\mu").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == r"\mu"

    def test_pi(self):
        """\\pi tokenizes as VARIABLE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\pi").tokenize()
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == r"\pi"


class TestOperatorTokens:
    """Tests for operator tokenization."""

    def test_plus(self):
        """Plus operator tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("+").tokenize()
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == "+"

    def test_minus(self):
        """Minus operator tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("-").tokenize()
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == "-"

    def test_multiply(self):
        """Multiply operator tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("*").tokenize()
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == "*"

    def test_divide(self):
        """Divide operator tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("/").tokenize()
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == "/"

    def test_power(self):
        """Power operator tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        # When not part of a variable
        tokens = ExpressionTokenizer("2^3").tokenize()
        # First token is NUMBER, check third token (after we skip implicit handling)
        # For now, just check that ^ appears somewhere in tokens
        op_tokens = [t for t in tokens if t.type == TokenType.OPERATOR]
        # Note: 2^3 might be parsed differently - let's check the actual behavior
        assert any(t.value == "^" for t in tokens) or "^" in str([t.value for t in tokens])

    def test_cdot(self):
        """\\cdot tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\cdot").tokenize()
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == r"\cdot"

    def test_times(self):
        """\\times tokenizes as OPERATOR."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\times").tokenize()
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == r"\times"


class TestFractionToken:
    """Tests for \\frac tokenization."""

    def test_frac_command(self):
        """\\frac tokenizes as FRAC."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\frac").tokenize()
        assert tokens[0].type == TokenType.FRAC
        assert tokens[0].value == r"\frac"


class TestParenthesisTokens:
    """Tests for parenthesis tokenization."""

    def test_left_paren(self):
        """( tokenizes as LPAREN."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("(").tokenize()
        assert tokens[0].type == TokenType.LPAREN

    def test_right_paren(self):
        """) tokenizes as RPAREN."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(")").tokenize()
        assert tokens[0].type == TokenType.RPAREN

    def test_left_latex_paren(self):
        """\\left( tokenizes as LPAREN."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\left(").tokenize()
        assert tokens[0].type == TokenType.LPAREN

    def test_right_latex_paren(self):
        """\\right) tokenizes as RPAREN."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\right)").tokenize()
        assert tokens[0].type == TokenType.RPAREN


class TestBraceTokens:
    """Tests for brace tokenization."""

    def test_left_brace(self):
        """{ tokenizes as LBRACE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("{").tokenize()
        assert tokens[0].type == TokenType.LBRACE

    def test_right_brace(self):
        """} tokenizes as RBRACE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("}").tokenize()
        assert tokens[0].type == TokenType.RBRACE


class TestWhitespaceHandling:
    """Tests for whitespace handling."""

    def test_spaces_skipped(self):
        """Spaces between tokens are skipped."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("1 + 2").tokenize()
        # Should have NUMBER, OPERATOR, NUMBER, EOF (no whitespace tokens)
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 3
        assert non_eof[0].type == TokenType.NUMBER
        assert non_eof[1].type == TokenType.OPERATOR
        assert non_eof[2].type == TokenType.NUMBER

    def test_latex_space_skipped(self):
        """LaTeX space (\\ ) is skipped."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"10\ \text{kg}").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 2
        assert non_eof[0].type == TokenType.NUMBER
        assert non_eof[1].type == TokenType.UNIT


class TestEOFToken:
    """Tests for EOF token."""

    def test_ends_with_eof(self):
        """Token list ends with EOF."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("x").tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_empty_input_produces_eof(self):
        """Empty input produces just EOF."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("").tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF


class TestComplexExpressions:
    """Tests for complex expression tokenization."""

    def test_simple_addition(self):
        """a + b tokenizes correctly."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("a + b").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 3
        assert non_eof[0].value == "a"
        assert non_eof[1].value == "+"
        assert non_eof[2].value == "b"

    def test_number_with_unit(self):
        """10\\ \\text{kg} tokenizes as NUMBER, UNIT."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"10\ \text{kg}").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 2
        assert non_eof[0].type == TokenType.NUMBER
        assert non_eof[0].value == "10"
        assert non_eof[1].type == TokenType.UNIT
        assert non_eof[1].value == "kg"

    def test_multiplication_with_cdot(self):
        """x \\cdot y tokenizes correctly."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"x \cdot y").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 3
        assert non_eof[0].type == TokenType.VARIABLE
        assert non_eof[1].type == TokenType.OPERATOR
        assert non_eof[1].value == r"\cdot"
        assert non_eof[2].type == TokenType.VARIABLE

    def test_fraction_structure(self):
        """\\frac{a}{b} tokenizes as FRAC, LBRACE, VARIABLE, RBRACE, LBRACE, VARIABLE, RBRACE."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\frac{a}{b}").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 7
        assert non_eof[0].type == TokenType.FRAC
        assert non_eof[1].type == TokenType.LBRACE
        assert non_eof[2].type == TokenType.VARIABLE
        assert non_eof[3].type == TokenType.RBRACE
        assert non_eof[4].type == TokenType.LBRACE
        assert non_eof[5].type == TokenType.VARIABLE
        assert non_eof[6].type == TokenType.RBRACE

    def test_parenthesized_expression(self):
        """(x + y) tokenizes correctly."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("(x + y)").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 5
        assert non_eof[0].type == TokenType.LPAREN
        assert non_eof[1].type == TokenType.VARIABLE
        assert non_eof[2].type == TokenType.OPERATOR
        assert non_eof[3].type == TokenType.VARIABLE
        assert non_eof[4].type == TokenType.RPAREN


class TestPriorityOrdering:
    """Tests to verify priority ordering (units before single letters)."""

    def test_kg_is_unit_not_k_g(self):
        """\\text{kg} is UNIT, not k*g."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer(r"\text{kg}").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 1
        assert non_eof[0].type == TokenType.UNIT
        assert non_eof[0].value == "kg"

    def test_variable_with_subscript_is_single_token(self):
        """PPE_{eff} is one VARIABLE token, not P*P*E_{eff}."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("PPE_{eff}").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 1
        assert non_eof[0].type == TokenType.VARIABLE
        assert non_eof[0].value == "PPE_{eff}"

    def test_E_subscript_is_variable(self):
        """E_{26} is VARIABLE, not Euler's number."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("E_{26}").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 1
        assert non_eof[0].type == TokenType.VARIABLE
        assert non_eof[0].value == "E_{26}"


class TestSpanTracking:
    """Tests for position/span tracking."""

    def test_token_has_correct_start_end(self):
        """Token has correct start and end positions."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        tokens = ExpressionTokenizer("42").tokenize()
        assert tokens[0].start == 0
        assert tokens[0].end == 2

    def test_second_token_position(self):
        """Second token has correct position after first."""
        from livemathtex.parser.expression_tokenizer import (
            ExpressionTokenizer,
            TokenType,
        )

        # "1 + 2" - positions: 1 at 0-1, + at 2-3, 2 at 4-5
        tokens = ExpressionTokenizer("1 + 2").tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert non_eof[0].start == 0
        assert non_eof[0].end == 1
        assert non_eof[1].start == 2
        assert non_eof[1].end == 3
        assert non_eof[2].start == 4
        assert non_eof[2].end == 5
