"""
Pint Backend for LiveMathTeX.

This module provides a wrapper around the Pint library for unit handling,
ensuring consistent configuration and providing utility functions
for unit validation, conversion, and conflict detection.

Key features:
- Case-sensitive unit parsing (e.g., 'm' vs 'M')
- Custom unit definitions (e.g., 'EUR', 'dag')
- LaTeX-wrapped unit detection (e.g., r'\text{kg}')
- Variable name conflict detection against all known units
"""

from dataclasses import dataclass
from typing import Any, Optional
import re
import pint


# Global Pint UnitRegistry instance
_ureg: Optional[pint.UnitRegistry] = None

# LaTeX wrapper pattern for extracting unit from LaTeX text commands
_LATEX_WRAPPER_PATTERN = re.compile(
    r'^\\(?:text|mathrm|mathit|textit|mathbf)\{([^}]+)\}$'
)


@dataclass
class ParsedQuantity:
    """Result of parsing a value with optional unit."""

    value: float
    unit: Optional[pint.Unit]
    unit_str: Optional[str]
    quantity: Optional[pint.Quantity]


def get_unit_registry() -> pint.UnitRegistry:
    """
    Get the global Pint UnitRegistry instance.

    Initializes the registry if it hasn't been already, configuring it
    for case-sensitive unit parsing and adding custom unit definitions.

    Returns:
        pint.UnitRegistry: The global unit registry.
    """
    global _ureg
    if _ureg is None:
        _ureg = pint.UnitRegistry(case_sensitive=True)
        _setup_custom_units(_ureg)
    return _ureg


def _setup_custom_units(ureg: pint.UnitRegistry) -> None:
    """
    Add custom unit definitions to the registry.

    This includes:
    - Currency units (EUR, USD)
    - Dutch aliases (dag = day)
    - Common abbreviations

    Note: Pint requires unit names to be valid Python identifiers,
    so symbols like '€' and '$' cannot be used directly.
    """
    # Currency as dimensionless placeholder (for calculations)
    # Note: Currency is typically dimensionless in physics context
    try:
        ureg.define('EUR = [currency]')
        ureg.define('USD = [currency]')
    except pint.errors.RedefinitionError:
        pass

    # Dutch language aliases
    try:
        ureg.define('dag = day')
        ureg.define('uur = hour')
        ureg.define('jaar = year')
    except pint.errors.RedefinitionError:
        pass


def reset_unit_registry() -> None:
    """
    Reset the Pint registry.

    Useful for testing to ensure a clean state.
    """
    global _ureg
    _ureg = None


def _unwrap_latex(token: str) -> str:
    """
    Extract unit name from LaTeX text wrappers.

    Args:
        token: The token which might be wrapped in LaTeX commands.

    Returns:
        The unwrapped unit name, or the original token if not wrapped.
    """
    if token is None:
        return ""

    match = _LATEX_WRAPPER_PATTERN.match(token.strip())
    if match:
        return match.group(1)
    return token


def clean_latex_unit(latex_unit: str) -> str:
    """
    Convert LaTeX unit notation to Pint-compatible string.

    Handles:
    - \\text{...} and \\mathrm{...} wrappers
    - LaTeX exponents: ^2 -> **2, ^{-3} -> **-3
    - LaTeX multiplication: \\cdot -> *
    - LaTeX fractions: \\frac{a}{b} -> a/b

    Args:
        latex_unit: The LaTeX-formatted unit string.

    Returns:
        Pint-compatible unit string.

    Examples:
        >>> clean_latex_unit("\\\\text{m/s}^2")
        'm/s**2'
        >>> clean_latex_unit("kg \\\\cdot m/s^2")
        'kg * m/s**2'
    """
    if latex_unit is None:
        return ""

    unit = latex_unit.strip()
    if not unit:
        return ""

    # Remove \\text{...} and \\mathrm{...} wrappers (keep content)
    unit = re.sub(r'\\text\{([^}]+)\}', r'\1', unit)
    unit = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', unit)
    unit = re.sub(r'\\mathit\{([^}]+)\}', r'\1', unit)
    unit = re.sub(r'\\textit\{([^}]+)\}', r'\1', unit)
    unit = re.sub(r'\\mathbf\{([^}]+)\}', r'\1', unit)

    # Convert \\frac{num}{denom} to num/denom
    unit = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', unit)

    # Convert LaTeX exponents to Python: ^2 -> **2, ^{-3} -> **-3
    unit = re.sub(r'\^\{([^}]+)\}', r'**\1', unit)  # braced first
    unit = re.sub(r'\^(-?\d+)', r'**\1', unit)       # then bare

    # Convert LaTeX multiplication to Python (use placeholder to avoid ** conflict)
    unit = unit.replace('\\cdot', '\x00MULT\x00')
    unit = unit.replace('·', '\x00MULT\x00')  # Unicode middle dot

    # Remove any remaining backslashes (LaTeX escapes)
    unit = unit.replace('\\', '')

    # Clean up whitespace around division
    unit = re.sub(r'\s*/\s*', '/', unit)

    # Restore multiplication with proper spacing
    unit = unit.replace('\x00MULT\x00', ' * ')

    # Clean up whitespace around single * (not **)
    # Replace single * with spaces, but preserve **
    unit = re.sub(r'(?<!\*)\*(?!\*)', ' * ', unit)

    # Clean up multiple spaces
    unit = re.sub(r'\s+', ' ', unit)
    unit = unit.strip()

    return unit


def is_unit_token(token: str) -> bool:
    """
    Check if a given token is a recognized unit in the Pint registry.

    Handles LaTeX-wrapped units like r'\\text{kg}' and r'\\mathrm{kW}',
    as well as LaTeX exponents and fractions (ISSUE-005).

    Args:
        token: The string token to check.

    Returns:
        True if the token is a unit, False otherwise.
    """
    if token is None or token == "":
        return False

    ureg = get_unit_registry()

    # Clean LaTeX notation (ISSUE-005: handles \text{m/s}^2 -> m/s**2)
    clean_token = clean_latex_unit(token)
    if not clean_token:
        return False

    try:
        # Attempt to parse the token as a unit.
        # We use ureg.Unit() rather than ureg() to distinguish
        # between units and quantities with magnitude
        ureg.Unit(clean_token)
        return True
    except (pint.errors.UndefinedUnitError, pint.errors.DimensionalityError):
        return False
    except Exception:
        # Catch other potential parsing errors
        return False


def get_unit(token: str) -> Optional[pint.Unit]:
    """
    Get a Pint Unit object for a given token.

    Handles LaTeX-wrapped units and notation (ISSUE-005).

    Args:
        token: The string token representing the unit.

    Returns:
        A pint.Unit object if the token is a recognized unit, None otherwise.
    """
    if token is None or token == "":
        return None

    ureg = get_unit_registry()
    # Clean LaTeX notation (ISSUE-005: handles \text{m/s}^2 -> m/s**2)
    clean_token = clean_latex_unit(token)

    try:
        return ureg.Unit(clean_token)
    except (pint.errors.UndefinedUnitError, pint.errors.DimensionalityError):
        return None
    except Exception:
        return None


def get_unit_description(token: str) -> Optional[str]:
    """
    Get a human-readable description of a unit.

    Args:
        token: The unit token.

    Returns:
        A description like "meter" for "m", or None if not a unit.
    """
    unit = get_unit(token)
    if unit is None:
        return None

    # Try to get the full unit name
    try:
        # The format method gives us the full name
        return str(unit)
    except Exception:
        return None


def get_all_unit_names() -> set[str]:
    """
    Get all known unit names from the registry.

    Returns:
        A set of all unit names (base, derived, prefixed, and custom).
    """
    ureg = get_unit_registry()
    names = set()

    # Get all units from the registry
    # This includes base units, derived units, and aliases
    for name in dir(ureg):
        if name.startswith('_'):
            continue
        try:
            attr = getattr(ureg, name)
            if isinstance(attr, pint.Unit):
                names.add(name)
        except Exception:
            continue

    # Also add common prefixed versions
    prefixes = ['k', 'M', 'G', 'T', 'm', 'µ', 'n', 'p', 'c', 'd']
    base_units = ['W', 'V', 'A', 'Pa', 'J', 'Hz', 'm', 'g', 's', 'bar', 'K', 'N']

    for prefix in prefixes:
        for unit in base_units:
            prefixed = f"{prefix}{unit}"
            if is_unit_token(prefixed):
                names.add(prefixed)

    # Add custom units (only valid Python identifiers)
    names.update(['EUR', 'USD', 'dag', 'uur', 'jaar'])

    return names


def check_variable_name_conflict(name: str) -> Optional[str]:
    """
    Check if a variable name conflicts with a known unit name.

    This is a strict safety check: users cannot define variables with names
    that Pint recognizes as units. This includes:
    - Common units: 'm' (meter), 's' (second), 'kg', etc.
    - Obscure units: 'a' (year/annum), 'b' (barn), 'mass' (milliarcsecond)

    Names with subscripts (containing '_') or superscripts (containing '^')
    are considered explicitly disambiguated and allowed. This allows common
    mathematical notation like R^2 (coefficient of determination) without
    conflicting with unit expressions like R**2 (molar_gas_constant ** 2).

    Args:
        name: The proposed variable name.

    Returns:
        An error message if the name conflicts, None if safe.
    """
    if name is None or name == "":
        return None

    # Names with subscripts or superscripts are explicitly disambiguated
    # ISS-033: R^2 should be allowed as a variable name (R-squared statistic)
    # The ^ character indicates user intent to define a variable, not a unit expression
    if '_' in name or '^' in name:
        return None

    # Use Pint's full unit detection - no exceptions
    if is_unit_token(name):
        desc = get_unit_description(name)
        if desc:
            return f"Variable name '{name}' conflicts with unit '{desc}'. Use a subscript like '{name}_1' or '{name}_var' to disambiguate."
        else:
            return f"Variable name '{name}' conflicts with a known unit. Use a subscript like '{name}_1' to disambiguate."

    return None


# =============================================================================
# ISSUE-002: Dynamic Unit Recognition Functions
# =============================================================================
# These functions replace hardcoded unit lists with dynamic Pint queries.
# Pint is the single source of truth for unit recognition.
# =============================================================================


def is_pint_unit(token: str) -> bool:
    """
    Check if a token is a valid Pint unit (built-in, not custom).
    
    This checks against Pint's native unit registry, NOT custom units
    defined via the === syntax. Use is_known_unit() to check both.
    
    Args:
        token: The string token to check (e.g., 'MWh', 'm/s', 'kg').
    
    Returns:
        True if Pint recognizes this as a unit, False otherwise.
    
    Examples:
        >>> is_pint_unit('MWh')      # True - Pint knows megawatt_hour
        >>> is_pint_unit('kWh/kg')   # True - Pint can parse compound units
        >>> is_pint_unit('EUR')      # True - We defined EUR in Pint setup
        >>> is_pint_unit('€')        # False - Symbol not in Pint
    """
    if not token or token.strip() == "":
        return False
    
    # Clean the token
    clean = _unwrap_latex(token.strip())
    if not clean:
        return False
    
    # Replace common LaTeX notation
    clean = clean.replace('\\cdot', '*').replace('³', '**3').replace('²', '**2')
    
    ureg = get_unit_registry()
    try:
        ureg.parse_expression(clean)
        return True
    except (pint.errors.UndefinedUnitError, pint.errors.DimensionalityError):
        return False
    except Exception:
        return False


def is_custom_unit(token: str) -> bool:
    """
    Check if a token is a custom unit defined via === syntax.

    Custom units are those not in Pint's default registry but defined
    by the user in their document using the === syntax.

    Args:
        token: The string token to check.

    Returns:
        True if this is a user-defined custom unit.

    Examples:
        >>> is_custom_unit('€')       # True if defined with '€ === €'
        >>> is_custom_unit('SEC')     # True if defined with 'SEC === kWh/kg'
        >>> is_custom_unit('MWh')     # False - Pint handles this
    """
    if not token or token.strip() == "":
        return False

    # Check against the custom unit registry
    try:
        registry = get_custom_unit_registry()
        return token in registry._custom_units
    except Exception:
        return False


def is_known_unit(token: str) -> bool:
    """
    Check if a token is a known unit (Pint native OR custom defined).
    
    This is the primary function for checking if a token represents a unit.
    It checks both Pint's built-in registry and custom units from === syntax.
    
    Args:
        token: The string token to check.
    
    Returns:
        True if this is any recognized unit (Pint or custom).
    
    Examples:
        >>> is_known_unit('MWh')  # True - Pint native
        >>> is_known_unit('€')    # True - Custom unit (if defined)
        >>> is_known_unit('foo')  # False - Unknown
    """
    return is_pint_unit(token) or is_custom_unit(token)


# NOTE: pint_to_sympy() and pint_to_sympy_with_prefix() removed in Phase 28.
# SymPy unit conversion is no longer needed - all unit handling uses Pint directly.


def parse_value_with_unit(text: str) -> Optional[ParsedQuantity]:
    """
    Parse a string containing a value with optional unit.

    Handles formats like:
    - "100 kg"
    - "5 kW"
    - "9.81 m/s**2"
    - "1.5e6 W"
    - "42" (unitless)

    Args:
        text: The text to parse.

    Returns:
        A ParsedQuantity with value, unit info, or None if parsing failed.
    """
    if text is None or text.strip() == "":
        return None

    ureg = get_unit_registry()
    text = text.strip()

    try:
        # First, try to parse as a Pint quantity
        quantity = ureg(text)

        if hasattr(quantity, 'magnitude'):
            # It's a quantity with magnitude
            value = float(quantity.magnitude)

            # Check if it's dimensionless
            if quantity.dimensionless:
                return ParsedQuantity(
                    value=value,
                    unit=None,
                    unit_str=None,
                    quantity=quantity
                )
            else:
                return ParsedQuantity(
                    value=value,
                    unit=quantity.units,
                    unit_str=str(quantity.units),
                    quantity=quantity
                )
        else:
            # It's just a number
            return ParsedQuantity(
                value=float(quantity),
                unit=None,
                unit_str=None,
                quantity=None
            )
    except Exception:
        pass

    # Fallback: try to parse as just a number
    try:
        value = float(text)
        return ParsedQuantity(
            value=value,
            unit=None,
            unit_str=None,
            quantity=None
        )
    except ValueError:
        return None


def convert_quantity(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Convert a value from one unit to another.

    Args:
        value: The numeric value.
        from_unit: The source unit.
        to_unit: The target unit.

    Returns:
        The converted value, or None if conversion is not possible.
    """
    ureg = get_unit_registry()

    try:
        quantity = value * ureg(from_unit)
        converted = quantity.to(to_unit)
        return float(converted.magnitude)
    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError):
        return None
    except Exception:
        return None


def to_si_base(value: float, unit: str) -> tuple[float, Optional[str]]:
    """
    Convert a value to SI base units.

    Args:
        value: The numeric value.
        unit: The unit of the value.

    Returns:
        A tuple of (converted_value, si_unit_str).
        Returns (value, None) if conversion fails.
    """
    ureg = get_unit_registry()

    try:
        quantity = value * ureg(unit)
        base = quantity.to_base_units()
        return float(base.magnitude), str(base.units)
    except Exception:
        return value, None


def define_custom_unit(definition: str) -> bool:
    """
    Define a custom unit in the registry.

    Args:
        definition: Unit definition in format "name === expression"
                   e.g., "dag === day" or "mybar === 100000 * Pa"

    Returns:
        True if successful, False otherwise.
    """
    ureg = get_unit_registry()

    # Convert LiveMathTeX syntax to Pint syntax
    # "name === expr" -> "name = expr"
    pint_def = definition.replace("===", "=").strip()

    try:
        ureg.define(pint_def)
        return True
    except (pint.errors.RedefinitionError, pint.errors.DefinitionSyntaxError):
        return False
    except Exception:
        return False


def define_custom_unit_from_latex(unit_name: str, definition: str) -> bool:
    """
    Define a custom unit from LaTeX-style syntax.

    Converts LaTeX notation to Pint-compatible format and registers the unit.

    Args:
        unit_name: The unit name being defined (e.g., "kWh", "€", "MWh")
        definition: The definition expression in LaTeX (e.g., "kW \\cdot h", "1000 \\cdot kWh")

    Returns:
        True if successful, False otherwise.

    Examples:
        define_custom_unit_from_latex("€", "€")  # Base currency unit
        define_custom_unit_from_latex("kWh", "kW \\cdot h")  # Compound unit
        define_custom_unit_from_latex("MWh", "1000 \\cdot kWh")  # Derived unit
    """
    ureg = get_unit_registry()

    # Clean the unit name - replace currency symbols
    clean_name = unit_name.replace('€', 'EUR').replace('$', 'USD')

    # Clean the definition - convert LaTeX to Pint format
    clean_def = definition.replace('\\cdot', '*').replace('\\times', '*')
    clean_def = clean_def.replace('€', 'EUR').replace('$', 'USD')
    clean_def = clean_def.replace('³', '**3').replace('²', '**2')
    clean_def = clean_def.strip()

    # Handle base unit definition (X === X)
    clean_def_normalized = clean_def.replace('EUR', 'EUR').replace('USD', 'USD')
    if clean_name == clean_def_normalized or clean_name == clean_def:
        # This is a base unit - check if already defined
        try:
            ureg.Unit(clean_name)
            return True  # Already exists
        except pint.errors.UndefinedUnitError:
            # Define as new base unit with its own dimension
            try:
                ureg.define(f'{clean_name} = [{clean_name}]')
                return True
            except pint.errors.RedefinitionError:
                return True  # Already defined
            except Exception:
                return False

    # Handle derived/compound units
    try:
        # Check if already defined
        try:
            ureg.Unit(clean_name)
            return True  # Already exists
        except pint.errors.UndefinedUnitError:
            pass

        # Try to define as derived unit
        pint_def = f'{clean_name} = {clean_def}'
        ureg.define(pint_def)
        return True

    except pint.errors.RedefinitionError:
        return True  # Already defined
    except pint.errors.DefinitionSyntaxError:
        return False
    except Exception:
        return False


def create_quantity(value: float, unit: str) -> Optional[pint.Quantity]:
    """
    Create a Pint Quantity from a value and unit string.

    Args:
        value: The numeric value.
        unit: The unit string.

    Returns:
        A pint.Quantity, or None if unit is not recognized.
    """
    ureg = get_unit_registry()

    try:
        return value * ureg(unit)
    except Exception:
        return None


# Backwards compatibility alias
def is_unit(token: str) -> bool:
    """Alias for is_unit_token."""
    return is_unit_token(token)


# =============================================================================
# IR v3.0 Conversion Helpers
# =============================================================================


@dataclass
class ConversionResult:
    """Result of converting a value to base units."""

    original_value: float
    original_unit: Optional[str]
    base_value: float
    base_unit: Optional[str]
    success: bool
    error: Optional[str] = None


def convert_to_base_units(value: float, unit: Optional[str]) -> ConversionResult:
    """
    Convert a value with unit to SI base units.

    This is the primary conversion function for IR v3.0, returning both
    original and base unit representations.

    Args:
        value: The numeric value.
        unit: The unit string (None for dimensionless).

    Returns:
        ConversionResult with both original and base representations.

    Examples:
        >>> convert_to_base_units(50.0, "m³/h")
        ConversionResult(original_value=50.0, original_unit="m³/h",
                        base_value=0.01389, base_unit="m³/s", ...)

        >>> convert_to_base_units(5.0, "kW")
        ConversionResult(original_value=5.0, original_unit="kW",
                        base_value=5000.0, base_unit="kg·m²/s³", ...)
    """
    if unit is None:
        return ConversionResult(
            original_value=value,
            original_unit=None,
            base_value=value,
            base_unit=None,
            success=True
        )

    ureg = get_unit_registry()

    try:
        quantity = value * ureg(unit)
        base = quantity.to_base_units()

        return ConversionResult(
            original_value=value,
            original_unit=unit,
            base_value=float(base.magnitude),
            base_unit=format_pint_unit(base.units),
            success=True
        )
    except Exception as e:
        return ConversionResult(
            original_value=value,
            original_unit=unit,
            base_value=value,
            base_unit=unit,
            success=False,
            error=str(e)
        )


def format_pint_unit(unit: pint.Unit) -> str:
    """
    Format a Pint unit to a clean string representation.

    Args:
        unit: A Pint Unit object.

    Returns:
        A string representation of the unit.

    Examples:
        >>> ureg = get_unit_registry()
        >>> format_pint_unit((5 * ureg.kilowatt).to_base_units().units)
        'kilogram * meter ** 2 / second ** 3'
    """
    if unit.dimensionless:
        return None

    # Get Pint's default string representation
    unit_str = str(unit)

    return unit_str if unit_str else None


def format_unit_latex(unit: Any, original_latex: Optional[str] = None) -> str:
    """
    Format a Pint unit as LaTeX-friendly string.

    If original_latex is provided, uses that for display (preserves user's notation).
    Otherwise, converts Pint unit to readable abbreviation.

    Args:
        unit: A Pint Unit or Quantity, or string representation
        original_latex: Optional original LaTeX string for display

    Returns:
        LaTeX-friendly unit string

    Example:
        kilogram -> "kg"
        meter/second -> "m/s"
        EUR/(kilowatt*hour) -> "€/kWh" (or original_latex if provided)
    """
    # Prefer original LaTeX if provided (preserves user notation)
    if original_latex:
        return original_latex

    if unit is None:
        return ""

    # Get string representation
    unit_str = str(unit)

    # Map Pint full names to common abbreviations
    # Order matters - longer names first to avoid partial replacements
    # Compound units MUST come before their component parts
    reverse_map = [
        # Compound unit patterns (must be first!)
        ('kilowatt_hour', 'kWh'),
        ('megawatt_hour', 'MWh'),
        ('watt_hour', 'Wh'),
        # Prefixed units (longer names before shorter)
        ('kilogram', 'kg'),
        ('milligram', 'mg'),
        ('microgram', 'µg'),
        ('gram', 'g'),
        ('millimeter', 'mm'),
        ('centimeter', 'cm'),
        ('kilometer', 'km'),
        ('meter', 'm'),
        ('millisecond', 'ms'),
        ('microsecond', 'µs'),
        ('nanosecond', 'ns'),
        ('second', 's'),
        ('minute', 'min'),
        ('hour', 'h'),
        ('day', 'd'),
        ('year', 'yr'),
        ('milliliter', 'mL'),
        ('microliter', 'µL'),
        ('liter', 'L'),
        ('gigawatt', 'GW'),
        ('megawatt', 'MW'),
        ('kilowatt', 'kW'),
        ('milliwatt', 'mW'),
        ('watt', 'W'),
        ('megajoule', 'MJ'),
        ('kilojoule', 'kJ'),
        ('millijoule', 'mJ'),
        ('joule', 'J'),
        ('kilonewton', 'kN'),
        ('meganewton', 'MN'),
        ('millinewton', 'mN'),
        ('newton', 'N'),
        ('megapascal', 'MPa'),
        ('kilopascal', 'kPa'),
        ('pascal', 'Pa'),
        ('millibar', 'mbar'),
        ('bar', 'bar'),
        ('kilovolt', 'kV'),
        ('millivolt', 'mV'),
        ('volt', 'V'),
        ('milliampere', 'mA'),
        ('microampere', 'µA'),
        ('ampere', 'A'),
        ('kelvin', 'K'),
        ('gigahertz', 'GHz'),
        ('megahertz', 'MHz'),
        ('kilohertz', 'kHz'),
        ('hertz', 'Hz'),
        ('kilomole', 'kmol'),
        ('millimole', 'mmol'),
        ('mole', 'mol'),
        ('euro', '€'),
        ('EUR', '€'),
        ('USD', '$'),
        ('dollar', '$'),
    ]

    for full, abbrev in reverse_map:
        unit_str = unit_str.replace(full, abbrev)

    # Clean up Pint artifacts for LaTeX compatibility
    unit_str = unit_str.replace(' ** ', '^')
    unit_str = unit_str.replace('**', '^')
    # Use proper LaTeX-compatible separator (will be converted to \cdot later)
    unit_str = unit_str.replace(' * ', ' · ')
    unit_str = unit_str.replace('*', ' · ')
    unit_str = unit_str.replace(' / ', '/')

    return unit_str


@dataclass
class FormulaEvalResult:
    """Result of evaluating a formula with units."""

    original_value: float
    original_unit: Optional[str]
    base_value: float
    base_unit: Optional[str]
    success: bool
    error: Optional[str] = None


# =============================================================================
# LaTeX Unit Parsing (migrated from units.py)
# =============================================================================


def strip_unit_from_value(latex: str) -> tuple[str, Optional[str], Optional[pint.Unit]]:
    """
    Strip the unit from a value expression and parse it.

    Handles multiple patterns:
        "0.139\\ €/kWh"         -> ("0.139", "€/kWh", pint.Unit)
        "100\\ \\text{kg}"      -> ("100", "kg", pint.Unit)
        "5.5\\ \\text{m/s}"     -> ("5.5", "m/s", pint.Unit)
        "1500\\ kWh"            -> ("1500", "kWh", pint.Unit)
        "50 \\frac{m^3}{h}"     -> ("50", "m³/h", pint.Unit)
        "42"                    -> ("42", None, None)

    Returns:
        Tuple of (value_latex, unit_string or None, pint_unit or None)
    """
    latex = latex.strip()

    # Pattern 0: number followed by \frac{numerator}{denominator}
    # Example: "50 \frac{m^{3}}{h}" or "1000 \frac{kg}{m^{3}}" or "44\ \frac{mg}{L}"
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
            # Use parentheses if denominator contains multiplication
            if '*' in denominator or '·' in denominator:
                unit_latex = f"{numerator}/({denominator})"
            else:
                unit_latex = f"{numerator}/{denominator}"
            pint_unit = parse_unit_string(unit_latex)
            if pint_unit is not None:
                return value_part, unit_latex, pint_unit
            else:
                # Unit pattern detected but not recognized
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
        pint_unit = parse_unit_string(unit_part)
        return value_part, unit_part, pint_unit

    # Pattern 2: number followed by backslash-space and unit
    # Example: "0.139\ €/kWh" or "1500\ kWh"
    match = re.match(
        r'^([\d.]+(?:[eE][+-]?\d+)?)\s*\\\s+(.+)$',
        latex
    )
    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        pint_unit = parse_unit_string(unit_part)
        return value_part, unit_part, pint_unit

    # Pattern 3: number followed by direct unit (no backslash)
    # Example: "100 kg" or "5.5 m/s" or "-2 m"
    match = re.match(
        r'^(-?[\d.]+(?:[eE][+-]?\d+)?)\s+([€$]?[a-zA-Z][a-zA-Z0-9/\*\^³²]*)\s*$',
        latex
    )
    if match:
        value_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        # Only accept if it parses as a known unit
        pint_unit = parse_unit_string(unit_part)
        if pint_unit is not None:
            return value_part, unit_part, pint_unit
        else:
            # Looks like a unit pattern but not recognized
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
        pint_unit = parse_unit_string(unit_part)
        if pint_unit is not None:
            return value_part, unit_part, pint_unit

    # No unit found
    return latex, None, None


def _extract_braced_content(s: str) -> tuple[Optional[str], str]:
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
    result = re.sub(r'\^\{3\}', '³', result)
    result = re.sub(r'\^3', '³', result)
    result = re.sub(r'\^\{2\}', '²', result)
    result = re.sub(r'\^2', '²', result)

    # Clean up whitespace
    result = re.sub(r'\s+', '', result)

    return result


def parse_unit_string(unit_str: str) -> Optional[pint.Unit]:
    """
    Parse a unit string into a Pint unit.

    Handles:
        - Simple units: "kg", "m", "s", "EUR"
        - Compound units: "m/s", "EUR/kWh", "mg/L/dag"
        - Powers: "m²", "m^2", "m³", "m^3"
        - Products: "kWh", "kg·m/s²"
        - Currency symbols: "€" -> EUR, "$" -> USD
        - LaTeX notation: "\\text{m/s}^2" (ISSUE-005)

    Returns:
        Pint Unit or None if not recognized
    """
    if not unit_str:
        return None

    ureg = get_unit_registry()

    # Clean LaTeX notation first (ISSUE-005: handles \text{m/s}^2 -> m/s**2)
    unit_str = clean_latex_unit(unit_str)
    if not unit_str:
        return None

    # Replace currency symbols with Pint-compatible names
    unit_str = unit_str.replace('€', 'EUR')
    unit_str = unit_str.replace('$', 'USD')

    # Replace Unicode superscripts with ** (clean_latex_unit handles LaTeX ^)
    unit_str = unit_str.replace('²', '**2').replace('³', '**3')

    # Try direct parse
    try:
        return ureg.Unit(unit_str)
    except (pint.errors.UndefinedUnitError, pint.errors.DimensionalityError):
        pass
    except Exception:
        pass

    # Try parsing compound expressions with custom handling
    return _parse_compound_unit_pint(unit_str)


def _parse_compound_unit_pint(unit_str: str) -> Optional[pint.Unit]:
    """
    Parse compound unit expressions like "EUR/kWh" or "mg/L/dag".

    Handles:
        - Division: a/b/c
        - Multiplication: a*b
        - Powers: a**2, a**3
    """
    ureg = get_unit_registry()

    # Split by / for division
    if '/' in unit_str:
        parts = unit_str.split('/')

        # First part is numerator
        try:
            result = ureg.Unit(parts[0].strip())
        except Exception:
            return None

        # Rest are denominators
        for denom_str in parts[1:]:
            denom_str = denom_str.strip()
            # Handle parentheses
            if denom_str.startswith('(') and denom_str.endswith(')'):
                denom_str = denom_str[1:-1]
            try:
                denom = ureg.Unit(denom_str)
                result = result / denom
            except Exception:
                return None

        return result

    # Handle multiplication
    if '*' in unit_str:
        parts = unit_str.split('*')
        result = None
        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                unit = ureg.Unit(part)
                if result is None:
                    result = unit
                else:
                    result = result * unit
            except Exception:
                return None
        return result

    return None


def convert_value_to_unit(
    value: float,
    from_unit: Optional[str],
    to_unit: str
) -> Optional[float]:
    """
    Convert a value from one unit to another using Pint.

    This is the primary conversion function for the value: directive.
    Handles custom units (EUR, kWh, etc.) and complex unit expressions.

    Args:
        value: The numeric value
        from_unit: The source unit string (or None for dimensionless)
        to_unit: The target unit string (in LaTeX-friendly format)

    Returns:
        The converted value, or None if conversion fails.

    Examples:
        >>> convert_value_to_unit(5000, "kWh", "MWh")
        5.0
        >>> convert_value_to_unit(750, "EUR", "EUR")
        750.0
        >>> convert_value_to_unit(50, "m³/h", "L/s")
        13.889
    """
    ureg = get_unit_registry()

    # Normalize target unit (handle LaTeX-style notation)
    to_unit_clean = to_unit.replace('€', 'EUR').replace('$', 'USD')
    to_unit_clean = to_unit_clean.replace('³', '**3').replace('²', '**2')
    to_unit_clean = to_unit_clean.replace('·', '*')

    try:
        if from_unit:
            # Normalize from_unit too
            from_unit_clean = from_unit.replace('€', 'EUR').replace('$', 'USD')
            from_unit_clean = from_unit_clean.replace('³', '**3').replace('²', '**2')
            from_unit_clean = from_unit_clean.replace('·', '*')

            # Create quantity and convert
            quantity = value * ureg(from_unit_clean)
            converted = quantity.to(to_unit_clean)
            return float(converted.magnitude)
        else:
            # Dimensionless - check if target is also dimensionless
            target_unit = ureg(to_unit_clean)
            if target_unit.dimensionless:
                return value
            return None  # Can't convert dimensionless to dimensioned

    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError) as e:
        # Conversion not possible
        return None
    except Exception:
        return None


def evaluate_formula_with_units(
    expression: str,
    symbol_values: dict[str, tuple[float, Optional[str]]]
) -> FormulaEvalResult:
    """
    Evaluate a formula expression using original units.

    This evaluates the formula with the original units of each symbol,
    then converts the result to base units. This preserves user-friendly
    unit representations in the original output.

    Args:
        expression: Formula using clean IDs (e.g., "v1 * v2 / v3")
        symbol_values: Dict mapping clean ID to (value, unit) tuple

    Returns:
        FormulaEvalResult with both original and base representations.

    Example:
        >>> symbol_values = {
        ...     "v1": (5.0, "L"),
        ...     "v2": (10.0, "min")
        ... }
        >>> result = evaluate_formula_with_units("v1 / v2", symbol_values)
        >>> result.original_unit  # 'L / min'
        >>> result.base_unit      # 'm³ / s'
    """
    ureg = get_unit_registry()

    try:
        # Build namespace with Pint quantities
        namespace = {}
        for sym_id, (val, unit) in symbol_values.items():
            if unit:
                namespace[sym_id] = val * ureg(unit)
            else:
                namespace[sym_id] = val

        # Safe evaluation (only basic arithmetic)
        # Note: In production, use a proper expression parser
        allowed_builtins = {
            'abs': abs,
            'max': max,
            'min': min,
            'pow': pow,
            'round': round,
        }
        result = eval(expression, {"__builtins__": allowed_builtins}, namespace)

        # Extract original and base representations
        if hasattr(result, 'magnitude'):
            orig_val = float(result.magnitude)
            orig_unit = format_pint_unit(result.units)
            base = result.to_base_units()
            base_val = float(base.magnitude)
            base_unit = format_pint_unit(base.units)
        else:
            orig_val = base_val = float(result)
            orig_unit = base_unit = None

        return FormulaEvalResult(
            original_value=orig_val,
            original_unit=orig_unit,
            base_value=base_val,
            base_unit=base_unit,
            success=True
        )

    except Exception as e:
        return FormulaEvalResult(
            original_value=0.0,
            original_unit=None,
            base_value=0.0,
            base_unit=None,
            success=False,
            error=str(e)
        )


# =============================================================================
# Custom Unit Registry (Pure Pint - No SymPy)
# =============================================================================
# Phase 28: SymPy removed. This registry tracks custom units defined via ===
# syntax. Pint handles all actual unit operations.
# =============================================================================


@dataclass
class CustomUnitDefinition:
    """Represents a custom unit definition."""
    name: str
    latex_name: str
    is_base_unit: bool = False
    definition_expr: Optional[str] = None


class CustomUnitRegistry:
    """
    Registry for custom unit definitions (Pure Pint).

    Tracks custom units defined via the `===` syntax:
    - € === €           -> New base unit
    - mbar === bar/1000 -> Derived unit
    - kWh === kW * h    -> Compound unit
    - dag === day       -> Alias

    Note: Actual unit handling is done by Pint. This registry just tracks
    which units were defined as custom so is_custom_unit() works correctly.
    """

    def __init__(self):
        self._custom_units: dict[str, CustomUnitDefinition] = {}
        self._initialize_builtin_units()

    def _initialize_builtin_units(self):
        """Initialize built-in custom units like euro."""
        # Currency units (track them as custom since they're defined in Pint setup)
        self._custom_units['€'] = CustomUnitDefinition(
            name='euro',
            latex_name='€',
            is_base_unit=True,
        )
        self._custom_units['EUR'] = self._custom_units['€']
        self._custom_units['euro'] = self._custom_units['€']

        # Dollar
        self._custom_units['$'] = CustomUnitDefinition(
            name='dollar',
            latex_name='$',
            is_base_unit=True,
        )
        self._custom_units['USD'] = self._custom_units['$']
        self._custom_units['dollar'] = self._custom_units['$']

    def _clean_unit_name(self, name: str) -> str:
        """Clean LaTeX formatting from unit name."""
        name = re.sub(r'\\text\{([^}]+)\}', r'\1', name)
        name = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', name)
        name = name.strip().replace('$', '')
        return name

    def define_unit(self, latex: str) -> Optional[CustomUnitDefinition]:
        """
        Parse and register a unit definition from `===` syntax.

        Returns CustomUnitDefinition if successful, None if not a unit definition.

        Note: Validation for existing units should be done in the caller
        (evaluator._handle_unit_definition) BEFORE adding to Pint registry.
        """
        if '===' not in latex:
            return None

        parts = latex.split('===')
        if len(parts) != 2:
            return None

        left = self._clean_unit_name(parts[0].strip())
        right = self._clean_unit_name(parts[1].strip())

        # Base unit (X === X)
        if left == right:
            return self._define_base_unit(left)

        # Derived/compound/alias
        return self._define_derived_unit(left, right)

    def _define_base_unit(self, name: str) -> CustomUnitDefinition:
        """Define a new base unit."""
        if name in self._custom_units:
            return self._custom_units[name]

        unit_def = CustomUnitDefinition(
            name=name,
            latex_name=name,
            is_base_unit=True,
        )
        self._custom_units[name] = unit_def
        return unit_def

    def _define_derived_unit(self, name: str, expr: str) -> CustomUnitDefinition:
        """Define a derived unit from an expression."""
        unit_def = CustomUnitDefinition(
            name=name,
            latex_name=name,
            is_base_unit=False,
            definition_expr=expr,
        )
        self._custom_units[name] = unit_def
        return unit_def

    def reset(self):
        """Reset to initial state (for testing)."""
        self._custom_units.clear()
        self._initialize_builtin_units()


# Singleton instance
_custom_unit_registry: Optional[CustomUnitRegistry] = None


def get_custom_unit_registry() -> CustomUnitRegistry:
    """Get the singleton CustomUnitRegistry instance."""
    global _custom_unit_registry
    if _custom_unit_registry is None:
        _custom_unit_registry = CustomUnitRegistry()
    return _custom_unit_registry


def reset_custom_unit_registry():
    """Reset the custom unit registry (for testing)."""
    global _custom_unit_registry
    if _custom_unit_registry is not None:
        _custom_unit_registry.reset()


# Backwards compatibility aliases
# evaluator.py imports these names - keep them working
UnitRegistry = CustomUnitRegistry
get_sympy_unit_registry = get_custom_unit_registry
reset_sympy_unit_registry = reset_custom_unit_registry


# =============================================================================
# Backwards Compatibility: sympy_strip_unit_from_value
# =============================================================================
# Phase 28: This function is kept for backwards compatibility but now uses
# the pure Pint strip_unit_from_value() internally.
# =============================================================================


def sympy_strip_unit_from_value(latex: str) -> tuple[str, Optional[str], Optional[Any]]:
    """
    Strip the unit from a value expression and parse it.

    Phase 28: This is now an alias to strip_unit_from_value for backwards
    compatibility. The third return value (previously SymPy unit) is now
    a Pint unit.

    Used by evaluator.py for parsing assignments like "100\\ kg".

    Returns:
        Tuple of (value_latex, unit_string or None, pint_unit or None)
    """
    return strip_unit_from_value(latex)


def reset_unit_registry():
    """Reset both Pint and custom unit registries (for testing)."""
    reset_custom_unit_registry()
    global _ureg
    _ureg = None


# =============================================================================
# ISSUE-006: Dimensional Compatibility Checking
# =============================================================================


def get_unit_dimensionality(unit_expr: Any) -> Optional[str]:
    """
    Get the dimensionality string for a unit expression.

    Uses Pint to determine the physical dimension of a unit.

    Args:
        unit_expr: A Pint unit, SymPy unit Quantity, or unit string

    Returns:
        Dimensionality string like '[mass]', '[length]', '[time]',
        '[length] / [time]', etc. Returns None for dimensionless or invalid.

    Examples:
        >>> get_unit_dimensionality('kg')
        '[mass]'
        >>> get_unit_dimensionality('m/s')
        '[length] / [time]'
        >>> get_unit_dimensionality('kWh')
        '[length] ** 2 * [mass] / [time] ** 2'
    """
    if unit_expr is None:
        return None

    ureg = get_unit_registry()

    def is_dimensionless(dim) -> bool:
        """Check if a Pint dimensionality is dimensionless."""
        # Pint's UnitsContainer is dimensionless if it's empty or contains only dimensionless
        if hasattr(dim, 'dimensionless'):
            return dim.dimensionless
        # For UnitsContainer, check if it's empty (no dimensions)
        return len(dim) == 0

    try:
        # If it's already a Pint unit/quantity with dimensionality
        if hasattr(unit_expr, 'dimensionality'):
            dim = unit_expr.dimensionality
            if is_dimensionless(dim):
                return None
            return str(dim)

        # Convert to string for parsing
        unit_str = str(unit_expr)
        if not unit_str or unit_str.strip() == '':
            return None

        # Clean LaTeX notation
        unit_str = clean_latex_unit(unit_str)
        if not unit_str:
            return None

        # Replace currency symbols
        unit_str = unit_str.replace('€', 'EUR').replace('$', 'USD')

        # Try to parse as Pint unit
        pint_unit = ureg.Unit(unit_str)
        dim = pint_unit.dimensionality
        if is_dimensionless(dim):
            return None
        return str(dim)

    except Exception:
        # Try as a quantity (might have magnitude)
        try:
            pint_qty = ureg.parse_expression(str(unit_expr))
            if hasattr(pint_qty, 'dimensionality'):
                dim = pint_qty.dimensionality
                if is_dimensionless(dim):
                    return None
                return str(dim)
        except Exception:
            pass

    return None


def are_dimensions_compatible(dim1: Optional[str], dim2: Optional[str]) -> bool:
    """
    Check if two dimensionalities are compatible for addition/subtraction.

    Compatible means:
    - Both are None (dimensionless)
    - Both have the same dimensionality string

    Args:
        dim1: First dimensionality string or None
        dim2: Second dimensionality string or None

    Returns:
        True if compatible, False otherwise
    """
    # Both dimensionless
    if dim1 is None and dim2 is None:
        return True

    # One has units, other doesn't
    if dim1 is None or dim2 is None:
        # For now, treat mixing unit + unitless as incompatible
        # This catches cases like "5 kg + 3" which is likely an error
        return False

    # Compare dimensionality strings
    return dim1 == dim2


# =============================================================================
# Backwards Compatibility: PintEvaluationError
# =============================================================================
# Phase 28: SymPy AST evaluation removed. This exception class kept for
# backwards compatibility in case any code catches it.
# =============================================================================


class PintEvaluationError(Exception):
    """Error during Pint-based evaluation."""
    pass
