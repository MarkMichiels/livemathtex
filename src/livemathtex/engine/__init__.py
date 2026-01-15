"""
LiveMathTeX Engine - Calculation and evaluation.

Components:
- Evaluator: Main calculation engine
- SymbolTable: Variable and function storage
- UnitRegistry: Custom unit definitions (via Pint backend)
"""

from .evaluator import Evaluator
from .symbols import SymbolTable, SymbolValue
from .pint_backend import (
    UnitRegistry,
    get_custom_unit_registry as get_unit_registry,
    reset_unit_registry,
)

__all__ = [
    "Evaluator",
    "SymbolTable",
    "SymbolValue",
    "UnitRegistry",
    "get_unit_registry",
    "reset_unit_registry",
]
