"""
CalcuLaTeX - Live LaTeX calculations in Markdown documents.

Write calculations in natural mathematical notation:
- Use := for assignment (definition)
- Use = or = ? for evaluation (request calculated value)

Example:
    $x := 42$
    $y := x^2$
    $y = ?$  →  $y = 1764$
"""

__version__ = "0.1.0"

from calculatex.processor import CalcuLaTeXProcessor
from calculatex.engine import CalculationEngine

__all__ = ["CalcuLaTeXProcessor", "CalculationEngine", "__version__"]
