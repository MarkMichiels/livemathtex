from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceLocation:
    """Location of a node in the source file."""
    start_line: int
    end_line: int
    start_col: int
    end_col: int

@dataclass(kw_only=True, frozen=True)
class Node:
    """Base class for AST nodes."""
    location: SourceLocation | None = None

@dataclass(kw_only=True, frozen=True)
class MathBlock(Node):
    """Represents a LaTeX math block (inline $...$ or display $$...$$)."""
    # Note: Using hash=True/frozen=True allows usage in dict keys
    content: str  # The raw LaTeX content including delimiters
    inner_content: str # Content without delimiters
    is_display: bool = False
    unit_comment: str | None = None  # e.g. "m/s" if <!-- [m/s] --> follows
    value_comment: str | None = None  # e.g. "value" or "value:kW" or "value:kW:2"
    config_comment: str | None = None  # e.g. "digits:6 format:sci" for overrides

@dataclass(kw_only=True, frozen=True)
class Calculation(Node):
    """Represents a calculable portion of a math block."""
    latex: str
    operation: str  # ":=", "==", "=>", "value", or "ERROR"
    target: str | None = None  # Variable name for assignment or lookup
    original_result: str | None = None  # Existing result if present
    unit_comment: str | None = None  # Inherited from block, or target unit for value
    precision: int | None = None  # Decimal places for value display
    error_message: str | None = None  # Error message for invalid syntax

@dataclass(kw_only=True, frozen=True)
class TextBlock(Node):
    """Represents plain Markdown text."""
    content: str

@dataclass(kw_only=True, frozen=True)
class Document(Node):
    """Root node representing the entire parsed document."""
    children: list[TextBlock | MathBlock] = field(default_factory=list)
