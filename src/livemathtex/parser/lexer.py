import re
from typing import List, Iterator, Optional
from .models import Document, TextBlock, MathBlock, Calculation, SourceLocation

class Lexer:
    """
    Parses Markdown text into a structured Document with MathBlocks and TextBlocks.
    Also parses MathBlocks to identify internal Structure (assignments, evaluations).
    """

    # Regex for finding math blocks: $...$ or $$...$$
    # AND optionally an HTML comment immediately following it on the same line (ignoring whitespace).
    # Group 1: The math block
    # Group 2: The comment content (inside <!-- [ ... ] -->) if exists
    # Note: We need to match lazily.
    # New regex: (\$\$[\s\S]*?\$\$|\$[^\$\n]*\$)(?:[ \t]*<!--\s*\[(.*?)\]\s*-->)?

    MATH_BLOCK_RE = re.compile(r'(\$\$[\s\S]*?\$\$|\$[^\$\n]*\$)(?:[ \t]*<!--\s*\[(.*?)\]\s*-->)?')

    # Regex for finding operations inside a math block
    # Matches:
    # 1. Assignment:  var := expr
    # 2. Evaluation:  expr == result (or just ==)
    # 3. Both:        var := expr == result
    # 4. Symbolic:    expr => result

    # We look for these operators.
    # :=  Assignment
    # ==  Evaluation
    # =>  Symbolic

    OPERATOR_RE = re.compile(r'(:=|==|=>)')

    def parse(self, text: str) -> Document:
        """Parse the full document text."""
        children = []
        last_pos = 0

        # Calculate line offsets for location tracking
        line_offsets = [0]
        for match in re.finditer(r'\n', text):
            line_offsets.append(match.end())

        for match in self.MATH_BLOCK_RE.finditer(text):
            # Text before the math block
            if match.start() > last_pos:
                children.append(TextBlock(content=text[last_pos:match.start()]))

            # The math block itself is Group 1
            full_math_str = match.group(1)
            unit_comment = match.group(2) # Optional unit from comment

            is_display = full_math_str.startswith('$$')
            inner_content = full_math_str[2:-2] if is_display else full_math_str[1:-1]

            # Calculate location
            # (Simplified location tracking - to be enhanced if needed for error reporting)
            start_line = self._get_line_number(match.start(), line_offsets)
            end_line = self._get_line_number(match.end(), line_offsets)

            math_block = MathBlock(
                content=match.group(0), # The FULL match including comment is the "content" we step over
                                        # But wait, Render replaces "content".
                                        # If we replace "content", we replace the comment too?
                                        # Yes, we want to reconstruction both math and comment.
                inner_content=inner_content,
                is_display=is_display,
                unit_comment=unit_comment,
                location=SourceLocation(start_line, end_line, 0, 0)
            )
            children.append(math_block)

            last_pos = match.end()

        # Remaining text
        if last_pos < len(text):
            children.append(TextBlock(content=text[last_pos:]))

        return Document(children=children)

    def _get_line_number(self, pos: int, line_offsets: List[int]) -> int:
        """Binary search or simple scan to find line number."""
        # Simple scan is fine for MVP
        for i, offset in enumerate(line_offsets):
            if pos < offset:
                return i
        return len(line_offsets)

    def extract_calculations(self, math_block: MathBlock) -> List[Calculation]:
        """
        Analyze a MathBlock to find specific calculation requests.
        Handles multiline blocks by treating each line as a potential separate calculation.

        If block contains NO livemathtex operators (:=, ==, =>), it's treated as
        pure display LaTeX and passed through unchanged (no error for bare '=').
        """
        content = math_block.inner_content
        lines = content.split('\n')
        calculations = []

        # First pass: check if block has ANY livemathtex operators
        has_operators = bool(re.search(r':=|==|=>', content))

        if not has_operators:
            # Pure display LaTeX - no calculations, pass through unchanged
            return []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # SAFETY CHECK: Bare '=' is an error ONLY in blocks with operators
            # (prevents accidental overwrites when user meant := or ==)
            # Check for '=' that is NOT part of ':=', '==', or '=>'
            if re.search(r'(?<!:)(?<!>)(?<!=)=(?!=)', line):
                # Found a bare '=' in a calculation block - create an error
                calculations.append(
                    Calculation(
                        latex=line,
                        operation="ERROR",
                        target=None,
                        original_result=None,
                        unit_comment=math_block.unit_comment,
                        error_message="Invalid operator '='. Use ':=' for definition or '==' for evaluation."
                    )
                )
                continue

            # Check for ":=" (Assignment)
            assign_match = re.search(r'^\s*(.*?)\s*:=\s*(.*)', line, re.DOTALL)
            if assign_match:
                lhs = assign_match.group(1).strip()
                rest = assign_match.group(2).strip()

                # Check if there is also an evaluation "==" in the "rest"
                eval_match = re.search(r'(.*?)\s*==\s*(.*)', rest, re.DOTALL)
                if eval_match:
                     expr = eval_match.group(1).strip()
                     result_part = eval_match.group(2).strip()
                     calculations.append(
                        Calculation(
                            latex=line,
                            operation=":=_==",
                            target=lhs,
                            original_result=result_part,
                            unit_comment=math_block.unit_comment
                        )
                     )
                else:
                    calculations.append(
                        Calculation(
                            latex=line,
                            operation=":=",
                            target=lhs,
                            original_result=None,
                            unit_comment=math_block.unit_comment
                        )
                    )
                continue

            # Check for "==" (Evaluation)
            # Regex: (expression)\s*==\s*(result)?
            eval_match = re.search(r'^\s*(.*?)\s*==\s*(.*)', line, re.DOTALL)
            if eval_match:
                result_part = eval_match.group(2).strip()
                calculations.append(
                    Calculation(
                        latex=line,
                        operation="==",
                        target=None,
                        original_result=result_part,
                        unit_comment=math_block.unit_comment
                    )
                )
                continue

            # Check for "=>" (Symbolic)
            sym_match = re.search(r'^\s*(.*?)\s*=>\s*(.*)', line, re.DOTALL)
            if sym_match:
                result_part = sym_match.group(2).strip()
                calculations.append(
                     Calculation(
                        latex=line,
                        operation="=>",
                        target=None,
                        original_result=result_part,
                        unit_comment=math_block.unit_comment
                    )
                )
                continue

        return calculations
