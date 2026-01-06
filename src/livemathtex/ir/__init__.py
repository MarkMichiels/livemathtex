"""
Intermediate Representation (IR) module for livemathtex.

Provides a JSON-serializable intermediate representation between
parsing and evaluation.

Symbol normalization uses the v_{n}/f_{n} architecture:
- Variables: v_{0}, v_{1}, v_{2}, ...
- Functions: f_{0}, f_{1}, f_{2}, ...

See symbols.py NameGenerator for the implementation.
"""

from .schema import (
    SymbolMapping,
    SymbolEntry,
    BlockResult,
    LivemathIR,
)
from .builder import IRBuilder

__all__ = [
    "SymbolMapping",
    "SymbolEntry",
    "BlockResult",
    "LivemathIR",
    "IRBuilder",
]
