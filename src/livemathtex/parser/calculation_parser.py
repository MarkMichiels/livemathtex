"""
Calculation parser with character-level span tracking.

Builds on Phase 8's hybrid parser to add operator detection with
precise document positions for all semantic parts (lhs, operator, rhs, result).
"""

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from .markdown_parser import ParsedMathBlock


@dataclass
class Span:
    """Character span in document."""
    start: int  # Start offset in document
    end: int    # End offset in document (exclusive)

    def extract(self, text: str) -> str:
        """Extract the span from document text."""
        return text[self.start:self.end]


@dataclass
class ParsedCalculation:
    """Calculation with character-level spans."""
    operation: str          # "===", ":=", "==", "=>", ":=_==", "value", "ERROR"
    operator_span: Span     # Position of operator in document

    # LHS (left-hand side) - variable name for assignments
    lhs: Optional[str] = None
    lhs_span: Optional[Span] = None

    # RHS (right-hand side) - expression
    rhs: Optional[str] = None
    rhs_span: Optional[Span] = None

    # Result (after == for evaluations)
    result: Optional[str] = None
    result_span: Optional[Span] = None

    # Unit hint (from [unit] or HTML comment)
    unit_hint: Optional[str] = None
    unit_hint_span: Optional[Span] = None

    # Original line for reference
    line: str = ""
    line_span: Optional[Span] = None

    # Error info
    error_message: Optional[str] = None
