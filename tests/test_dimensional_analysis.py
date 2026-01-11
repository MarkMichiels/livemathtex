"""Tests for ISSUE-006: Dimensional compatibility checking."""
import pytest
from livemathtex.core import process_text


class TestIncompatibleUnits:
    """Test that incompatible unit operations produce errors."""

    def test_kg_plus_m_raises_error(self):
        """Adding kg + m should produce an error."""
        result, ir = process_text("$m_1 := 5\\ kg$\n$d_1 := 3\\ m$\n$bad := m_1 + d_1 ==$")
        assert "Error" in result
        # Should mention incompatible units
        assert "kg" in result.lower() or "incompatible" in result.lower()

    def test_seconds_minus_velocity_raises_error(self):
        """Subtracting s - m/s should produce an error."""
        result, ir = process_text("$t_1 := 10\\ s$\n$v_1 := 5\\ \\frac{m}{s}$\n$bad := t_1 - v_1 ==$")
        assert "Error" in result

    def test_three_incompatible_terms(self):
        """Multiple incompatible terms should error."""
        result, ir = process_text("$a_1 := 1\\ kg$\n$b_1 := 2\\ m$\n$c_1 := 3\\ s$\n$bad := a_1 + b_1 + c_1 ==$")
        assert "Error" in result


class TestCompatibleUnits:
    """Test that compatible unit operations work correctly."""

    def test_kg_plus_kg_works(self):
        """Adding kg + kg should work."""
        result, ir = process_text("$m_1 := 5\\ kg$\n$m_2 := 3\\ kg$\n$total := m_1 + m_2 ==$")
        assert "Error" not in result
        assert "8" in result

    def test_km_plus_m_works(self):
        """Adding km + m (same dimension, different scale) should work."""
        result, ir = process_text("$d_1 := 1\\ km$\n$d_2 := 500\\ m$\n$total := d_1 + d_2 ==$")
        assert "Error" not in result
        # Result should be 1500 m or 1.5 km

    def test_unitless_addition_works(self):
        """Adding unitless numbers should work."""
        result, ir = process_text("$a_1 := 5$\n$b_1 := 3$\n$c_1 := a_1 + b_1 ==$")
        assert "Error" not in result
        assert "8" in result


class TestEdgeCases:
    """Test edge cases for dimensional analysis."""

    def test_multiplication_different_units_ok(self):
        """Multiplying different units should work (kg * m = kg*m)."""
        result, ir = process_text("$m_1 := 5\\ kg$\n$d_1 := 3\\ m$\n$prod := m_1 \\cdot d_1 ==$")
        assert "Error" not in result

    def test_division_different_units_ok(self):
        """Dividing different units should work (m / s = m/s)."""
        result, ir = process_text("$d_1 := 10\\ m$\n$t_1 := 2\\ s$\n$v_1 := d_1 / t_1 ==$")
        assert "Error" not in result
