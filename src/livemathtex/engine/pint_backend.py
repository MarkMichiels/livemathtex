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


def is_unit_token(token: str) -> bool:
    """
    Check if a given token is a recognized unit in the Pint registry.

    Handles LaTeX-wrapped units like r'\\text{kg}' and r'\\mathrm{kW}'.

    Args:
        token: The string token to check.

    Returns:
        True if the token is a unit, False otherwise.
    """
    if token is None or token == "":
        return False

    ureg = get_unit_registry()

    # Unwrap LaTeX commands
    clean_token = _unwrap_latex(token)
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

    Args:
        token: The string token representing the unit.

    Returns:
        A pint.Unit object if the token is a recognized unit, None otherwise.
    """
    if token is None or token == "":
        return None

    ureg = get_unit_registry()
    clean_token = _unwrap_latex(token)

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

    Names with subscripts (containing '_') are considered explicitly
    disambiguated and allowed.

    Args:
        name: The proposed variable name.

    Returns:
        An error message if the name conflicts, None if safe.
    """
    if name is None or name == "":
        return None

    # Names with subscripts are explicitly disambiguated
    if '_' in name:
        return None

    # Use Pint's full unit detection - no exceptions
    if is_unit_token(name):
        desc = get_unit_description(name)
        if desc:
            return f"Variable name '{name}' conflicts with unit '{desc}'. Use a subscript like '{name}_1' or '{name}_var' to disambiguate."
        else:
            return f"Variable name '{name}' conflicts with a known unit. Use a subscript like '{name}_1' to disambiguate."

    return None


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


@dataclass
class FormulaEvalResult:
    """Result of evaluating a formula with units."""

    original_value: float
    original_unit: Optional[str]
    base_value: float
    base_unit: Optional[str]
    success: bool
    error: Optional[str] = None


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
