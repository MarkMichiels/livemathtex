from dataclasses import dataclass, field
from typing import Optional, List, Union, Any

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
    location: Optional[SourceLocation] = None

@dataclass(kw_only=True, frozen=True)
class MathBlock(Node):
    """Represents a LaTeX math block (inline $...$ or display $$...$$)."""
    # Note: Using hash=True/frozen=True allows usage in dict keys
    content: str  # The raw LaTeX content including delimiters
    inner_content: str # Content without delimiters
    is_display: bool = False
    unit_comment: Optional[str] = None # e.g. "m/s" if <!-- [m/s] --> follows

@dataclass(kw_only=True, frozen=True)
class Calculation(Node):
    """Represents a calculable portion of a math block."""
    latex: str
    operation: str  # ":=", "==", "=>", or "ERROR"
    target: Optional[str] = None  # Variable name for assignment
    original_result: Optional[str] = None  # Existing result if present
    unit_comment: Optional[str] = None # Inherited from block
    error_message: Optional[str] = None # Error message for invalid syntax

@dataclass(kw_only=True, frozen=True)
class TextBlock(Node):
    """Represents plain Markdown text."""
    content: str

@dataclass(kw_only=True, frozen=True)
class Document(Node):
    """Root node representing the entire parsed document."""
    children: List[Union[TextBlock, MathBlock]] = field(default_factory=list)
