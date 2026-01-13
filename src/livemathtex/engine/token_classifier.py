"""
Token classification for variables, units, and functions.

This module centralizes the logic for determining what a token represents
(unit, variable, function, or unknown) and detecting implicit multiplication
patterns from latex2sympy parsing.

Addresses ISS-018 and ISS-022: Improve diagnostics when multi-letter identifiers
are split by latex2sympy's implicit multiplication.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Set, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from sympy import Symbol
    from .symbols import SymbolTable


class TokenType(Enum):
    """Classification of a token in mathematical expressions."""
    UNIT = auto()      # Known unit (kg, MWh, mol, etc.)
    VARIABLE = auto()  # Defined variable in symbol table
    FUNCTION = auto()  # Known function (sin, cos, log, etc.)
    UNKNOWN = auto()   # Not recognized


@dataclass
class ImplicitMultInfo:
    """
    Information about detected implicit multiplication of a multi-letter identifier.

    When latex2sympy parses 'PPE' as 'P*P*E', this class captures that pattern
    to provide better error messages.

    Attributes:
        intended_symbol: The original multi-letter identifier (e.g., "PPE")
        split_as: How it was parsed (e.g., "P*P*E")
        undefined_letters: Letters that are undefined (e.g., ["P", "E"])
        unit_conflicts: Letters that conflict with unit names (e.g., ["A"] for ampere)
    """
    intended_symbol: str
    split_as: str
    undefined_letters: List[str]
    unit_conflicts: List[str]


# Known LaTeX functions that latex2sympy recognizes
KNOWN_FUNCTIONS = {
    'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
    'arcsin', 'arccos', 'arctan', 'asin', 'acos', 'atan',
    'sinh', 'cosh', 'tanh', 'coth',
    'exp', 'log', 'ln', 'lg',
    'sqrt', 'root',
    'abs', 'floor', 'ceil',
    'max', 'min',
    'sum', 'prod', 'int',
}

# Single-letter symbols that are commonly units (for conflict detection)
SINGLE_LETTER_UNITS = {
    'A': 'ampere',
    'V': 'volt',
    'W': 'watt',
    'J': 'joule',
    'N': 'newton',
    'C': 'coulomb',
    'F': 'farad',
    'H': 'henry',
    'K': 'kelvin',
    'T': 'tesla',
    'm': 'meter',
    's': 'second',
    'g': 'gram',
    'L': 'liter',
    'l': 'liter',
}


class TokenClassifier:
    """
    Centralized token classification for variables, units, and functions.

    This class provides a unified interface for determining what a token
    represents in mathematical expressions, and for detecting when
    latex2sympy has incorrectly split multi-letter identifiers.
    """

    def __init__(self, symbol_table: "SymbolTable"):
        """
        Initialize the classifier.

        Args:
            symbol_table: The symbol table containing defined variables
        """
        self.symbols = symbol_table

    def classify(self, token: str) -> TokenType:
        """
        Classify a token as UNIT, VARIABLE, FUNCTION, or UNKNOWN.

        Args:
            token: The token to classify

        Returns:
            The TokenType classification
        """
        if not token:
            return TokenType.UNKNOWN

        # Check if it's a known function
        if token.lower() in KNOWN_FUNCTIONS:
            return TokenType.FUNCTION

        # Check if it's a defined variable
        if self._is_defined_variable(token):
            return TokenType.VARIABLE

        # Check if it's a unit
        if self._is_unit(token):
            return TokenType.UNIT

        return TokenType.UNKNOWN

    def _is_defined_variable(self, token: str) -> bool:
        """Check if token is a defined variable in the symbol table."""
        # Get all defined symbols
        mappings = self.symbols.get_all_latex_to_internal()
        return token in mappings

    def _is_unit(self, token: str) -> bool:
        """Check if token is a recognized unit."""
        from .pint_backend import is_known_unit
        return is_known_unit(token)

    def is_multi_letter_identifier(self, token: str) -> bool:
        """
        Check if token looks like a multi-letter identifier.

        Multi-letter identifiers are:
        - 2+ characters
        - All letters (possibly with some numbers)
        - Not a known function
        - Not a known unit

        Examples:
            PPE, PAR, ABC -> True (multi-letter)
            x, A, kg -> False (single letter or known unit)
            sin, cos -> False (known function)
        """
        if not token or len(token) < 2:
            return False

        # Must be alphabetic (possibly with trailing numbers like PPE1)
        if not re.match(r'^[A-Za-z][A-Za-z0-9]*$', token):
            return False

        # Should not be a known function
        if token.lower() in KNOWN_FUNCTIONS:
            return False

        # Should not be a known unit
        if self._is_unit(token):
            return False

        return True

    def has_unit_conflict(self, letter: str) -> Optional[str]:
        """
        Check if a single letter conflicts with a unit name.

        Args:
            letter: A single letter to check

        Returns:
            The unit name if there's a conflict, None otherwise
        """
        return SINGLE_LETTER_UNITS.get(letter)

    def detect_implicit_multiplication(
        self,
        original_latex: str,
        parsed_symbols: Set["Symbol"]
    ) -> Optional[ImplicitMultInfo]:
        """
        Detect if a multi-letter identifier was split by latex2sympy.

        When latex2sympy parses 'PPE' as 'P*P*E', we can detect this by:
        1. Finding contiguous multi-letter sequences in the original LaTeX
        2. Checking if those letters appear as separate symbols in parsed_symbols

        Args:
            original_latex: The original LaTeX string (e.g., "x := PPE")
            parsed_symbols: Set of Symbol objects from the parsed expression

        Returns:
            ImplicitMultInfo if implicit multiplication detected, None otherwise
        """
        # Extract the single-letter symbol names from parsed expression
        parsed_letters = set()
        for sym in parsed_symbols:
            name = str(sym)
            # Only consider single letters
            if len(name) == 1 and name.isalpha():
                parsed_letters.add(name)

        if not parsed_letters:
            return None

        # Find multi-letter sequences in original LaTeX
        # Pattern: contiguous uppercase letters or mixed case starting with uppercase
        # We look for sequences that:
        # - Are 2+ letters
        # - Appear to be identifiers (not in \text{} or similar)
        candidates = self._find_multi_letter_candidates(original_latex)

        for candidate in candidates:
            # Check if the candidate's letters appear in parsed symbols
            letters = list(candidate)
            matching_letters = [l for l in letters if l in parsed_letters]

            # If most/all letters from candidate appear as single symbols,
            # it was likely split by implicit multiplication
            if len(matching_letters) >= len(letters) * 0.5 and len(matching_letters) >= 2:
                # This candidate was probably split
                undefined_letters = []
                unit_conflicts = []

                for letter in set(letters):
                    # Check if this letter is defined or is a unit
                    if not self._is_defined_variable(letter):
                        # Check for unit conflict
                        unit_name = self.has_unit_conflict(letter)
                        if unit_name:
                            unit_conflicts.append(letter)
                        elif not self._is_unit(letter):
                            undefined_letters.append(letter)

                # Build the "split as" string
                split_as = '*'.join(letters)

                return ImplicitMultInfo(
                    intended_symbol=candidate,
                    split_as=split_as,
                    undefined_letters=sorted(undefined_letters),
                    unit_conflicts=sorted(unit_conflicts),
                )

        return None

    def _find_multi_letter_candidates(self, latex: str) -> List[str]:
        """
        Find potential multi-letter identifiers in LaTeX string.

        Looks for sequences like PPE, PAR, ABC that could be interpreted
        as implicit multiplication.

        Args:
            latex: The LaTeX string to search

        Returns:
            List of candidate multi-letter identifiers
        """
        candidates = []

        # Remove LaTeX commands and their arguments to avoid false positives
        # E.g., \text{kg} should not yield 'kg' as a candidate
        cleaned = re.sub(r'\\(text|mathrm|textbf|mathbf)\{[^}]*\}', '', latex)
        cleaned = re.sub(r'\\[a-zA-Z]+', '', cleaned)  # Remove other commands

        # Find contiguous letter sequences of 2+ characters
        # These could be multi-letter identifiers
        pattern = r'[A-Za-z]{2,}'
        matches = re.findall(pattern, cleaned)

        for match in matches:
            # Skip if it's a known function
            if match.lower() in KNOWN_FUNCTIONS:
                continue
            # Skip if it's a known unit
            if self._is_unit(match):
                continue
            # Skip if it's already defined
            if self._is_defined_variable(match):
                continue

            candidates.append(match)

        return candidates
