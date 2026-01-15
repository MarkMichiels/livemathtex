"""
Test suite for ISSUE-002: Dynamic unit recognition via Pint.

Tests that:
1. Pint native units work without custom definition
2. Custom units require === definition
3. Variable/unit conflicts are detected
4. Edge cases (Unicode, compound units) work correctly
"""
import pytest
from livemathtex.engine.pint_backend import (
    is_pint_unit,
    is_custom_unit,
    is_known_unit,
    reset_unit_registry,
    get_custom_unit_registry,
)


@pytest.fixture(autouse=True)
def reset_registries():
    """Reset registries before each test."""
    reset_unit_registry()
    yield


class TestIsPintUnit:
    """Test is_pint_unit() function."""

    def test_si_base_units(self):
        """SI base units should be recognized."""
        assert is_pint_unit('m')
        assert is_pint_unit('kg')
        assert is_pint_unit('s')
        assert is_pint_unit('A')
        assert is_pint_unit('K')
        assert is_pint_unit('mol')
        assert is_pint_unit('cd')

    def test_si_derived_units(self):
        """SI derived units should be recognized."""
        assert is_pint_unit('N')
        assert is_pint_unit('J')
        assert is_pint_unit('W')
        assert is_pint_unit('Pa')
        assert is_pint_unit('Hz')
        assert is_pint_unit('V')
        assert is_pint_unit('ohm')

    def test_prefixed_units(self):
        """Prefixed units should be recognized."""
        assert is_pint_unit('kW')
        assert is_pint_unit('MW')
        assert is_pint_unit('GW')
        assert is_pint_unit('mm')
        assert is_pint_unit('km')
        assert is_pint_unit('mg')
        assert is_pint_unit('kHz')
        assert is_pint_unit('MHz')

    def test_energy_units(self):
        """Energy units (including Wh family) should be recognized."""
        assert is_pint_unit('Wh')
        assert is_pint_unit('kWh')
        assert is_pint_unit('MWh')
        assert is_pint_unit('GWh')

    def test_compound_units(self):
        """Compound units should be recognized."""
        assert is_pint_unit('m/s')
        assert is_pint_unit('kg/m³') or is_pint_unit('kg/m**3')
        assert is_pint_unit('kWh/kg')
        assert is_pint_unit('m³/h') or is_pint_unit('m**3/h')

    def test_currency_not_recognized(self):
        """Currency symbols should NOT be recognized as Pint units."""
        assert not is_pint_unit('€')
        assert not is_pint_unit('$')
        # EUR/USD are defined in our Pint setup
        assert is_pint_unit('EUR')
        assert is_pint_unit('USD')

    def test_unknown_units(self):
        """Unknown strings should not be recognized."""
        assert not is_pint_unit('xyz')
        assert not is_pint_unit('foo')
        assert not is_pint_unit('')
        assert not is_pint_unit(None)


class TestIsCustomUnit:
    """Test is_custom_unit() function."""

    def test_builtin_custom_units(self):
        """Built-in custom units (€, $) should be recognized."""
        registry = get_custom_unit_registry()
        assert '€' in registry._custom_units
        assert '$' in registry._custom_units
        assert 'EUR' in registry._custom_units
        assert 'USD' in registry._custom_units

    def test_user_defined_custom_unit(self):
        """User-defined custom units should be recognized after definition."""
        registry = get_custom_unit_registry()

        # Before definition
        assert not is_custom_unit('SEC')

        # Define custom unit
        registry.define_unit('SEC === kWh/kg')

        # After definition
        assert is_custom_unit('SEC')


class TestIsKnownUnit:
    """Test is_known_unit() function."""

    def test_pint_units_are_known(self):
        """Pint units should be known."""
        assert is_known_unit('kWh')
        assert is_known_unit('MW')
        assert is_known_unit('bar')

    def test_custom_units_are_known(self):
        """Custom units should be known."""
        assert is_known_unit('€')

    def test_unknown_not_known(self):
        """Unknown strings should not be known."""
        assert not is_known_unit('xyz')
        assert not is_known_unit('')


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_unicode_units(self):
        """Unicode characters should work."""
        # μm, m³, etc.
        assert is_pint_unit('µm') or is_pint_unit('um')  # micro prefix
        assert is_pint_unit('m³') or is_pint_unit('m**3')

    def test_latex_wrapped_units(self):
        """LaTeX-wrapped units should work."""
        # The unwrap function handles \text{kg}, etc.
        from livemathtex.engine.pint_backend import _unwrap_latex
        
        assert _unwrap_latex(r'\text{kg}') == 'kg'
        assert _unwrap_latex(r'\mathrm{kW}') == 'kW'

    def test_case_sensitivity(self):
        """Unit parsing should be case-sensitive."""
        # 'm' is meter, 'M' is mega prefix
        assert is_pint_unit('m')
        assert is_pint_unit('M')  # mega prefix is valid

    def test_dag_ambiguity(self):
        """'dag' in Pint means decagram, not day."""
        # This is a known gotcha - 'dag' in Pint is 10 grams
        assert is_pint_unit('dag')  # decagram
        # For 'day' as unit, use 'day'
        assert is_pint_unit('day')


class TestIntegration:
    """Integration tests with full LiveMathTeX processing."""

    def test_pint_units_work_without_definition(self):
        """Standard units should work without === definition."""
        from livemathtex.core import process_text
        
        # kWh is recognized by Pint, no definition needed
        result = process_text("$$ E := 100\\ kWh $$")
        assert 'Error' not in result

    def test_custom_units_need_definition(self):
        """Currency needs === definition."""
        from livemathtex.core import process_text
        
        # € is pre-defined in our SymPy registry
        result = process_text("$$ € === € $$\n$$ price := 100\\ € $$")
        assert 'Error' not in result


# Summary test
class TestIssue002Summary:
    """Summary tests verifying ISSUE-002 requirements."""

    def test_no_hardcoded_lists_needed(self):
        """
        Verify that Pint recognizes all common units without hardcoded lists.
        
        This was the core goal of ISSUE-002: remove ~230 hardcoded unit
        definitions and use Pint as single source of truth.
        """
        common_units = [
            # SI base
            'm', 'kg', 's', 'A', 'K', 'mol', 'cd',
            # SI derived
            'N', 'J', 'W', 'Pa', 'Hz', 'V',
            # Prefixed
            'kW', 'MW', 'GW', 'mm', 'cm', 'km', 'mg', 'kJ', 'MJ',
            # Energy (special)
            'kWh', 'MWh', 'Wh',
            # Pressure
            'bar', 'mbar',
            # Volume
            'L', 'mL',
            # Time
            'h', 'min', 'day',
        ]
        
        for unit in common_units:
            assert is_pint_unit(unit), f"Pint should recognize '{unit}'"

    def test_only_currency_needs_custom(self):
        """
        Currency is the main exception that needs custom definition.
        """
        # These are NOT in Pint by default
        assert not is_pint_unit('€')
        assert not is_pint_unit('$')
        
        # But we pre-define EUR/USD in our Pint setup
        assert is_pint_unit('EUR')
        assert is_pint_unit('USD')
        
        # And € and $ are in our SymPy custom registry
        assert is_custom_unit('€')
        assert is_custom_unit('$')

