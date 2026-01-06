"""
LiveMathTeX Unit System - Custom unit definitions and mappings.

Supports the `===` syntax for defining custom units:
- Base unit:     € === €           (new unit)
- Derived unit:  mbar === bar/1000 (scaled from existing)
- Compound unit: kWh === kW * h    (product of units)
- Alias:         dag === day       (rename existing)

Uses SymPy's physics.units module for calculations.
"""

import re
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field

import sympy
from sympy.physics.units import Quantity, UnitSystem
from sympy.physics.units.systems import SI
from sympy.physics.units import (
    # Base SI units
    meter, kilogram, second, ampere, kelvin, mole, candela,
    # Derived units
    newton, joule, watt, pascal, hertz, volt, ohm,
    # Common units
    gram, milligram, liter, hour, minute, day,
    bar, psi,
    # Prefixes
    kilo, mega, giga, milli, micro, nano, centi,
)


# =============================================================================
# Built-in Unit Abbreviation Mappings
# =============================================================================

# Map common abbreviations to SymPy units
UNIT_ABBREVIATIONS: Dict[str, Any] = {
    # Mass
    'kg': kilogram,
    'g': gram,
    'mg': milligram,

    # Length
    'm': meter,
    'cm': centi * meter,
    'mm': milli * meter,
    'km': kilo * meter,

    # Time
    's': second,
    'h': hour,
    'min': minute,
    'dag': day,  # Dutch for "day"

    # Volume
    'L': liter,
    'l': liter,  # lowercase also accepted
    'mL': milli * liter,
    'ml': milli * liter,

    # Power/Energy
    'W': watt,
    'kW': kilo * watt,
    'MW': mega * watt,
    'J': joule,
    'kJ': kilo * joule,

    # Pressure
    'Pa': pascal,
    'kPa': kilo * pascal,
    'bar': bar,
    'mbar': milli * bar,

    # Electrical
    'V': volt,
    'A': ampere,
    'mA': milli * ampere,

    # Temperature
    'K': kelvin,
}

# Compound units (parsed from expressions like "m/s" or "kg/m³")
COMPOUND_UNIT_PATTERNS = {
    'm/s': meter / second,
    'm/s²': meter / second**2,
    'm/s^2': meter / second**2,
    'kg/m³': kilogram / meter**3,
    'kg/m^3': kilogram / meter**3,
    'kWh': kilo * watt * hour,
    'Wh': watt * hour,
    'mg/L': milligram / liter,
    'mg/L/dag': milligram / liter / day,
    'mg/L/day': milligram / liter / day,
}


# =============================================================================
# Custom Unit Registry
# =============================================================================

@dataclass
class UnitDefinition:
    """Represents a custom unit definition."""
    name: str
    latex_name: str
    sympy_unit: Any
    is_base_unit: bool = False
    definition_expr: Optional[str] = None


class UnitRegistry:
    """
    Registry for custom unit definitions.

    Handles the `===` syntax:
    - € === €           → New base unit
    - mbar === bar/1000 → Derived unit
    - kWh === kW * h    → Compound unit
    - dag === day       → Alias
    """

    def __init__(self):
        self._custom_units: Dict[str, UnitDefinition] = {}
        self._initialize_builtin_units()

    def _initialize_builtin_units(self):
        """Initialize built-in custom units like euro."""
        # Currency units (not in SymPy by default)
        euro = Quantity('euro', abbrev='EUR')
        self._custom_units['€'] = UnitDefinition(
            name='euro',
            latex_name='€',
            sympy_unit=euro,
            is_base_unit=True,
        )
        self._custom_units['EUR'] = self._custom_units['€']
        self._custom_units['euro'] = self._custom_units['€']

        # Dollar
        dollar = Quantity('dollar', abbrev='USD')
        self._custom_units['$'] = UnitDefinition(
            name='dollar',
            latex_name='$',
            sympy_unit=dollar,
            is_base_unit=True,
        )
        self._custom_units['USD'] = self._custom_units['$']
        self._custom_units['dollar'] = self._custom_units['$']

    def define_unit(self, latex: str) -> Optional[UnitDefinition]:
        """
        Parse and register a unit definition from `===` syntax.

        Examples:
            "€ === €"           → Base unit
            "mbar === bar/1000" → Derived unit
            "kWh === kW * h"    → Compound unit
            "dag === day"       → Alias

        Returns:
            UnitDefinition if successful, None if not a unit definition.
        """
        # Check for === operator
        if '===' not in latex:
            return None

        parts = latex.split('===')
        if len(parts) != 2:
            return None

        left = parts[0].strip()
        right = parts[1].strip()

        # Clean LaTeX formatting
        left = self._clean_unit_name(left)
        right = self._clean_unit_name(right)

        # Case 1: Base unit (X === X)
        if left == right:
            return self._define_base_unit(left)

        # Case 2: Try to parse as derived/compound/alias
        return self._define_derived_unit(left, right)

    def _clean_unit_name(self, name: str) -> str:
        """Clean LaTeX formatting from unit name."""
        # Remove \text{...}
        name = re.sub(r'\\text\{([^}]+)\}', r'\1', name)
        # Remove \mathrm{...}
        name = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', name)
        # Remove spaces
        name = name.strip()
        # Remove $ signs (math mode)
        name = name.replace('$', '')
        return name

    def _define_base_unit(self, name: str) -> UnitDefinition:
        """Define a new base unit."""
        # Check if already defined
        if name in self._custom_units:
            return self._custom_units[name]

        # Create new SymPy Quantity
        sympy_unit = Quantity(name, abbrev=name)

        unit_def = UnitDefinition(
            name=name,
            latex_name=name,
            sympy_unit=sympy_unit,
            is_base_unit=True,
        )

        self._custom_units[name] = unit_def
        return unit_def

    def _define_derived_unit(self, name: str, expr: str) -> UnitDefinition:
        """Define a derived unit from an expression."""
        # Try to evaluate the expression
        sympy_unit = self._parse_unit_expression(expr)

        if sympy_unit is None:
            # If we can't parse, treat as alias attempt
            # Check if right side is a known unit
            if expr in UNIT_ABBREVIATIONS:
                sympy_unit = UNIT_ABBREVIATIONS[expr]
            elif expr in self._custom_units:
                sympy_unit = self._custom_units[expr].sympy_unit
            else:
                # Create as new base unit
                sympy_unit = Quantity(name, abbrev=name)

        unit_def = UnitDefinition(
            name=name,
            latex_name=name,
            sympy_unit=sympy_unit,
            is_base_unit=False,
            definition_expr=expr,
        )

        self._custom_units[name] = unit_def
        return unit_def

    def _parse_unit_expression(self, expr: str) -> Optional[Any]:
        """
        Parse a unit expression like "bar/1000" or "kW * h".

        Returns SymPy unit expression or None if cannot parse.
        """
        # Replace LaTeX operators
        expr = expr.replace('\\cdot', '*')
        expr = expr.replace('\\times', '*')
        expr = expr.replace('\\div', '/')

        # Build namespace with known units
        namespace = dict(UNIT_ABBREVIATIONS)
        for name, unit_def in self._custom_units.items():
            namespace[name] = unit_def.sympy_unit

        # Add SymPy units directly
        namespace.update({
            'bar': bar,
            'day': day,
            'hour': hour,
            'watt': watt,
            'liter': liter,
            'gram': gram,
            'meter': meter,
            'second': second,
            'kilogram': kilogram,
            'kilo': kilo,
            'milli': milli,
            'micro': micro,
        })

        try:
            result = eval(expr, {"__builtins__": {}}, namespace)
            return result
        except Exception:
            return None

    def get_unit(self, name: str) -> Optional[Any]:
        """
        Get a unit by name (abbreviation or custom).

        Checks:
        1. Custom units (including currency)
        2. Built-in abbreviations
        3. Compound unit patterns
        """
        # Clean the name
        clean_name = self._clean_unit_name(name)

        # Check custom units
        if clean_name in self._custom_units:
            return self._custom_units[clean_name].sympy_unit

        # Check built-in abbreviations
        if clean_name in UNIT_ABBREVIATIONS:
            return UNIT_ABBREVIATIONS[clean_name]

        # Check compound patterns
        if clean_name in COMPOUND_UNIT_PATTERNS:
            return COMPOUND_UNIT_PATTERNS[clean_name]

        return None

    def parse_unit_from_latex(self, latex: str) -> Optional[Any]:
        """
        Parse a unit from LaTeX like `\\text{kg}` or `\\text{EUR/kWh}`.

        Returns SymPy unit or None if not recognized.
        """
        # Extract from \text{...}
        match = re.search(r'\\text\{([^}]+)\}', latex)
        if match:
            unit_str = match.group(1)
        else:
            unit_str = latex

        # Try direct lookup
        unit = self.get_unit(unit_str)
        if unit is not None:
            return unit

        # Try to parse as compound (e.g., "EUR/kWh")
        return self._parse_compound_unit(unit_str)

    def _parse_compound_unit(self, unit_str: str) -> Optional[Any]:
        """Parse compound units like EUR/kWh or mg/L/dag."""
        # Split by / and *
        parts = re.split(r'[/\*]', unit_str)
        operators = re.findall(r'[/\*]', unit_str)

        if len(parts) < 2:
            return None

        # Get first unit
        result = self.get_unit(parts[0])
        if result is None:
            return None

        # Apply operators
        for i, op in enumerate(operators):
            next_unit = self.get_unit(parts[i + 1])
            if next_unit is None:
                return None

            if op == '/':
                result = result / next_unit
            else:  # '*'
                result = result * next_unit

        return result

    def list_units(self) -> Dict[str, str]:
        """List all available units (built-in + custom)."""
        result = {}

        # Built-in abbreviations
        for abbrev in UNIT_ABBREVIATIONS:
            result[abbrev] = 'built-in'

        # Custom units
        for name, unit_def in self._custom_units.items():
            if unit_def.is_base_unit:
                result[name] = 'base unit'
            else:
                result[name] = f'derived: {unit_def.definition_expr}'

        return result


# =============================================================================
# Global Registry Instance
# =============================================================================

# Singleton instance for the application
_unit_registry: Optional[UnitRegistry] = None


def get_unit_registry() -> UnitRegistry:
    """Get the global unit registry instance."""
    global _unit_registry
    if _unit_registry is None:
        _unit_registry = UnitRegistry()
    return _unit_registry


def reset_unit_registry():
    """Reset the unit registry (for testing)."""
    global _unit_registry
    _unit_registry = None


# =============================================================================
# Helper Functions
# =============================================================================

def strip_unit_from_value(latex: str) -> Tuple[str, Optional[str]]:
    """
    Strip the unit from a value expression.

    Example:
        "100\\ \\text{kg}" -> ("100", "kg")
        "5.5\\ \\text{m/s}" -> ("5.5", "m/s")
        "42" -> ("42", None)

    Returns:
        Tuple of (value_latex, unit_string or None)
    """
    # Pattern: number followed by \text{...} or \mathrm{...}
    match = re.match(
        r'^(.+?)\s*\\?\s*\\(?:text|mathrm)\{([^}]+)\}\s*$',
        latex.strip()
    )

    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        return value_part, unit_part

    # No unit found
    return latex.strip(), None


def format_unit_latex(unit: Any) -> str:
    """
    Format a SymPy unit as LaTeX.

    Example:
        kilogram -> "kg"
        meter/second -> "m/s"
    """
    if unit is None:
        return ""

    # Get string representation
    unit_str = str(unit)

    # Map back to common abbreviations
    reverse_map = {
        'kilogram': 'kg',
        'gram': 'g',
        'meter': 'm',
        'second': 's',
        'hour': 'h',
        'day': 'dag',
        'liter': 'L',
        'watt': 'W',
        'joule': 'J',
        'newton': 'N',
        'pascal': 'Pa',
        'volt': 'V',
        'ampere': 'A',
        'kelvin': 'K',
        'euro': '€',
        'dollar': '$',
    }

    for full, abbrev in reverse_map.items():
        unit_str = unit_str.replace(full, abbrev)

    return unit_str
