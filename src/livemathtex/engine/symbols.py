"""
Symbol management for livemathtex.

This module provides:
- SymbolValue: Stores both original and SI-converted values
- NameGenerator: Creates unique IDs for variables, formulas, and parameters
- SymbolTable: Manages variable state during evaluation

ID Convention (v3.0):
- v1, v2, v3... for values (numeric with optional unit)
- f1, f2, f3... for formulas (computed from other symbols)
- x1, x2, x3... for function parameters (local scope)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


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
        si_unit: SI unit string (Pint-based in v3.0)
        valid: Whether conversion was successful
        raw_latex: The LaTeX string of the RHS (definition expression)
        latex_name: The original LaTeX form of the variable name (LHS)
        internal_id: Internal ID (v3.0: "v1", "f1"; legacy: "v_{0}")
        line: Source line number where this symbol was defined

        # v3.0 formula tracking fields
        is_formula: Whether this is a formula (not a direct value)
        formula_expression: Expression using clean IDs (e.g., "v1 * v2")
        depends_on: List of clean IDs this formula depends on
        parameters: List of clean parameter IDs for functions (e.g., ["x1", "x2"])
        parameter_latex: Original LaTeX names for parameters (e.g., ["x", "y"])
    """
    original_value: Optional[float] = None
    original_unit: Optional[str] = None
    si_value: Any = None  # Pint Quantity or number (or SymPy in legacy mode)
    si_unit: Optional[Any] = None  # Pint unit string (or SymPy unit in legacy mode)
    valid: bool = True
    raw_latex: str = ""
    latex_name: str = ""
    internal_id: str = ""
    line: int = 0

    # v3.0 formula tracking fields
    is_formula: bool = False
    formula_expression: str = ""
    depends_on: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    parameter_latex: List[str] = field(default_factory=list)

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
    Generates unique internal names for symbols.

    v3.0 format (clean IDs):
        v1, v2, v3... for values (numeric with optional unit)
        f1, f2, f3... for formulas (computed from other symbols)
        x1, x2, x3... for function parameters (local scope within a function)

    Legacy format (for backwards compatibility):
        v_{0}, v_{1}, v_{2}... for variables
        f_{0}, f_{1}, f_{2}... for functions
    """

    def __init__(self, use_clean_ids: bool = False):
        """
        Initialize name generator.

        Args:
            use_clean_ids: If True, use v1/f1/x1 format (v3.0).
                          If False, use v_{0}/f_{0} format (legacy).
                          Default is False for backwards compatibility.
        """
        self._value_counter = 0
        self._formula_counter = 0
        self._param_counter = 0
        self._use_clean_ids = use_clean_ids
        # Bidirectional mapping
        self._latex_to_internal: Dict[str, str] = {}
        self._internal_to_latex: Dict[str, str] = {}

    def next_value_id(self) -> str:
        """
        Generate next value ID (v1, v2, v3...).

        For symbols that are direct values with optional units.
        """
        self._value_counter += 1
        if self._use_clean_ids:
            return f"v{self._value_counter}"
        return f"v_{{{self._value_counter - 1}}}"

    def next_formula_id(self) -> str:
        """
        Generate next formula ID (f1, f2, f3...).

        For symbols that are computed from other symbols.
        """
        self._formula_counter += 1
        if self._use_clean_ids:
            return f"f{self._formula_counter}"
        return f"f_{{{self._formula_counter - 1}}}"

    def next_param_id(self) -> str:
        """
        Generate next parameter ID (x1, x2, x3...).

        For function parameters (local scope within a function definition).
        """
        self._param_counter += 1
        if self._use_clean_ids:
            return f"x{self._param_counter}"
        return f"x_{{{self._param_counter - 1}}}"

    def reset_param_counter(self) -> None:
        """Reset parameter counter for new function scope."""
        self._param_counter = 0

    def get_or_create_var(self, latex_name: str) -> str:
        """
        Get existing internal name or create new one for a variable.

        Args:
            latex_name: Original LaTeX variable name (e.g., "N_{MPC}")

        Returns:
            Internal name (e.g., "v1" or "v_{0}" depending on mode)
        """
        if latex_name in self._latex_to_internal:
            return self._latex_to_internal[latex_name]

        internal = self.next_value_id()
        self._latex_to_internal[latex_name] = internal
        self._internal_to_latex[internal] = latex_name
        return internal

    def get_or_create_func(self, latex_name: str) -> str:
        """
        Get existing internal name or create new one for a formula.

        Args:
            latex_name: Original LaTeX name (e.g., "A_{pipe}")

        Returns:
            Internal name (e.g., "f1" or "f_{0}" depending on mode)
        """
        if latex_name in self._latex_to_internal:
            return self._latex_to_internal[latex_name]

        internal = self.next_formula_id()
        self._latex_to_internal[latex_name] = internal
        self._internal_to_latex[internal] = latex_name
        return internal

    def register_id(self, latex_name: str, internal_id: str) -> None:
        """
        Register a specific ID for a LaTeX name.

        Used when we want to control the exact ID assignment.
        """
        self._latex_to_internal[latex_name] = internal_id
        self._internal_to_latex[internal_id] = latex_name

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
        self._value_counter = 0
        self._formula_counter = 0
        self._param_counter = 0
        self._latex_to_internal.clear()
        self._internal_to_latex.clear()


class SymbolTable:
    """
    Manages the state of variables during document processing.

    Architecture:
    - Each variable has an original LaTeX name (e.g., "P_{LED,out}")
    - Each variable gets an internal ID (e.g., "v1" for v3.0, "v_{0}" legacy)
    - Stores both original and SI-converted values
    - The mapping is stored for output conversion back to LaTeX
    """

    def __init__(self, use_clean_ids: bool = False):
        """
        Initialize symbol table.

        Args:
            use_clean_ids: If True, use v1/f1/x1 format (v3.0).
                          If False, use v_{0}/f_{0} format (legacy).
                          Default is False for backwards compatibility.
        """
        self._symbols: Dict[str, SymbolValue] = {}
        self._names = NameGenerator(use_clean_ids=use_clean_ids)
        self._use_clean_ids = use_clean_ids

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
        line: int = 0,
        # v3.0 formula tracking fields
        is_formula: bool = False,
        formula_expression: str = "",
        depends_on: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        parameter_latex: Optional[List[str]] = None,
    ):
        """
        Define a variable with both original and SI values.

        Args:
            name: Internal normalized name (e.g., "P_LED_out") - for backwards compat
            value: The SI-converted value (Pint Quantity or number) - numeric part only
            unit: SI unit string (Pint-based in v3.0)
            raw_latex: The LaTeX string of the RHS expression
            latex_name: The original LaTeX form of the variable name
                       (e.g., "P_{LED,out}"). Used for expression rewriting.
            unit_latex: The original unit string for display (e.g., "€/kWh")
                       (backwards compat, prefer original_unit)
            original_value: User's input value (numeric, before SI conversion)
            original_unit: User's input unit string (e.g., "m³/h")
            valid: Whether the unit conversion was successful
            line: Source line number where this symbol was defined

            # v3.0 formula tracking fields
            is_formula: Whether this is a formula (not a direct value)
            formula_expression: Expression using clean IDs (e.g., "v1 * v2")
            depends_on: List of clean IDs this formula depends on
            parameters: List of clean parameter IDs for functions
            parameter_latex: Original LaTeX names for parameters
        """
        # Generate internal ID - use formula ID if it's a formula
        internal_id = ""
        if latex_name:
            if is_formula:
                internal_id = self._names.get_or_create_func(latex_name)
            else:
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
            line=line,
            is_formula=is_formula,
            formula_expression=formula_expression,
            depends_on=depends_on or [],
            parameters=parameters or [],
            parameter_latex=parameter_latex or [],
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
