"""
LaTeX expression tokenizer for LiveMathTeX.

Tokenizes LaTeX math expressions into typed tokens. Uses priority-ordered
pattern matching to correctly identify units, variables, operators, etc.

Key design principle: Units and multi-letter variables MUST be matched
before single letters to avoid implicit multiplication issues.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class TokenType(Enum):
    """Types of tokens in LaTeX math expressions."""

    NUMBER = "number"  # 3.14, 1e-6
    VARIABLE = "variable"  # x, E_{26}, PPE_{eff}, R^2, \alpha
    UNIT = "unit"  # \text{kg}, \mathrm{MWh}
    OPERATOR = "operator"  # +, -, *, /, ^, \cdot, \times
    FRAC = "frac"  # \frac
    LPAREN = "lparen"  # (, \left(
    RPAREN = "rparen"  # ), \right)
    LBRACE = "lbrace"  # {
    RBRACE = "rbrace"  # }
    EOF = "eof"  # End of input


@dataclass
class Token:
    """A token in a LaTeX math expression."""

    type: TokenType
    value: str
    start: int  # Start position in source
    end: int  # End position in source (exclusive)


class ExpressionTokenizer:
    """
    Tokenize LaTeX math expressions for LiveMathTeX.

    Uses priority-ordered pattern matching:
    1. Units in \\text{} or \\mathrm{} - HIGHEST PRIORITY
    2. Numbers (including scientific notation)
    3. Variables with subscripts/superscripts (multi-letter first)
    4. Greek letters
    5. LaTeX commands (\\frac, \\cdot, etc.)
    6. Operators
    7. Parentheses and braces
    8. Single letters - LOWEST PRIORITY (fallback)

    This order prevents splitting "kg" into "k*g" or "PPE" into "P*P*E".
    """

    # Ordered by priority - most specific first
    # Each tuple: (compiled_pattern, token_type, uses_group1)
    # uses_group1: True if we want to extract group(1), False for group(0)
    PATTERNS: List[Tuple[re.Pattern, Optional[TokenType], bool]] = [
        # Units in \text{} or \mathrm{} - HIGHEST PRIORITY
        # Capture the content inside braces
        (re.compile(r"\\text\{([^}]+)\}"), TokenType.UNIT, True),
        (re.compile(r"\\mathrm\{([^}]+)\}"), TokenType.UNIT, True),
        # Numbers (including scientific notation)
        # Must come before variables to not split "1e6" at "e"
        (re.compile(r"\d+\.?\d*(?:[eE][+-]?\d+)?"), TokenType.NUMBER, False),
        # Multi-letter variables with subscripts in braces - BEFORE single letters
        # E_{26}, PPE_{eff}, Cost_{total}
        (re.compile(r"[A-Za-z]+_\{[^}]+\}"), TokenType.VARIABLE, False),
        # Note: Superscript patterns REMOVED - in evaluations, ^ is always an operator
        # x^{2} tokenizes as: VARIABLE(x), OPERATOR(^), LBRACE, NUMBER(2), RBRACE
        # Variable definitions like R^2 := 0.904 are handled by _compute(), not this tokenizer
        #
        # Multi-letter variables with simple subscript (no braces)
        # x_1, E_0 (but not just x or E alone)
        (re.compile(r"[A-Za-z]+_[A-Za-z0-9]+"), TokenType.VARIABLE, False),
        # Simple alphanumeric internal IDs (v0, v1, f0, x0, etc.)
        # Must be a letter followed by digits only (not letter+letter like "kg")
        # This supports the v3.0 internal ID format
        (re.compile(r"[vfx]\d+"), TokenType.VARIABLE, False),
        # Greek letters (common ones used in math/physics)
        (
            re.compile(
                r"\\(?:alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|"
                r"lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|"
                r"Alpha|Beta|Gamma|Delta|Epsilon|Zeta|Eta|Theta|Iota|Kappa|"
                r"Lambda|Mu|Nu|Xi|Pi|Rho|Sigma|Tau|Upsilon|Phi|Chi|Psi|Omega)"
            ),
            TokenType.VARIABLE,
            False,
        ),
        # Fraction command
        (re.compile(r"\\frac"), TokenType.FRAC, False),
        # LaTeX multiplication operators
        (re.compile(r"\\cdot"), TokenType.OPERATOR, False),
        (re.compile(r"\\times"), TokenType.OPERATOR, False),
        # Basic operators (single characters)
        (re.compile(r"[+\-*/^]"), TokenType.OPERATOR, False),
        # LaTeX parentheses
        (re.compile(r"\\left\("), TokenType.LPAREN, False),
        (re.compile(r"\\right\)"), TokenType.RPAREN, False),
        # Regular parentheses
        (re.compile(r"\("), TokenType.LPAREN, False),
        (re.compile(r"\)"), TokenType.RPAREN, False),
        # Braces
        (re.compile(r"\{"), TokenType.LBRACE, False),
        (re.compile(r"\}"), TokenType.RBRACE, False),
        # Single letters LAST (fallback) - after all multi-letter patterns
        (re.compile(r"[A-Za-z]"), TokenType.VARIABLE, False),
        # Whitespace patterns to skip (None token type = skip)
        (re.compile(r"\s+"), None, False),  # Regular whitespace
        (re.compile(r"\\\\"), None, False),  # LaTeX line breaks
        (re.compile(r"\\ "), None, False),  # LaTeX space command
    ]

    def __init__(self, text: str):
        """Initialize tokenizer with input text."""
        self.text = text
        self.pos = 0

    def tokenize(self) -> List[Token]:
        """
        Tokenize the input text into a list of tokens.

        Returns:
            List of Token objects, always ending with EOF token.
        """
        tokens = []
        while self.pos < len(self.text):
            token = self._next_token()
            if token is not None:
                tokens.append(token)
        # Always end with EOF
        tokens.append(Token(TokenType.EOF, "", self.pos, self.pos))
        return tokens

    def _next_token(self) -> Optional[Token]:
        """
        Match the next token at current position.

        Returns:
            Token if matched, None if whitespace/skip pattern matched.
            Advances self.pos either way.
        """
        for pattern, token_type, uses_group1 in self.PATTERNS:
            match = pattern.match(self.text, self.pos)
            if match:
                start = match.start()
                end = match.end()

                # Extract value: group(1) for units, group(0) for everything else
                if uses_group1 and match.lastindex and match.lastindex >= 1:
                    value = match.group(1)
                else:
                    value = match.group(0)

                self.pos = end

                # Skip whitespace patterns (token_type is None)
                if token_type is None:
                    return None

                return Token(token_type, value, start, end)

        # Unknown character - skip it and continue
        # This handles any unrecognized LaTeX commands or symbols
        self.pos += 1
        return None
