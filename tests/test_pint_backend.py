"""
Tests for the Pint-based unit backend.

These tests verify that the Pint backend correctly:
- Detects unit tokens
- Validates variable names against unit conflicts
- Parses quantities with units
- Converts between units
"""

import pytest

from livemathtex.engine.pint_backend import (
    is_unit_token,
    get_all_unit_names,
    check_variable_name_conflict,
    get_unit_description,
    parse_value_with_unit,
    convert_quantity,
    to_si_base,
    define_custom_unit,
    reset_unit_registry,
    clean_latex_unit,
)


class TestIsUnitToken:
    """Tests for is_unit_token function."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_unit_registry()

    # Base SI units
    def test_base_units(self):
        """Base SI units should be recognized."""
        assert is_unit_token("m") is True
        assert is_unit_token("s") is True
        assert is_unit_token("kg") is True
        assert is_unit_token("A") is True
        assert is_unit_token("K") is True
        assert is_unit_token("mol") is True

    # Derived units
    def test_derived_units(self):
        """Common derived units should be recognized."""
        assert is_unit_token("N") is True
        assert is_unit_token("J") is True
        assert is_unit_token("W") is True
        assert is_unit_token("Pa") is True
        assert is_unit_token("Hz") is True
        assert is_unit_token("V") is True

    # Prefixed units
    def test_prefixed_units(self):
        """Prefixed units should be recognized."""
        assert is_unit_token("kW") is True
        assert is_unit_token("MW") is True
        assert is_unit_token("mW") is True
        assert is_unit_token("km") is True
        assert is_unit_token("mm") is True
        assert is_unit_token("kPa") is True
        assert is_unit_token("mbar") is True

    # Compound units
    def test_compound_units(self):
        """Compound units should be recognized."""
        assert is_unit_token("m/s") is True
        assert is_unit_token("kg/m**3") is True
        assert is_unit_token("kW*h") is True

    # Custom units (defined in registry)
    def test_custom_units(self):
        """Custom defined units should be recognized."""
        assert is_unit_token("EUR") is True
        assert is_unit_token("USD") is True
        # dag is defined as alias for day
        assert is_unit_token("dag") is True

    # Not units
    def test_not_units(self):
        """Non-unit tokens should not be recognized."""
        assert is_unit_token("foo") is False
        assert is_unit_token("bar_var") is False
        assert is_unit_token("P_out") is False
        assert is_unit_token("xyz_value") is False
        assert is_unit_token("myvar") is False
        assert is_unit_token("") is False
        assert is_unit_token(None) is False

    # Obscure units that Pint recognizes
    def test_obscure_units(self):
        """Pint recognizes obscure units - we want to catch these too."""
        # 'a' is recognized as year (annum)
        assert is_unit_token("a") is True
        # 'b' is recognized as barn (nuclear physics unit)
        assert is_unit_token("b") is True
        # 'mass' is recognized as milliarcsecond (mas)
        assert is_unit_token("mass") is True

    # LaTeX-wrapped units
    def test_latex_wrapped_units(self):
        """Units wrapped in LaTeX commands should be recognized."""
        assert is_unit_token(r"\text{kg}") is True
        assert is_unit_token(r"\mathrm{kW}") is True


class TestVariableNameConflict:
    """Tests for variable name conflict detection."""

    def setup_method(self):
        reset_unit_registry()

    def test_single_letter_unit_conflict(self):
        """Single-letter unit names should conflict."""
        # These are common traps
        error = check_variable_name_conflict("m")
        assert error is not None
        assert "meter" in error.lower()

        error = check_variable_name_conflict("g")
        assert error is not None
        assert "gram" in error.lower()

        error = check_variable_name_conflict("s")
        assert error is not None
        assert "second" in error.lower()

    def test_multi_letter_unit_conflict(self):
        """Multi-letter unit names should conflict."""
        error = check_variable_name_conflict("kg")
        assert error is not None

        error = check_variable_name_conflict("Pa")
        assert error is not None

    def test_subscripted_names_allowed(self):
        """Names with subscripts should be allowed (explicitly disambiguated)."""
        assert check_variable_name_conflict("m_1") is None
        assert check_variable_name_conflict("g_acc") is None
        assert check_variable_name_conflict("s_total") is None
        assert check_variable_name_conflict("P_out") is None

    def test_non_unit_names_allowed(self):
        """Names that aren't units should be allowed."""
        # Names with subscripts are always allowed (explicitly disambiguated)
        assert check_variable_name_conflict("m_1") is None
        assert check_variable_name_conflict("a_val") is None
        assert check_variable_name_conflict("mass_obj") is None
        # Names that Pint doesn't recognize as units
        assert check_variable_name_conflict("foo") is None
        assert check_variable_name_conflict("myvar") is None
        assert check_variable_name_conflict("xyz_value") is None

    def test_obscure_unit_names_rejected(self):
        """Even obscure unit names should be rejected (strict mode)."""
        # 'a' = year, 'b' = barn, 'mass' = milliarcsecond
        error = check_variable_name_conflict("a")
        assert error is not None
        assert "year" in error.lower()

        error = check_variable_name_conflict("b")
        assert error is not None
        assert "barn" in error.lower()

        error = check_variable_name_conflict("mass")
        assert error is not None
        assert "milliarcsecond" in error.lower()


class TestParseValueWithUnit:
    """Tests for parsing values with units."""

    def setup_method(self):
        reset_unit_registry()

    def test_simple_value_unit(self):
        """Parse simple value + unit."""
        result = parse_value_with_unit("100 kg")
        assert result is not None
        assert result.value == 100.0
        assert result.unit_str is not None
        assert "kg" in str(result.unit_str) or "kilogram" in str(result.unit_str)

    def test_prefixed_unit(self):
        """Parse value with prefixed unit."""
        result = parse_value_with_unit("5 kW")
        assert result is not None
        assert result.value == 5.0

    def test_unitless_value(self):
        """Parse unitless value."""
        result = parse_value_with_unit("42")
        assert result is not None
        assert result.value == 42.0
        assert result.unit is None

    def test_decimal_value(self):
        """Parse decimal value with unit."""
        result = parse_value_with_unit("9.81 m/s**2")
        assert result is not None
        assert abs(result.value - 9.81) < 0.001

    def test_scientific_notation(self):
        """Parse scientific notation."""
        result = parse_value_with_unit("1.5e6 W")
        assert result is not None
        assert result.value == 1.5e6


class TestUnitConversion:
    """Tests for unit conversion."""

    def setup_method(self):
        reset_unit_registry()

    def test_prefix_conversion(self):
        """Convert between prefixed units."""
        result = convert_quantity(5, "kW", "W")
        assert result is not None
        assert result == 5000.0

        result = convert_quantity(1000, "mm", "m")
        assert result is not None
        assert result == 1.0

    def test_time_conversion(self):
        """Convert between time units."""
        result = convert_quantity(1, "h", "s")
        assert result is not None
        assert result == 3600.0

        result = convert_quantity(1, "min", "s")
        assert result is not None
        assert result == 60.0

    def test_pressure_conversion(self):
        """Convert between pressure units."""
        result = convert_quantity(1, "bar", "Pa")
        assert result is not None
        assert result == 100000.0


class TestToSIBase:
    """Tests for SI base unit conversion."""

    def setup_method(self):
        reset_unit_registry()

    def test_power_to_si(self):
        """Convert power to SI base (kg*m²/s³)."""
        value, unit = to_si_base(5, "kW")
        assert value == 5000.0
        assert unit is not None

    def test_pressure_to_si(self):
        """Convert pressure to SI base (kg/(m*s²))."""
        value, unit = to_si_base(1, "bar")
        assert value == 100000.0
        assert unit is not None

    def test_length_to_si(self):
        """Convert length to SI base (m)."""
        value, unit = to_si_base(1000, "mm")
        assert value == 1.0
        assert "m" in str(unit).lower() or "meter" in str(unit).lower()


class TestCustomUnits:
    """Tests for custom unit definitions."""

    def setup_method(self):
        reset_unit_registry()

    def test_define_alias(self):
        """Define an alias for an existing unit."""
        # dag === day is pre-defined, but test the mechanism
        result = define_custom_unit("mydag === day")
        assert result is True
        assert is_unit_token("mydag") is True

    def test_define_derived(self):
        """Define a derived unit."""
        result = define_custom_unit("mybar === 100000 * Pa")
        assert result is True


class TestGetAllUnitNames:
    """Tests for getting all unit names."""

    def setup_method(self):
        reset_unit_registry()

    def test_contains_base_units(self):
        """Should contain base SI units."""
        names = get_all_unit_names()
        assert "m" in names
        assert "s" in names
        assert "kg" in names

    def test_contains_prefixed_units(self):
        """Should contain prefixed units."""
        names = get_all_unit_names()
        assert "kW" in names
        assert "mm" in names
        assert "kPa" in names

    def test_contains_custom_units(self):
        """Should contain custom-defined units."""
        names = get_all_unit_names()
        assert "EUR" in names


class TestCleanLatexUnit:
    """Tests for ISSUE-005: LaTeX-wrapped units with exponents."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_unit_registry()

    def test_text_wrapper_with_exponent(self):
        """\\text{m/s}^2 should become m/s**2."""
        result = clean_latex_unit("\\text{m/s}^2")
        assert result == "m/s**2"

    def test_mathrm_wrapper(self):
        """\\mathrm{kg} should become kg."""
        result = clean_latex_unit("\\mathrm{kg}")
        assert result == "kg"

    def test_bare_exponent(self):
        """m^3 should become m**3."""
        result = clean_latex_unit("m^3")
        assert result == "m**3"

    def test_braced_exponent(self):
        """m^{-2} should become m**-2."""
        result = clean_latex_unit("m^{-2}")
        assert result == "m**-2"

    def test_cdot_multiplication(self):
        """kg \\cdot m/s^2 should become kg * m/s**2."""
        result = clean_latex_unit("kg \\cdot m/s^2")
        assert result == "kg * m/s**2"

    def test_multiple_text_wrappers(self):
        """\\text{kW} \\cdot \\text{h} should become kW * h."""
        result = clean_latex_unit("\\text{kW} \\cdot \\text{h}")
        assert result == "kW * h"

    def test_frac_notation(self):
        """\\frac{m}{s^2} should become m/s**2."""
        result = clean_latex_unit("\\frac{m}{s^2}")
        assert result == "m/s**2"

    def test_none_input(self):
        """None input should return empty string."""
        result = clean_latex_unit(None)
        assert result == ""

    def test_empty_input(self):
        """Empty string should return empty string."""
        result = clean_latex_unit("")
        assert result == ""

    def test_plain_unit_unchanged(self):
        """Plain unit without LaTeX should remain unchanged."""
        result = clean_latex_unit("kg")
        assert result == "kg"

    def test_unicode_middle_dot(self):
        """Unicode middle dot (·) should become *."""
        result = clean_latex_unit("kg·m/s^2")
        assert result == "kg * m/s**2"
