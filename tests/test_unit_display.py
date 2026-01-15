"""Tests for unit display formatting options (ISS-042)."""

import pytest
from livemathtex import process_text
from livemathtex.config import LivemathConfig, UnitFormat
from livemathtex.engine.pint_backend import format_unit_latex


class TestUnitFormatConfig:
    """Test UnitFormat enum and config handling."""

    def test_unit_format_enum_values(self):
        """Verify enum has expected values."""
        assert UnitFormat.DEFAULT.value == "default"
        assert UnitFormat.FRACTION.value == "fraction"
        assert UnitFormat.EXPONENT.value == "exponent"

    def test_config_default_unit_format(self):
        """Default config should use DEFAULT format."""
        config = LivemathConfig()
        assert config.unit_format == UnitFormat.DEFAULT

    def test_config_with_unit_format_override(self):
        """Config should accept unit_format override."""
        config = LivemathConfig().with_overrides({"unit_format": "fraction"})
        assert config.unit_format == UnitFormat.FRACTION

        config2 = LivemathConfig().with_overrides({"unit_format": "exponent"})
        assert config2.unit_format == UnitFormat.EXPONENT

    def test_config_invalid_unit_format_ignored(self):
        """Invalid unit_format values should be ignored."""
        config = LivemathConfig().with_overrides({"unit_format": "invalid"})
        assert config.unit_format == UnitFormat.DEFAULT


class TestFormatUnitLatexDefault:
    """Test default unit formatting (backward compatibility)."""

    def test_simple_unit(self):
        """Simple units should be abbreviated."""
        assert format_unit_latex("kilogram") == "kg"
        assert format_unit_latex("meter") == "m"
        assert format_unit_latex("second") == "s"

    def test_compound_unit_default(self):
        """Default format should use Pint-style output."""
        result = format_unit_latex("kilogram / meter / second")
        assert "kg" in result
        assert "m" in result
        assert "s" in result

    def test_original_latex_preserved(self):
        """Original LaTeX should be preserved if provided."""
        result = format_unit_latex("kilogram", original_latex="kg")
        assert result == "kg"


class TestFormatUnitLatexFraction:
    """Test fraction format (parenthesized denominator)."""

    def test_simple_division(self):
        """Simple division should not add parentheses."""
        result = format_unit_latex("mg / L", unit_format="fraction")
        assert result == "mg/L"

    def test_multiple_denominators(self):
        """Multiple denominators should be parenthesized."""
        result = format_unit_latex("mg / d / L", unit_format="fraction")
        # Should produce mg/(d · L) or similar
        assert "mg" in result
        assert "(" in result
        assert ")" in result

    def test_no_division(self):
        """Units without division should just use middle dot."""
        result = format_unit_latex("kg * m", unit_format="fraction")
        assert "kg" in result
        assert "m" in result
        assert "/" not in result


class TestFormatUnitLatexExponent:
    """Test exponent format (negative superscripts)."""

    def test_simple_division(self):
        """Simple division should become negative exponent."""
        result = format_unit_latex("m / s", unit_format="exponent")
        assert "m" in result
        assert "s" in result
        assert "⁻¹" in result

    def test_multiple_denominators(self):
        """Multiple denominators should each get negative exponents."""
        result = format_unit_latex("mg / d / L", unit_format="exponent")
        assert "mg" in result
        assert "⁻¹" in result
        # Should have two ⁻¹ (one for d, one for L)
        assert result.count("⁻¹") == 2

    def test_exponent_in_denominator(self):
        """Exponents in denominator should become negative."""
        result = format_unit_latex("kg / m^2", unit_format="exponent")
        assert "kg" in result
        assert "m" in result
        assert "⁻²" in result

    def test_no_division(self):
        """Units without division should just use middle dot."""
        result = format_unit_latex("kg * m", unit_format="exponent")
        assert "kg" in result
        assert "m" in result
        assert "/" not in result


class TestUnitFormatIntegration:
    """Test unit formatting through full processing pipeline."""

    def test_default_format_in_output(self):
        """Default format should work in full pipeline."""
        content = """
$v_1 := 10\\ \\frac{m}{s}$
$v_1 ==$
"""
        result, _ = process_text(content)
        assert "10" in result
        assert "m" in result
        assert "s" in result

    def test_compound_unit_output(self):
        """Compound units should display correctly."""
        content = """
$rate_1 := 5\\ \\frac{mg}{L}$
$time_1 := 2\\ d$
$total_1 := rate_1 \\cdot time_1 ==$
"""
        result, _ = process_text(content)
        assert "10" in result
        assert "mg" in result
        # Default format will have some combination of d, L, mg
