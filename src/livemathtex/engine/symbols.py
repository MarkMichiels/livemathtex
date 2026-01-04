from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SymbolValue:
    """Holds the value and metadata of a variable."""
    value: Any  # SymPy object or number
    unit: Optional[Any] = None # Pint unit object (Phase 2)
    raw_latex: str = "" # The latex string used to define it

class SymbolTable:
    """
    Manages the state of variables during document processing.
    """
    def __init__(self):
        self._symbols: Dict[str, SymbolValue] = {}
        
    def set(self, name: str, value: Any, unit=None, raw_latex=""):
        """Define a variable."""
        self._symbols[name] = SymbolValue(value=value, unit=unit, raw_latex=raw_latex)
        
    def get(self, name: str) -> Optional[SymbolValue]:
        """Retrieve a variable."""
        return self._symbols.get(name)
        
    def clear(self):
        """Reset the table."""
        self._symbols.clear()
        
    def __contains__(self, name: str) -> bool:
        return name in self._symbols
