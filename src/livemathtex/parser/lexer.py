import re
from typing import Any, Dict, List, Iterator, Optional
from .models import Document, TextBlock, MathBlock, Calculation, SourceLocation

class Lexer:
    """
    Parses Markdown text into a structured Document with MathBlocks and TextBlocks.
    Also parses MathBlocks to identify internal Structure (assignments, evaluations).
    """

    # Regex for finding math blocks: $...$ or $$...$$
    # AND optionally an HTML comment immediately following it on the same line.
    #
    # Supported comment formats:
    # - <!-- [\frac{m}{s}] -->                    → unit conversion (LaTeX notation)
    # - <!-- value:vel -->                        → value lookup
    # - <!-- value:vel [\frac{m}{s}] -->          → value lookup with unit (LaTeX)
    # - <!-- value:vel [\frac{m}{s}] :2 -->       → value lookup with unit and precision
    # - <!-- value:P_{hyd} [\text{kW}] :2 -->     → complex variable names work too
    # - <!-- digits:6 -->                         → config override (expression level)
    # - <!-- digits:6 format:sci -->              → multiple config overrides
    # - <!-- [\frac{m}{s}] digits:4 -->           → unit + config combined
    #
    # Group 1: The math block
    # Group 2: Unit comment content (inside <!-- [...] -->)
    # Group 3: Value comment content (after <!-- value:...)
    # Group 4: Generic comment content (any other HTML comment)

    MATH_BLOCK_RE = re.compile(
        r'(\$\$[\s\S]*?\$\$|\$[^\$\n]*\$)'  # Group 1: math block
        r'(?:'
            r'[ \t]*<!--\s*\[(.*?)\]\s*-->'  # Group 2: unit comment <!-- [...] -->
            r'|'
            r'[ \t]*<!--\s*value:(.*?)\s*-->'  # Group 3: value comment <!-- value:... -->
            r'|'
            r'[ \t]*<!--\s*((?!livemathtex:)[^>]*?)\s*-->'  # Group 4: config comment (not doc directive)
        r')?'
    )

    # Regex for finding operations inside a math block
    # Matches:
    # 1. Unit def:    unit === expr (unit definition)
    # 2. Assignment:  var := expr
    # 3. Evaluation:  expr == result (or just ==)
    # 4. Both:        var := expr == result
    # 5. Symbolic:    expr => result

    # We look for these operators.
    # === Unit definition (must check BEFORE ==)
    # :=  Assignment
    # ==  Evaluation
    # =>  Symbolic

    OPERATOR_RE = re.compile(r'(===|:=|==|=>)')

    # Regex for finding fenced code blocks (``` or ~~~)
    # These should be skipped - we don't process math inside code blocks
    CODE_BLOCK_RE = re.compile(r'```[\s\S]*?```|~~~[\s\S]*?~~~')

    def parse(self, text: str) -> Document:
        """Parse the full document text."""
        children = []
        last_pos = 0

        # Calculate line offsets for location tracking
        line_offsets = [0]
        for match in re.finditer(r'\n', text):
            line_offsets.append(match.end())

        # Find all code block regions to exclude
        code_block_regions = [(m.start(), m.end()) for m in self.CODE_BLOCK_RE.finditer(text)]

        def is_in_code_block(pos: int) -> bool:
            """Check if position is inside a fenced code block."""
            for start, end in code_block_regions:
                if start <= pos < end:
                    return True
            return False

        for match in self.MATH_BLOCK_RE.finditer(text):
            # Skip math blocks inside fenced code blocks
            if is_in_code_block(match.start()):
                continue
            # Text before the math block
            if match.start() > last_pos:
                children.append(TextBlock(content=text[last_pos:match.start()]))

            # The math block itself is Group 1
            full_math_str = match.group(1)
            unit_comment = match.group(2)  # Optional unit from <!-- [unit] -->
            value_comment = match.group(3)  # Optional value from <!-- value... -->
            config_comment = match.group(4)  # Optional config from <!-- key:value -->

            # Handle combined format: <!-- digits:4 [mbar] --> or <!-- [mbar] digits:4 -->
            # If config_comment contains [unit], extract it
            if config_comment and not unit_comment:
                unit_in_config = re.search(r'\[([^\]]+)\]', config_comment)
                if unit_in_config:
                    unit_comment = unit_in_config.group(1)
                    # Remove the unit part from config_comment
                    config_comment = re.sub(r'\s*\[[^\]]+\]\s*', ' ', config_comment).strip()
                    if not config_comment:
                        config_comment = None

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
                value_comment=value_comment,  # New: for <!-- value --> syntax
                config_comment=config_comment,  # New: for expression-level config overrides
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

        Special case: <!-- value --> or <!-- value:unit --> or <!-- value:unit:precision -->
        triggers a "value" operation that displays the value of a previously defined variable.
        """
        content = math_block.inner_content
        lines = content.split('\n')
        calculations = []

        # Check for value display syntax: <!-- value:VAR_LATEX [\unit_latex] :precision -->
        if math_block.value_comment:
            # Parse: "VAR_LATEX [\unit_latex] :precision"
            # Examples:
            #   "vel" → var=vel, unit=None, precision=None
            #   "vel [\frac{m}{s}]" → var=vel, unit=\frac{m}{s}, precision=None
            #   "vel [\frac{m}{s}] :2" → var=vel, unit=\frac{m}{s}, precision=2
            #   "P_{hyd} [\text{kW}] :2" → var=P_{hyd}, unit=\text{kW}, precision=2

            value_str = math_block.value_comment.strip()

            # Extract precision (at end, after :)
            precision = None
            if re.search(r'\s*:\s*(\d+)\s*$', value_str):
                precision_match = re.search(r'\s*:\s*(\d+)\s*$', value_str)
                precision = int(precision_match.group(1))
                value_str = value_str[:precision_match.start()].strip()

            # Extract unit (in square brackets)
            target_unit = None
            unit_match = re.search(r'\s*\[(.*?)\]\s*$', value_str)
            if unit_match:
                target_unit = unit_match.group(1).strip()
                value_str = value_str[:unit_match.start()].strip()

            # Remaining is the variable name (LaTeX notation)
            var_name = value_str.strip()

            calculations.append(
                Calculation(
                    latex=content.strip(),
                    operation="value",
                    target=var_name,  # The LaTeX variable name to look up
                    original_result=None,
                    unit_comment=target_unit,  # Unit in LaTeX notation
                    precision=precision  # Precision for formatting
                )
            )
            return calculations

        # First pass: check if block has ANY livemathtex operators
        has_operators = bool(re.search(r':=|===|==|=>', content))

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

            # Check for "===" (Unit Definition) - MUST come before "==" check!
            unit_def_match = re.search(r'^\s*(.*?)\s*===\s*(.*)', line, re.DOTALL)
            if unit_def_match:
                lhs = unit_def_match.group(1).strip()
                rhs = unit_def_match.group(2).strip()
                calculations.append(
                    Calculation(
                        latex=line,
                        operation="===",
                        target=lhs,  # The unit name being defined
                        original_result=rhs,  # The definition expression
                        unit_comment=math_block.unit_comment
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

    # =========================================================================
    # Configuration Parsing
    # =========================================================================

    # Regex for document-level directives: <!-- livemathtex: key=value, ... -->
    DOCUMENT_DIRECTIVE_RE = re.compile(
        r'<!--\s*livemathtex:\s*([^>]+)\s*-->',
        re.IGNORECASE
    )

    # Regex for expression-level config overrides: <!-- key:value key2:value2 -->
    # These use colon (key:value) to distinguish from document directives (key=value)
    EXPRESSION_CONFIG_RE = re.compile(r'(\w+):(\w+)')

    # Regex for flag-style config (no value): <!-- trailing_zeros -->
    EXPRESSION_FLAG_RE = re.compile(r'\b(trailing_zeros)\b(?!:)')

    def parse_document_directives(self, content: str) -> Dict[str, Any]:
        """
        Extract livemathtex config directives from document content.

        Syntax: <!-- livemathtex: key=value, key2=value2 -->

        These directives set document-wide configuration and are typically
        placed at the top of the document.

        Args:
            content: Full document text

        Returns:
            Dictionary of configuration key-value pairs.
            Empty dict if no directives found.

        Example:
            >>> lexer = Lexer()
            >>> content = '<!-- livemathtex: digits=6, format=engineering -->'
            >>> lexer.parse_document_directives(content)
            {'digits': 6, 'format': 'engineering'}
        """
        directives: Dict[str, Any] = {}

        for match in self.DOCUMENT_DIRECTIVE_RE.finditer(content):
            pairs_str = match.group(1)
            for pair in pairs_str.split(','):
                pair = pair.strip()
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    directives[key] = self._parse_directive_value(value)

        return directives

    def parse_expression_overrides(self, comment: str) -> Dict[str, Any]:
        """
        Parse expression-level config overrides from an inline comment.

        Expression-level overrides use colon syntax (key:value) to distinguish
        from document directives (key=value). They apply only to the single
        calculation they follow.

        Syntax examples:
            <!-- digits:6 -->
            <!-- digits:3 format:scientific -->
            <!-- format:eng trailing_zeros -->
            <!-- digits:6 [kW] -->  (combined with unit conversion)

        Args:
            comment: The comment content (may include other parts like units)

        Returns:
            Dictionary of config overrides. Empty dict if none found.

        Example:
            >>> lexer = Lexer()
            >>> lexer.parse_expression_overrides("digits:6 format:sci")
            {'digits': 6, 'format': 'scientific'}
        """
        if not comment:
            return {}

        overrides: Dict[str, Any] = {}

        # Extract key:value pairs
        for match in self.EXPRESSION_CONFIG_RE.finditer(comment):
            key, value = match.groups()
            # Skip 'output' at expression level - doesn't make sense per-calculation
            if key.lower() == 'output':
                continue
            overrides[key] = self._parse_directive_value(value)

        # Extract flags (key without value = true)
        for match in self.EXPRESSION_FLAG_RE.finditer(comment):
            overrides[match.group(1)] = True

        # Handle format shortcuts
        if overrides.get('format') == 'sci':
            overrides['format'] = 'scientific'
        elif overrides.get('format') == 'eng':
            overrides['format'] = 'engineering'

        return overrides

    def _parse_directive_value(self, value: str) -> Any:
        """
        Parse a directive/config value to appropriate Python type.

        Handles:
        - Booleans: true/false/yes/no/1/0
        - Integers: 123
        - Floats: 1.23, 1e-12
        - Strings: everything else (quotes stripped)

        Args:
            value: String value to parse

        Returns:
            Parsed value in appropriate Python type
        """
        value = value.strip()

        # Boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float (including scientific notation)
        try:
            return float(value)
        except ValueError:
            pass

        # String (remove quotes if present)
        return value.strip('"\'')

    def extract_config_from_comment(self, math_block: MathBlock) -> Dict[str, Any]:
        """
        Extract expression-level config overrides from a MathBlock's comments.

        This uses the config_comment field captured during parsing.
        Config overrides use colon syntax like <!-- digits:6 format:sci -->.

        Args:
            math_block: The MathBlock to check

        Returns:
            Dictionary of config overrides found in comments
        """
        # Use the config_comment field if it was captured during parsing
        if math_block.config_comment:
            return self.parse_expression_overrides(math_block.config_comment)

        return {}
