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


def parse_calculation_line(
    line: str,
    line_start_offset: int,
    unit_comment: Optional[str] = None
) -> Optional[ParsedCalculation]:
    """Parse a single line of LaTeX into a ParsedCalculation.

    Args:
        line: Single line of LaTeX (not stripped - preserves positions)
        line_start_offset: Character offset of line start in document
        unit_comment: Unit hint from HTML comment (if any)

    Returns:
        ParsedCalculation or None if line has no operators
    """
    # Strip for content analysis but track original positions
    stripped = line.strip()
    if not stripped:
        return None

    # Find where stripped content starts in original line
    leading_ws = len(line) - len(line.lstrip())
    content_start = line_start_offset + leading_ws

    # Check for operators (in priority order)
    has_operators = bool(re.search(r'===|:=|==|=>', stripped))

    if not has_operators:
        return None

    line_span = Span(content_start, content_start + len(stripped))

    # Check for bare '=' error (not part of :=, ==, =>, ===)
    if re.search(r'(?<!:)(?<!>)(?<!=)=(?!=)', stripped):
        return ParsedCalculation(
            operation="ERROR",
            operator_span=Span(content_start, content_start + len(stripped)),
            line=stripped,
            line_span=line_span,
            error_message="Invalid operator '='. Use ':=' for definition or '==' for evaluation."
        )

    # 1. Check for === (unit definition) - must come before ==
    if '===' in stripped:
        idx = stripped.find('===')
        lhs = stripped[:idx].strip()
        rhs = stripped[idx + 3:].strip()

        lhs_start = content_start + stripped.find(lhs)
        op_start = content_start + idx
        rhs_start = content_start + idx + 3 + (len(stripped[idx + 3:]) - len(stripped[idx + 3:].lstrip()))

        return ParsedCalculation(
            operation="===",
            operator_span=Span(op_start, op_start + 3),
            lhs=lhs,
            lhs_span=Span(lhs_start, lhs_start + len(lhs)),
            rhs=rhs,
            rhs_span=Span(rhs_start, rhs_start + len(rhs)),
            line=stripped,
            line_span=line_span,
            unit_hint=unit_comment
        )

    # 2. Check for := (assignment)
    if ':=' in stripped:
        assign_idx = stripped.find(':=')
        lhs = stripped[:assign_idx].strip()
        rest = stripped[assign_idx + 2:]

        lhs_start = content_start + stripped.find(lhs) if lhs else content_start
        assign_op_start = content_start + assign_idx

        # Check for secondary == (combined assignment+eval)
        if '==' in rest:
            eval_idx = rest.find('==')
            expr = rest[:eval_idx].strip()
            result_part = rest[eval_idx + 2:].strip()

            # Check for inline unit hint [unit] at end
            unit_hint = unit_comment
            unit_hint_span = None
            unit_match = re.search(r'\[([^\]]+)\]\s*$', result_part)
            if unit_match and not unit_hint:
                unit_hint = unit_match.group(1).strip()
                unit_hint_start = content_start + assign_idx + 2 + eval_idx + 2 + result_part.find('[')
                unit_hint_span = Span(unit_hint_start, unit_hint_start + len(unit_match.group(0)))
                result_part = result_part[:unit_match.start()].strip()

            expr_start = content_start + assign_idx + 2 + (len(rest[:eval_idx]) - len(rest[:eval_idx].lstrip()))
            eval_op_start = content_start + assign_idx + 2 + eval_idx
            result_start = eval_op_start + 2 + (len(rest[eval_idx + 2:]) - len(rest[eval_idx + 2:].lstrip()))

            return ParsedCalculation(
                operation=":=_==",
                operator_span=Span(assign_op_start, assign_op_start + 2),  # Point to :=
                lhs=lhs,
                lhs_span=Span(lhs_start, lhs_start + len(lhs)) if lhs else None,
                rhs=expr,
                rhs_span=Span(expr_start, expr_start + len(expr)),
                result=result_part,
                result_span=Span(result_start, result_start + len(result_part)),
                line=stripped,
                line_span=line_span,
                unit_hint=unit_hint,
                unit_hint_span=unit_hint_span
            )

        # Simple assignment (no ==)
        rhs = rest.strip()
        rhs_start = content_start + assign_idx + 2 + (len(rest) - len(rest.lstrip()))

        return ParsedCalculation(
            operation=":=",
            operator_span=Span(assign_op_start, assign_op_start + 2),
            lhs=lhs,
            lhs_span=Span(lhs_start, lhs_start + len(lhs)) if lhs else None,
            rhs=rhs,
            rhs_span=Span(rhs_start, rhs_start + len(rhs)),
            line=stripped,
            line_span=line_span,
            unit_hint=unit_comment
        )

    # 3. Check for == (evaluation)
    if '==' in stripped:
        idx = stripped.find('==')
        expr = stripped[:idx].strip()
        result_part = stripped[idx + 2:].strip()

        # Check for inline unit hint [unit] at end
        unit_hint = unit_comment
        unit_hint_span = None
        unit_match = re.search(r'\[([^\]]+)\]\s*$', result_part)
        if unit_match and not unit_hint:
            unit_hint = unit_match.group(1).strip()
            unit_hint_start = content_start + idx + 2 + result_part.find('[')
            unit_hint_span = Span(unit_hint_start, unit_hint_start + len(unit_match.group(0)))
            result_part = result_part[:unit_match.start()].strip()

        expr_start = content_start + stripped.find(expr) if expr else content_start
        op_start = content_start + idx
        result_start = content_start + idx + 2 + (len(stripped[idx + 2:]) - len(stripped[idx + 2:].lstrip()))

        return ParsedCalculation(
            operation="==",
            operator_span=Span(op_start, op_start + 2),
            lhs=expr,
            lhs_span=Span(expr_start, expr_start + len(expr)) if expr else None,
            result=result_part,
            result_span=Span(result_start, result_start + len(result_part)),
            line=stripped,
            line_span=line_span,
            unit_hint=unit_hint,
            unit_hint_span=unit_hint_span
        )

    # 4. Check for => (symbolic)
    if '=>' in stripped:
        idx = stripped.find('=>')
        expr = stripped[:idx].strip()
        result_part = stripped[idx + 2:].strip()

        expr_start = content_start + stripped.find(expr) if expr else content_start
        op_start = content_start + idx
        result_start = content_start + idx + 2 + (len(stripped[idx + 2:]) - len(stripped[idx + 2:].lstrip()))

        return ParsedCalculation(
            operation="=>",
            operator_span=Span(op_start, op_start + 2),
            lhs=expr,
            lhs_span=Span(expr_start, expr_start + len(expr)) if expr else None,
            result=result_part,
            result_span=Span(result_start, result_start + len(result_part)),
            line=stripped,
            line_span=line_span,
            unit_hint=unit_comment
        )

    return None


def parse_math_block_calculations(
    block: "ParsedMathBlock",
    unit_comment: Optional[str] = None,
    value_comment: Optional[str] = None
) -> List[ParsedCalculation]:
    """Parse calculations from a math block.

    Args:
        block: ParsedMathBlock from Phase 8 parser
        unit_comment: Unit hint from HTML comment
        value_comment: Value lookup syntax from HTML comment

    Returns:
        List of ParsedCalculation objects
    """
    calculations: List[ParsedCalculation] = []

    # Handle value_comment case (special value lookup)
    if value_comment:
        # Parse value comment: "VAR [\unit] :precision"
        value_str = value_comment.strip()

        # Extract precision (at end, after :)
        precision_match = re.search(r'\s*:\s*(\d+)\s*$', value_str)
        if precision_match:
            value_str = value_str[:precision_match.start()].strip()

        # Extract unit (in square brackets)
        target_unit = None
        unit_match = re.search(r'\s*\[(.*?)\]\s*$', value_str)
        if unit_match:
            target_unit = unit_match.group(1).strip()
            value_str = value_str[:unit_match.start()].strip()

        # Remaining is the variable name
        var_name = value_str.strip()

        # Create a value calculation - spans point to the whole block
        calculations.append(ParsedCalculation(
            operation="value",
            operator_span=Span(block.doc_start_offset, block.doc_end_offset),
            lhs=var_name,
            lhs_span=Span(block.doc_start_offset, block.doc_end_offset),
            line=block.inner_content.strip(),
            line_span=Span(block.doc_start_offset, block.doc_end_offset),
            unit_hint=target_unit
        ))
        return calculations

    # Calculate delimiter length
    delimiter_len = 2 if block.is_display else 1

    # Split inner content by newlines
    lines = block.inner_content.split('\n')

    # Calculate cumulative offset for each line
    cumulative_offset = 0

    for line in lines:
        # Calculate line start offset in document
        # doc_start_offset + delimiter_len + cumulative_offset
        line_start = block.doc_start_offset + delimiter_len + cumulative_offset

        # Parse this line
        calc = parse_calculation_line(line, line_start, unit_comment)
        if calc is not None:
            calculations.append(calc)

        # Update cumulative offset (line length + newline)
        cumulative_offset += len(line) + 1  # +1 for newline

    return calculations
