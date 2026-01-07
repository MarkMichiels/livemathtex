"""
Intermediate Representation (IR) module for livemathtex.

Version 2.0 - Simplified schema:
- Symbols with original and SI-converted values
- Custom unit definitions
- Errors array with line numbers

Symbol normalization uses the v_{n}/f_{n} architecture:
- Variables: v_{0}, v_{1}, v_{2}, ...
- Functions: f_{0}, f_{1}, f_{2}, ...

See symbols.py NameGenerator for the implementation.
"""

from .schema import (
    ValueWithUnit,
    SymbolEntry,
    IRError,
    LivemathIR,
)
from .builder import IRBuilder

__all__ = [
    "ValueWithUnit",
    "SymbolEntry",
    "IRError",
    "LivemathIR",
    "IRBuilder",
]
