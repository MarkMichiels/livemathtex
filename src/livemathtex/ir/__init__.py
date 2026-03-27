"""
Intermediate Representation (IR) module for livemathtex.

Version 3.0 - Schema with simple internal IDs:
- Symbols with original and SI-converted values
- Custom unit definitions
- Errors array with line numbers

Symbol normalization uses the v0/f0/x0 architecture:
- Variables: v0, v1, v2, ...
- Formulas: f0, f1, f2, ...
- Parameters: x0, x1, x2, ...

See symbols.py NameGenerator for the implementation.
"""

from .builder import IRBuilder
from .schema import (
    IRError,
    LivemathIR,
    SymbolEntry,
    ValueWithUnit,
)

__all__ = [
    "ValueWithUnit",
    "SymbolEntry",
    "IRError",
    "LivemathIR",
    "IRBuilder",
]
