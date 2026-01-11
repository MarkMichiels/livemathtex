"""
LiveMathTeX - Mathcad-style recalculation for Markdown.

Public API:
    process_text(content, source="<string>") -> (rendered_output, ir)
    process_text_v3(content, source="<string>", config=None) -> (rendered_output, ir_v3)
    process_file(input_path, output_path=None, verbose=False, ir_output_path=None) -> ir

Configuration:
    LivemathConfig - Configuration options for processing

Result inspection:
    LivemathIR - Intermediate Representation (v2.0)
    LivemathIRV3 - Intermediate Representation (v3.0 with Pint units)

CLI entry point:
    main() - Click CLI application

Example:
    >>> from livemathtex import process_text
    >>> content = "$x := 5$\\n$y := x^2 ==$"
    >>> output, ir = process_text(content)
    >>> print(output)
"""

from .cli import main
from .core import process_text, process_text_v3, process_file
from .config import LivemathConfig
from .ir import LivemathIR
from .ir.schema import LivemathIRV3

__version__ = "0.1.0"

__all__ = [
    # Processing functions
    "process_text",
    "process_text_v3",
    "process_file",
    # Configuration
    "LivemathConfig",
    # Result types
    "LivemathIR",
    "LivemathIRV3",
    # CLI
    "main",
    # Metadata
    "__version__",
]
