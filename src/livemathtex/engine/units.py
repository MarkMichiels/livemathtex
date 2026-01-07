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
        4. Parse compound expressions (kW*h, m/s, etc.)
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

        # Try to parse compound expressions like kW*h, m/s, etc.
        if '*' in clean_name or '/' in clean_name:
            return self._parse_compound_unit(clean_name)

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

def strip_unit_from_value(latex: str) -> Tuple[str, Optional[str], Optional[Any]]:
    """
    Strip the unit from a value expression and parse it.

    Handles multiple patterns:
        "0.139\\ €/kWh"         -> ("0.139", "€/kWh", euro/(kilo*watt*hour))
        "100\\ \\text{kg}"      -> ("100", "kg", kilogram)
        "5.5\\ \\text{m/s}"     -> ("5.5", "m/s", meter/second)
        "1500\\ kWh"            -> ("1500", "kWh", kilo*watt*hour)
        "50 \\frac{m^3}{h}"     -> ("50", "m³/h", meter**3/hour)
        "42"                    -> ("42", None, None)

    Returns:
        Tuple of (value_latex, unit_string or None, sympy_unit or None)
    """
    latex = latex.strip()

    # Pattern 0: number followed by \frac{numerator}{denominator}
    # Example: "50 \frac{m^{3}}{h}" or "1000 \frac{kg}{m^{3}}" or "44\ \frac{mg}{L}"
    # Use helper to handle nested braces like {m^{3}}
    # Note: \s*\\?\s* handles both "44 \frac" and "44\ \frac" (LaTeX thin space)
    frac_match = re.match(r'^(-?[\d.]+(?:[eE][+-]?\d+)?)\s*\\?\s*\\frac', latex)
    if frac_match:
        value_part = frac_match.group(1).strip()
        rest = latex[frac_match.end():]
        # Extract numerator and denominator handling nested braces
        numerator, rest = _extract_braced_content(rest)
        denominator, _ = _extract_braced_content(rest)
        if numerator is not None and denominator is not None:
            # Clean up LaTeX: m^{3} -> m³, \text{kg} -> kg, \cdot -> *
            numerator = _clean_unit_latex(numerator)
            denominator = _clean_unit_latex(denominator)
            # Use parentheses if denominator contains multiplication to preserve order
            if '*' in denominator or '·' in denominator:
                unit_latex = f"{numerator}/({denominator})"
            else:
                unit_latex = f"{numerator}/{denominator}"
            sympy_unit = _parse_unit_string(unit_latex)
            if sympy_unit is not None:
                return value_part, unit_latex, sympy_unit
            else:
                # Unit pattern detected but not recognized - this is an error
                raise ValueError(f"Unrecognized unit: \\frac{{{numerator}}}{{{denominator}}}. "
                               f"Define it first with '$$ {unit_latex} === ... $$'")

    # Pattern 1: number followed by \text{...} or \mathrm{...}
    # Example: "100\ \text{kg}" or "5.5 \text{m/s}"
    match = re.match(
        r'^(.+?)\s*\\?\s*\\(?:text|mathrm)\{([^}]+)\}\s*$',
        latex
    )
    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        sympy_unit = _parse_unit_string(unit_part)
        return value_part, unit_part, sympy_unit

    # Pattern 2: number followed by backslash-space and unit
    # Example: "0.139\ €/kWh" or "1500\ kWh"
    match = re.match(
        r'^([\d.]+(?:[eE][+-]?\d+)?)\s*\\\s+(.+)$',
        latex
    )
    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        sympy_unit = _parse_unit_string(unit_part)
        return value_part, unit_part, sympy_unit

    # Pattern 3: number followed by direct unit (no backslash)
    # Example: "100 kg" or "5.5 m/s" or "-2 m"
    # Be careful: only match if unit looks like a unit (not a variable)
    match = re.match(
        r'^(-?[\d.]+(?:[eE][+-]?\d+)?)\s+([€$]?[a-zA-Z][a-zA-Z0-9/\*\^³²]*)\s*$',
        latex
    )
    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        # Only accept if it parses as a known unit
        sympy_unit = _parse_unit_string(unit_part)
        if sympy_unit is not None:
            return value_part, unit_part, sympy_unit
        else:
            # Looks like a unit pattern but not recognized
            # Only raise error if it really looks like a unit (not a single letter that could be a variable)
            if len(unit_part) > 1 or unit_part in ['m', 's', 'g', 'A', 'K', 'N', 'J', 'W', 'V', 'L', 'h']:
                raise ValueError(f"Unrecognized unit: '{unit_part}'. "
                               f"Define it first with '$$ {unit_part} === ... $$'")

    # Pattern 4: number with unit symbol directly attached (currency)
    # Example: "0.139€/kWh"
    match = re.match(
        r'^([\d.]+(?:[eE][+-]?\d+)?)\s*([€$][a-zA-Z0-9/\*\^³²]*)\s*$',
        latex
    )
    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        sympy_unit = _parse_unit_string(unit_part)
        if sympy_unit is not None:
            return value_part, unit_part, sympy_unit

    # No unit found
    return latex, None, None


def _extract_braced_content(s: str) -> Tuple[Optional[str], str]:
    """
    Extract content from balanced braces, handling nesting.

    Example:
        "{m^{3}}rest" -> ("m^{3}", "rest")
        "{kg}{m^{3}}" -> ("kg", "{m^{3}}")

    Returns:
        Tuple of (content or None, remaining string)
    """
    s = s.strip()
    if not s or s[0] != '{':
        return None, s

    depth = 0
    start = 0
    for i, c in enumerate(s):
        if c == '{':
            if depth == 0:
                start = i + 1
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return s[start:i], s[i+1:]

    return None, s


def _clean_unit_latex(unit_latex: str) -> str:
    """
    Clean LaTeX unit notation to simple format.

    Converts:
        "\\text{mg}" -> "mg"
        "\\mathrm{kg}" -> "kg"
        "m^{3}" -> "m³"
        "m^3"   -> "m³"
        "m^{2}" -> "m²"
        "s^{2}" -> "s²"
        "\\cdot" -> "*"

    Returns:
        Cleaned unit string
    """
    result = unit_latex

    # Remove \text{} and \mathrm{} wrappers
    result = re.sub(r'\\text\{([^}]+)\}', r'\1', result)
    result = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', result)

    # Replace \cdot with *
    result = result.replace(r'\cdot', '*')
    result = result.replace('·', '*')  # Unicode middle dot

    # Replace LaTeX power notation with Unicode
    # Note: braces need to be escaped in regex
    result = re.sub(r'\^\{3\}', '³', result)
    result = re.sub(r'\^3', '³', result)
    result = re.sub(r'\^\{2\}', '²', result)
    result = re.sub(r'\^2', '²', result)

    # Clean up whitespace
    result = re.sub(r'\s+', '', result)

    return result


def _parse_unit_string(unit_str: str) -> Optional[Any]:
    """
    Parse a unit string into a SymPy unit expression.

    Handles:
        - Simple units: "kg", "m", "s", "€"
        - Compound units: "m/s", "€/kWh", "mg/L/dag"
        - Powers: "m²", "m^2", "m³", "m^3"
        - Products: "kWh", "kg·m/s²"

    Returns:
        SymPy unit expression or None if not recognized
    """
    if not unit_str:
        return None

    # Clean the unit string
    unit_str = unit_str.strip()

    # Replace Unicode superscripts
    unit_str = unit_str.replace('²', '^2').replace('³', '^3')

    # Replace · with *
    unit_str = unit_str.replace('·', '*').replace('\\cdot', '*')

    # Get the global registry
    registry = get_unit_registry()

    # Try direct lookup first (handles custom units like €)
    result = registry.get_unit(unit_str)
    if result is not None:
        return result

    # Try parsing as compound unit
    result = registry.parse_unit_from_latex(unit_str)
    if result is not None:
        return result

    # Try parsing compound expressions manually
    return _parse_compound_unit_expr(unit_str, registry)


def _parse_compound_unit_expr(unit_str: str, registry: 'UnitRegistry') -> Optional[Any]:
    """
    Parse compound unit expressions like "€/kWh" or "mg/L/dag".

    Handles:
        - Division: a/b/c = a / (b * c)
        - Multiplication: a*b or ab (for known units)
        - Powers: a^2, a^3
    """
    import sympy

    # Split by / for division
    if '/' in unit_str:
        parts = unit_str.split('/')

        # First part is numerator
        numerator = _parse_single_unit(parts[0], registry)
        if numerator is None:
            return None

        # Rest are denominators
        result = numerator
        for denom_str in parts[1:]:
            denom = _parse_single_unit(denom_str, registry)
            if denom is None:
                return None
            result = result / denom

        return result

    # No division, try single unit
    return _parse_single_unit(unit_str, registry)


def _parse_single_unit(unit_str: str, registry: 'UnitRegistry') -> Optional[Any]:
    """
    Parse a single unit (possibly with power or parentheses).

    Examples:
        "kg" -> kilogram
        "m^2" -> meter**2
        "kWh" -> kilo*watt*hour
        "(L*dag)" -> liter * day
    """
    import sympy

    unit_str = unit_str.strip()
    if not unit_str:
        return None

    # Handle parentheses: (L*dag) -> multiply contents
    if unit_str.startswith('(') and unit_str.endswith(')'):
        inner = unit_str[1:-1]
        # Parse as multiplication
        if '*' in inner:
            parts = inner.split('*')
            result = None
            for part in parts:
                part_unit = _parse_single_unit(part.strip(), registry)
                if part_unit is None:
                    return None
                if result is None:
                    result = part_unit
                else:
                    result = result * part_unit
            return result
        else:
            # Just remove parentheses and parse
            return _parse_single_unit(inner, registry)

    # Handle powers: m^2, s^-1
    if '^' in unit_str:
        base, exp = unit_str.split('^', 1)
        base_unit = _parse_single_unit(base.strip(), registry)
        if base_unit is None:
            return None
        try:
            exp_val = int(exp.strip())
            return base_unit ** exp_val
        except ValueError:
            return None

    # Handle multiplication: L*dag
    if '*' in unit_str:
        parts = unit_str.split('*')
        result = None
        for part in parts:
            part_unit = _parse_single_unit(part.strip(), registry)
            if part_unit is None:
                return None
            if result is None:
                result = part_unit
            else:
                result = result * part_unit
        return result

    # Try direct lookup
    result = registry.get_unit(unit_str)
    if result is not None:
        return result

    # Try built-in abbreviations
    if unit_str in UNIT_ABBREVIATIONS:
        return UNIT_ABBREVIATIONS[unit_str]

    # Try compound patterns
    if unit_str in COMPOUND_UNIT_PATTERNS:
        return COMPOUND_UNIT_PATTERNS[unit_str]

    # Try with SI prefixes
    prefixed = _try_prefixed_unit(unit_str)
    if prefixed is not None:
        return prefixed

    return None


def _try_prefixed_unit(unit_str: str) -> Optional[Any]:
    """
    Try to parse a unit with SI prefix (k, M, m, µ, n, c).

    Examples:
        "kW" -> kilo * watt
        "mm" -> milli * meter
        "MHz" -> mega * hertz
    """
    from sympy.physics.units.prefixes import kilo, mega, giga, milli, micro, nano, centi

    if len(unit_str) < 2:
        return None

    # SI prefix mapping (first char)
    prefix_map = {
        'k': kilo,
        'M': mega,
        'G': giga,
        'c': centi,
        'µ': micro,
        'u': micro,
        'n': nano,
    }

    # Try prefix + base unit
    first_char = unit_str[0]
    if first_char in prefix_map:
        base_str = unit_str[1:]

        # Check if base is a known unit
        if base_str in UNIT_ABBREVIATIONS:
            return prefix_map[first_char] * UNIT_ABBREVIATIONS[base_str]

    # Special case: mm (milli-meter, not mega-meter)
    if unit_str == 'mm':
        return milli * meter

    return None


def format_unit_latex(unit: Any, original_latex: Optional[str] = None) -> str:
    """
    Format a SymPy unit as LaTeX.

    If original_latex is provided, uses that for display (preserves user's notation).
    Otherwise, converts SymPy unit to readable abbreviation.

    Example:
        kilogram -> "kg"
        meter/second -> "m/s"
        euro/(kilowatt*hour) -> "€/kWh" (or original_latex if provided)
    """
    # Prefer original LaTeX if provided (preserves user notation)
    if original_latex:
        return original_latex

    if unit is None:
        return ""

    # Get string representation
    unit_str = str(unit)

    # Map back to common abbreviations
    reverse_map = {
        'kilogram': 'kg',
        'gram': 'g',
        'milligram': 'mg',
        'meter': 'm',
        'millimeter': 'mm',
        'centimeter': 'cm',
        'kilometer': 'km',
        'second': 's',
        'millisecond': 'ms',
        'minute': 'min',
        'hour': 'h',
        'day': 'dag',
        'liter': 'L',
        'milliliter': 'mL',
        'watt': 'W',
        'kilowatt': 'kW',
        'megawatt': 'MW',
        'joule': 'J',
        'kilojoule': 'kJ',
        'newton': 'N',
        'pascal': 'Pa',
        'kilopascal': 'kPa',
        'bar': 'bar',
        'millibar': 'mbar',
        'volt': 'V',
        'ampere': 'A',
        'milliampere': 'mA',
        'kelvin': 'K',
        'hertz': 'Hz',
        'kilohertz': 'kHz',
        'megahertz': 'MHz',
        'mole': 'mol',
        'euro': '€',
        'dollar': '$',
    }

    for full, abbrev in reverse_map.items():
        unit_str = unit_str.replace(full, abbrev)

    # Clean up SymPy artifacts
    unit_str = unit_str.replace('**', '^')
    unit_str = unit_str.replace('*', '·')

    return unit_str
