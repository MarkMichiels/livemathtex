"""
Intermediate Representation (IR) module for livemathtex.

Provides a JSON-serializable intermediate representation between
parsing and evaluation, inspired by Cortex-JS MathJSON patterns.
"""

from .schema import (
    SymbolMapping,
    SymbolEntry,
    BlockResult,
    LivemathIR,
)
from .normalize import normalize_symbol, denormalize_symbol
from .builder import IRBuilder

__all__ = [
    "SymbolMapping",
    "SymbolEntry",
    "BlockResult",
    "LivemathIR",
    "normalize_symbol",
    "denormalize_symbol",
    "IRBuilder",
]
