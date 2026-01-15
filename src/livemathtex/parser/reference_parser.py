"""
Cross-reference parser for LiveMathTeX.

Detects and parses `{{...}}` references in text outside math blocks.

Example:
    The maximum capacity is {{C_{max}}} kg.
    → After processing: The maximum capacity is 550 kg<!-- {{C_{max}}} -->.

The HTML comment preserves the original reference for clear/reprocess cycles.
"""

from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class Reference:
    """A parsed cross-reference.

    Attributes:
        content: The content inside the braces (e.g., "C_{max}")
        start: Start position in the document
        end: End position in the document (exclusive)
    """
    content: str
    start: int
    end: int


@dataclass
class ProcessedReference:
    """A processed cross-reference with its replacement.

    Attributes:
        original: The original Reference
        value: Evaluated value string (e.g., "550")
        unit: Unit string if any (e.g., "kg")
        error: Error message if evaluation failed
    """
    original: Reference
    value: Optional[str] = None
    unit: Optional[str] = None
    error: Optional[str] = None

    @property
    def formatted(self) -> str:
        """Get the formatted replacement text with HTML comment."""
        if self.error:
            return f"{{{{ERROR: {self.error}}}}}"

        result = self.value or ""
        if self.unit:
            result = f"{result} {self.unit}"

        # Preserve original in HTML comment for clear/reprocess
        return f"{result}<!-- {{{{{self.original.content}}}}} -->"


def find_math_block_ranges(content: str) -> List[tuple]:
    """Find all ranges of math blocks to exclude from reference search.

    Returns:
        List of (start, end) tuples for math blocks
    """
    ranges = []

    # Display math blocks: $$...$$ (non-greedy)
    for match in re.finditer(r'\$\$[\s\S]*?\$\$', content):
        ranges.append((match.start(), match.end()))

    # Inline math blocks: $...$ (non-greedy, exclude $$ already matched)
    # Must not start or end at positions already in a display block
    display_positions = set()
    for start, end in ranges:
        display_positions.update(range(start, end))

    for match in re.finditer(r'\$[^$\n]+?\$', content):
        if match.start() not in display_positions:
            ranges.append((match.start(), match.end()))

    # Code blocks: ```...``` (fenced)
    for match in re.finditer(r'```[\s\S]*?```', content):
        ranges.append((match.start(), match.end()))

    # Inline code: `...`
    for match in re.finditer(r'`[^`]+?`', content):
        ranges.append((match.start(), match.end()))

    # HTML comments (but not our marker comments)
    # Skip comments that look like: <!-- {{...}} --> (our markers)
    for match in re.finditer(r'<!--(?!.*\{\{)[\s\S]*?-->', content):
        ranges.append((match.start(), match.end()))

    return sorted(ranges)


def is_in_excluded_range(pos: int, ranges: List[tuple]) -> bool:
    """Check if a position is within any excluded range."""
    for start, end in ranges:
        if start <= pos < end:
            return True
    return False


def extract_references(content: str) -> List[Reference]:
    r"""Extract all {{...}} references from content.

    Args:
        content: Document content

    Returns:
        List of Reference objects

    Notes:
        - Skips references inside math blocks, code blocks, and HTML comments
        - Handles escaped \{{ which should be treated as literal {{
        - Handles nested braces like {{C_{max}}} correctly
    """
    references = []
    excluded_ranges = find_math_block_ranges(content)

    # Pattern: {{ followed by content with balanced braces until }}
    # Must not be escaped (preceded by \)
    # Content can include single braces {} but must end with }}
    # Use: match everything including nested {} until we hit }}
    pattern = r'(?<!\\)\{\{((?:[^{}]|\{[^{}]*\})*)\}\}'

    for match in re.finditer(pattern, content):
        start = match.start()

        # Skip if inside excluded range
        if is_in_excluded_range(start, excluded_ranges):
            continue

        references.append(Reference(
            content=match.group(1).strip(),
            start=start,
            end=match.end()
        ))

    return references


def find_processed_references(content: str) -> List[tuple]:
    """Find previously processed references (value<!-- {{ref}} -->).

    Returns:
        List of (full_match_start, full_match_end, reference_content) tuples
    """
    results = []

    # Pattern: numeric value with optional unit/symbol followed by <!-- {{...}} -->
    # Value format: number + optional unit/symbol (e.g., "550 kg", "93.8%", "1.5 m/s")
    # Content can include nested {} for LaTeX subscripts
    pattern = r'([\d.]+(?:[%]|(?:\s+[A-Za-z/]+))?)\s*<!-- \{\{((?:[^{}]|\{[^{}]*\})*)\}\} -->'

    for match in re.finditer(pattern, content):
        results.append((
            match.start(),
            match.end(),
            match.group(2).strip()  # The original reference content
        ))

    return results


def restore_references(content: str) -> tuple:
    """Restore processed references back to original {{...}} syntax.

    This is used by clear_text to undo reference substitution.

    Args:
        content: Document content with processed references

    Returns:
        Tuple of (cleared_content, count_of_restored_references)
    """
    processed = find_processed_references(content)

    if not processed:
        return content, 0

    # Apply replacements in reverse order to maintain offsets
    result = content
    for start, end, ref_content in reversed(processed):
        replacement = f"{{{{{ref_content}}}}}"
        result = result[:start] + replacement + result[end:]

    return result, len(processed)
