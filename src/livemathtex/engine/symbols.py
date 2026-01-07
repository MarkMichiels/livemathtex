"""
Symbol management for livemathtex.

This module provides:
- SymbolValue: Stores both original and SI-converted values
- NameGenerator: Creates unique v_{n} IDs for latex2sympy
- SymbolTable: Manages variable state during evaluation
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SymbolValue:
    """
    Holds the value and metadata of a variable.

    Stores both original (user-input) and SI-converted values for:
    - Display: Show user's original units
    - Calculation: Use SI units internally
    - Validation: Check conversion round-trip

    Attributes:
        original_value: User's input value (numeric part)
        original_unit: User's input unit string (e.g., "m³/h", "kW")
        si_value: SI-converted value (numeric part)
        si_unit: SI unit (SymPy unit expression)
        valid: Whether conversion was successful
        raw_latex: The LaTeX string of the RHS (definition expression)
        latex_name: The original LaTeX form of the variable name (LHS)
        internal_id: Internal ID for latex2sympy (e.g., "v_{0}")
    """
    original_value: Optional[float] = None
    original_unit: Optional[str] = None
    si_value: Any = None  # SymPy object or number
    si_unit: Optional[Any] = None  # SymPy unit expression
    valid: bool = True
    raw_latex: str = ""
    latex_name: str = ""
    internal_id: str = ""

    @property
    def value(self) -> Any:
        """Get the SI value (for calculations). Backwards compatible."""
        return self.si_value

    @property
    def unit(self) -> Optional[Any]:
        """Get the SI unit (for calculations). Backwards compatible."""
        return self.si_unit

    @property
    def unit_latex(self) -> str:
        """Get the original unit string for display. Backwards compatible."""
        return self.original_unit or ""

    @property
    def value_with_unit(self) -> Any:
        """Get the full SI value including unit (for calculations)."""
        if self.si_unit is not None:
            return self.si_value * self.si_unit
        return self.si_value


class NameGenerator:
    """
    Generates unique internal names for latex2sympy.

    Uses simple format: v_{0}, v_{1}, v_{2}, ... for variables
                        f_{0}, f_{1}, f_{2}, ... for functions

    This format is 100% compatible with latex2sympy (no parsing issues).
    """

    def __init__(self):
        self._var_counter = 0
        self._func_counter = 0
        # Bidirectional mapping
        self._latex_to_internal: Dict[str, str] = {}
        self._internal_to_latex: Dict[str, str] = {}

    def get_or_create_var(self, latex_name: str) -> str:
        """
        Get existing internal name or create new one for a variable.

        Args:
            latex_name: Original LaTeX variable name (e.g., "N_{MPC}")

        Returns:
            Internal name (e.g., "v_{0}")
        """
        if latex_name in self._latex_to_internal:
            return self._latex_to_internal[latex_name]

        internal = f"v_{{{self._var_counter}}}"
        self._var_counter += 1
        self._latex_to_internal[latex_name] = internal
        self._internal_to_latex[internal] = latex_name
        return internal

    def get_or_create_func(self, latex_name: str) -> str:
        """
        Get existing internal name or create new one for a function.

        Args:
            latex_name: Original LaTeX function name (e.g., "f(x)")

        Returns:
            Internal name (e.g., "f_{0}")
        """
        if latex_name in self._latex_to_internal:
            return self._latex_to_internal[latex_name]

        internal = f"f_{{{self._func_counter}}}"
        self._func_counter += 1
        self._latex_to_internal[latex_name] = internal
        self._internal_to_latex[internal] = latex_name
        return internal

    def get_internal(self, latex_name: str) -> Optional[str]:
        """Get internal name for a LaTeX name, or None if not registered."""
        return self._latex_to_internal.get(latex_name)

    def get_latex(self, internal_name: str) -> Optional[str]:
        """Get original LaTeX name for an internal name, or None if not registered."""
        return self._internal_to_latex.get(internal_name)

    def all_mappings(self) -> Dict[str, str]:
        """Return all latex -> internal mappings."""
        return self._latex_to_internal.copy()

    def clear(self):
        """Reset the generator."""
        self._var_counter = 0
        self._func_counter = 0
        self._latex_to_internal.clear()
        self._internal_to_latex.clear()


class SymbolTable:
    """
    Manages the state of variables during document processing.

    Architecture:
    - Each variable has an original LaTeX name (e.g., "P_{LED,out}")
    - Each variable gets an internal ID (e.g., "v_{0}") for latex2sympy
    - Stores both original and SI-converted values
    - The mapping is stored for output conversion back to LaTeX
    """

    def __init__(self):
        self._symbols: Dict[str, SymbolValue] = {}
        self._names = NameGenerator()

    def set(
        self,
        name: str,
        value: Any = None,
        unit: Any = None,
        raw_latex: str = "",
        latex_name: str = "",
        unit_latex: str = "",
        original_value: Optional[float] = None,
        original_unit: Optional[str] = None,
        valid: bool = True,
    ):
        """
        Define a variable with both original and SI values.

        Args:
            name: Internal normalized name (e.g., "P_LED_out") - for backwards compat
            value: The SI-converted value (SymPy object or number) - numeric part only
            unit: Optional SymPy unit expression (SI unit)
            raw_latex: The LaTeX string of the RHS expression
            latex_name: The original LaTeX form of the variable name
                       (e.g., "P_{LED,out}"). Used for expression rewriting.
            unit_latex: The original unit string for display (e.g., "€/kWh")
                       (backwards compat, prefer original_unit)
            original_value: User's input value (numeric, before SI conversion)
            original_unit: User's input unit string (e.g., "m³/h")
            valid: Whether the unit conversion was successful
        """
        # Generate internal ID for latex2sympy
        internal_id = ""
        if latex_name:
            internal_id = self._names.get_or_create_var(latex_name)

        # Handle backwards compatibility: use unit_latex as original_unit if not provided
        if original_unit is None and unit_latex:
            original_unit = unit_latex

        self._symbols[name] = SymbolValue(
            original_value=original_value,
            original_unit=original_unit,
            si_value=value,
            si_unit=unit,
            valid=valid,
            raw_latex=raw_latex,
            latex_name=latex_name,
            internal_id=internal_id,
        )

    def get(self, name: str) -> Optional[SymbolValue]:
        """Retrieve a variable."""
        return self._symbols.get(name)

    def get_internal_id(self, latex_name: str) -> Optional[str]:
        """Get the internal ID (v_{n}) for a LaTeX variable name."""
        return self._names.get_internal(latex_name)

    def get_latex_name(self, internal_id: str) -> Optional[str]:
        """Get the original LaTeX name for an internal ID."""
        return self._names.get_latex(internal_id)

    def get_all_latex_to_internal(self) -> Dict[str, str]:
        """Get all LaTeX -> internal ID mappings for expression rewriting."""
        return self._names.all_mappings()

    def clear(self):
        """Reset the table."""
        self._symbols.clear()
        self._names.clear()

    def all_names(self) -> list:
        """Return all defined symbol names."""
        return list(self._symbols.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._symbols
