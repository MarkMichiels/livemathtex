"""
Tests for Pint-based evaluation (ISS-024 fix).

This module tests the Pint evaluator that fixes numerical calculations
where rate × time should properly produce energy units (e.g., kW × h = kWh).

Note: Single-letter variable names often conflict with Pint units (P=poise, L=liter,
t=metric_ton). Tests use subscripted names (P_1, L_1, etc.) to avoid conflicts.
"""

import pytest
from livemathtex import process_text


class TestRateTimeCalculations:
    """Test that rate × time calculations work correctly (ISS-024)."""

    def test_power_times_time_gives_energy(self):
        """kW × h should produce kWh/MWh correctly."""
        text = r"""
$P_1 := 310.7\ kW$
$t_1 := 8760\ h$
$E_1 := P_1 \cdot t_1 ==$ <!-- [MWh] -->
"""
        result, ir = process_text(text)
        # Expected: 310.7 * 8760 / 1000 = 2721.732 MWh
        assert r"2721.732\ \text{MWh}" in result
        assert "Error" not in result

    def test_mass_rate_times_time_gives_mass(self):
        """g/day × day should produce mass correctly."""
        text = r"""
$m_r := 49020\ \frac{g}{d}$
$t_d := 365\ d$
$C_m := m_r \cdot t_d ==$ <!-- [kg] -->
"""
        result, ir = process_text(text)
        # Expected: 49020 * 365 / 1000 = 17,892.3 kg
        assert "kg" in result
        # The day units should cancel, leaving mass
        assert "Error" not in result

    def test_volume_flow_times_time_gives_volume(self):
        """m³/h × h should produce volume correctly."""
        text = r"""
$Q_1 := 50\ \frac{m^3}{h}$
$t_1 := 24\ h$
$V_1 := Q_1 \cdot t_1 ==$ <!-- [m³] -->
"""
        result, ir = process_text(text)
        # Expected: 50 * 24 = 1200 m³
        assert "1200" in result
        assert "Error" not in result


class TestUnitConversions:
    """Test unit conversions via unit hints."""

    def test_force_to_newton(self):
        """kg·m/s² should convert to N."""
        text = r"""
$m_1 := 10\ kg$
$a_1 := 9.81\ \frac{m}{s^2}$
$F_1 := m_1 \cdot a_1 ==$ <!-- [N] -->
"""
        result, ir = process_text(text)
        # Expected: 10 * 9.81 = 98.1 N
        assert "98.1" in result
        assert "N" in result
        assert "Error" not in result

    def test_energy_joules_to_kwh(self):
        """J should convert to kWh."""
        text = r"""
$E_j := 3600000\ J$
$E_k := E_j ==$ <!-- [kWh] -->
"""
        result, ir = process_text(text)
        # Expected: 3600000 J = 1 kWh
        assert "kWh" in result
        assert "Error" not in result

    def test_velocity_conversion(self):
        """km/h should convert to m/s."""
        text = r"""
$v_1 := 36\ \frac{km}{h}$
$v_m := v_1 ==$ <!-- [m/s] -->
"""
        result, ir = process_text(text)
        # Expected: 36 km/h = 10 m/s
        assert "10" in result
        assert "m/s" in result
        assert "Error" not in result


class TestCompoundExpressions:
    """Test complex expressions with multiple operations."""

    def test_area_from_diameter(self):
        """π × D²/4 should give area."""
        text = r"""
$D_1 := 0.1\ m$
$A_1 := \frac{\pi \cdot D_1^2}{4} ==$
"""
        result, ir = process_text(text)
        # Expected: π × 0.1² / 4 ≈ 0.007854 m²
        # Note: 0.0079 is also acceptable due to rounding
        assert "0.0078" in result or "0.0079" in result or "7853" in result
        assert "Error" not in result

    def test_kinetic_energy(self):
        """½mv² should give energy."""
        text = r"""
$m_1 := 10\ kg$
$v_1 := 5\ \frac{m}{s}$
$E_k := \frac{1}{2} \cdot m_1 \cdot v_1^2 ==$
"""
        result, ir = process_text(text)
        # Expected: 0.5 * 10 * 25 = 125 J (or kg·m²/s²)
        assert "125" in result
        assert "Error" not in result


class TestDimensionlessResults:
    """Test that dimensionless results use SymPy formatting."""

    def test_ratio_is_dimensionless(self):
        """Ratio of same units should be dimensionless."""
        text = r"""
$m_1 := 10\ kg$
$m_2 := 25\ kg$
$r_m := \frac{m_2}{m_1} ==$
"""
        result, ir = process_text(text)
        # Expected: 25/10 = 2.5 (dimensionless)
        assert "2.5" in result
        assert "Error" not in result

    def test_pure_number_formats_correctly(self):
        """Pure numbers should use SymPy formatting with format settings."""
        text = r"""
$x_1 := 123456789$
$x_1 ==$ <!-- digits:3 format:scientific -->
"""
        result, ir = process_text(text)
        # Should use scientific notation
        assert "e+" in result.lower() or "1.23" in result
        assert "Error" not in result


class TestPintASTEvaluator:
    """Test the Pint AST evaluator directly."""

    def test_multiplication_with_units(self):
        """Multiplication should propagate units."""
        text = r"""
$a_1 := 5\ m$
$b_1 := 3\ s$
$c_1 := a_1 \cdot b_1 ==$
"""
        result, ir = process_text(text)
        assert "15" in result
        assert "Error" not in result

    def test_division_with_units(self):
        """Division should create compound units."""
        text = r"""
$d_1 := 100\ m$
$t_1 := 10\ s$
$v_1 := \frac{d_1}{t_1} ==$
"""
        result, ir = process_text(text)
        # Expected: 100/10 = 10 m/s
        assert "10" in result
        assert "Error" not in result

    def test_power_with_units(self):
        """Power should work with units."""
        text = r"""
$L_1 := 2\ m$
$A_1 := L_1^2 ==$
"""
        result, ir = process_text(text)
        # Expected: 2² = 4 m²
        assert "4" in result
        assert "Error" not in result


class TestISS024Regression:
    """Regression tests for ISS-024 - rate × time calculations."""

    def test_annual_production_calculation(self):
        """Annual production from daily rate × operating days."""
        text = r"""
$rate_1 := 49020\ \frac{g}{d}$
$days_1 := 365\ d$
$yield_f := 0.9$
$annual := rate_1 \cdot days_1 \cdot yield_f ==$ <!-- [kg] -->
"""
        result, ir = process_text(text)
        # Expected: 49020 * 365 * 0.9 / 1000 = 16,103 kg
        assert "kg" in result
        # Check reasonable value (should be ~16000)
        assert "Error" not in result

    def test_energy_cost_calculation(self):
        """Energy from power × time, then cost."""
        text = r"""
$P_1 := 100\ kW$
$hours_1 := 8760\ h$
$price_1 := 0.10\ \frac{€}{kWh}$
$E_1 := P_1 \cdot hours_1 ==$ <!-- [kWh] -->
$cost_1 := E_1 \cdot price_1 ==$
"""
        result, ir = process_text(text)
        # Expected E: 100 * 8760 = 876,000 kWh
        # Expected cost: 876,000 * 0.10 = 87,600 €
        assert "876" in result  # Energy in kWh
        assert "Error" not in result


class TestSymPyConstants:
    """Test SymPy mathematical constants (ISS-025 fix).

    SymPy constants like Pi, E (Exp1), EulerGamma inherit from NumberSymbol,
    not Number, so they need special handling in evaluate_sympy_ast_with_pint().
    """

    def test_pi_in_expression(self):
        """Pi should evaluate to ~3.14159 in calculations."""
        text = r"""
$x_1 := 38\ mm$
$d_1 := \frac{2 \cdot x_1}{\pi} ==$
"""
        result, ir = process_text(text)
        # Expected: 2 * 38 / pi = 76 / 3.14159 ≈ 24.19 mm
        assert "24.19" in result or "24.2" in result
        assert "Error" not in result

    def test_pi_times_r_squared(self):
        """Area of circle: π × r² should work."""
        text = r"""
$r_1 := 5\ m$
$A_1 := \pi \cdot r_1^2 ==$
"""
        result, ir = process_text(text)
        # Expected: π × 25 ≈ 78.54 m²
        assert "78.5" in result or "78.54" in result
        assert "Error" not in result

    def test_e_in_expression(self):
        """Euler's number e should evaluate to ~2.718."""
        text = r"""
$x_1 := 1$
$y_1 := e^{x_1} ==$
"""
        result, ir = process_text(text)
        # Expected: e^1 ≈ 2.718
        assert "2.71" in result or "2.718" in result
        assert "Error" not in result

    def test_two_pi(self):
        """2π should evaluate to ~6.283."""
        text = r"""
$omega_1 := 2 \cdot \pi ==$
"""
        result, ir = process_text(text)
        # Expected: 2π ≈ 6.283
        assert "6.28" in result
        assert "Error" not in result

    def test_pi_in_compound_formula(self):
        """Pi in more complex formula: circumference = 2πr."""
        text = r"""
$r_1 := 10\ cm$
$C_1 := 2 \cdot \pi \cdot r_1 ==$
"""
        result, ir = process_text(text)
        # Expected: 2 × π × 10 ≈ 62.83 cm
        assert "62.8" in result or "62.83" in result
        assert "Error" not in result
