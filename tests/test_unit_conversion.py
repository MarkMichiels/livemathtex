"""Tests for recursive unit conversion (ISS-014).

Tests unit conversion for recursively defined units like MWh, mol/day, kWh
that previously failed because SymPy ratio approach couldn't simplify them.
"""

import pytest
from livemathtex import process_text


class TestRecursiveUnitConversion:
    """Test conversion to recursively defined units (MWh, mol/day, etc.)."""

    def test_mwh_conversion(self):
        """Test conversion from J to MWh.

        MWh = 1000*kWh = 1000000*Wh = 3600000000 J
        168000000000 J = 46.67 MWh (approximately)

        Should NOT produce kg*m^2/s^2 (SI base units).
        """
        content = '$E := 168000000000\\ J$\n$E == [MWh]$'
        result, _ = process_text(content)

        # Must contain MWh unit
        assert '\\text{MWh}' in result, f"Expected \\text{{MWh}} in result, got: {result}"
        # Must NOT fall back to SI base units
        assert 'kg' not in result, f"Should not contain 'kg' (SI base), got: {result}"
        assert 'm^2' not in result or 's^2' not in result, f"Should not contain SI base units, got: {result}"

    def test_mol_per_day_conversion(self):
        """Test conversion to mol/day compound unit.

        1 mol/s = 86400 mol/day
        0.001 mol/s = 86.4 mol/day
        """
        content = '$rate := 0.001\\ \\frac{mol}{s}$\n$rate == [mol/day]$'
        result, _ = process_text(content)

        # Must contain the target unit
        assert 'mol' in result, f"Expected mol in result, got: {result}"
        assert 'day' in result, f"Expected day in result, got: {result}"

    def test_compound_unit_mwh_per_kg(self):
        """Test conversion to MWh/kg compound unit.

        Combines prefixed unit (MWh) with simple unit (kg).
        """
        content = '$E := 3600000000\\ \\frac{J}{kg}$\n$E == [MWh/kg]$'
        result, _ = process_text(content)

        # Must contain MWh and kg
        assert 'MWh' in result, f"Expected MWh in result, got: {result}"
        assert 'kg' in result, f"Expected kg in result, got: {result}"
        # Should NOT have m^2/s^2 pattern
        assert 'm^2' not in result or 's^2' not in result, f"Should not contain SI base units, got: {result}"

    def test_prefixed_unit_kwh(self):
        """Test conversion from J to kWh.

        3600000 J = 1 kWh
        7200000 J = 2 kWh
        """
        content = '$E := 7200000\\ J$\n$E == [kWh]$'
        result, _ = process_text(content)

        # Must contain kWh
        assert '\\text{kWh}' in result or 'kWh' in result, f"Expected kWh in result, got: {result}"
        # Check for reasonable numeric value (approximately 2)
        assert '2' in result, f"Expected value around 2 kWh, got: {result}"
        # Must NOT fall back to SI base units
        assert 'm^2' not in result or 's^2' not in result, f"Should not contain SI base units, got: {result}"


class TestUnitConversionEdgeCases:
    """Test edge cases for unit conversion."""

    def test_gwh_conversion(self):
        """Test conversion to GWh (giga-watt-hour).

        1 GWh = 1000 MWh = 3.6e12 J
        """
        content = '$E := 3.6e12\\ J$\n$E == [GWh]$'
        result, _ = process_text(content)

        # Must contain GWh
        assert 'GWh' in result, f"Expected GWh in result, got: {result}"

    def test_mmol_per_hour_conversion(self):
        """Test conversion to mmol/h (millimol per hour).

        1 mol/s = 3600000 mmol/h
        """
        content = '$rate := 1e-6\\ \\frac{mol}{s}$\n$rate == [mmol/h]$'
        result, _ = process_text(content)

        # Must contain mmol and h
        assert 'mmol' in result, f"Expected mmol in result, got: {result}"
        assert 'h' in result, f"Expected h (hour) in result, got: {result}"
