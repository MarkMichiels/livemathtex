"""
Test suite for ISSUE-003: Strict separation of value vs formula definitions.

Tests that:
1. Undefined symbols in formulas raise errors (not unit fallback)
2. Defined symbols in formulas work correctly
3. Value definitions with units work correctly
4. Unit-conflict errors are raised appropriately

This is the RED phase of TDD - these tests should FAIL until the fix is implemented.
"""
import pytest
from livemathtex.core import process_text
from livemathtex.engine.pint_backend import reset_unit_registry


@pytest.fixture(autouse=True)
def reset_registries():
    """Reset registries before each test."""
    reset_unit_registry()
    yield


class TestUndefinedSymbolInFormula:
    """Test that undefined symbols in formulas raise errors, NOT unit fallback."""

    def test_undefined_V_in_formula_raises_error(self):
        """
        Cap := V * 15 * 0.001 where V undefined should error.

        ISSUE-003: Currently silently interprets V as volt when expression has decimals.
        The decimal triggers is_definition_with_units=True, which allows unit fallback.
        Expected: Error about undefined variable V.
        """
        content = "$Cap := V \\cdot 15 \\cdot 0.001$"
        result, ir = process_text(content)

        # Should contain an error - undefined variable V
        # (V as unit should NOT be used as fallback in formulas)
        assert "\\color{red}" in result, (
            "Expected error for undefined V, but got no error. "
            f"Result: {result}"
        )
        assert "Undefined" in result or "undefined" in result.lower(), (
            f"Error should mention 'undefined'. Result: {result}"
        )

    def test_undefined_symbol_in_formula_no_unit_conflict(self):
        """
        y := x * 2 where x undefined should error.

        x is not a unit name, so this tests the general undefined symbol case.
        """
        content = "$y := x \\cdot 2$"
        result, ir = process_text(content)

        # Should contain an error about undefined x
        assert "\\color{red}" in result, (
            "Expected error for undefined x, but got no error. "
            f"Result: {result}"
        )

    def test_undefined_N_in_formula_raises_error(self):
        """
        force := N * 10.5 where N undefined should error.

        N is a unit (Newton), but in a formula with decimals it should NOT fall back
        to unit interpretation - it should be treated as undefined variable.
        """
        content = "$force := N \\cdot 10.5$"
        result, ir = process_text(content)

        # Should contain an error - undefined variable N
        assert "\\color{red}" in result, (
            "Expected error for undefined N, but got no error. "
            f"Result: {result}"
        )


class TestDefinedSymbolInFormula:
    """Test that defined symbols in formulas work correctly."""

    def test_defined_variable_in_formula_works(self):
        """
        Define V_tot, then use it in Cap formula - should work.
        """
        content = """
$V_{tot} := 100$
$Cap := V_{tot} \\cdot 15$
$Cap ==$
"""
        result, ir = process_text(content)

        # Should NOT contain errors
        assert "\\color{red}" not in result, (
            f"Unexpected error for defined variable. Result: {result}"
        )
        # Should contain the evaluation result (100 * 15 = 1500)
        # ISS-039: With thousands separator, it's 1\,500
        assert "1\\,500" in result or "1500" in result, (
            f"Expected 1500 or 1\\,500 in result. Result: {result}"
        )

    def test_subscripted_variable_avoids_unit_conflict(self):
        """
        V_tot avoids conflict with volt unit V.
        """
        content = """
$V_{tot} := 37824$
$Cap := V_{tot} \\cdot 0.015$
$Cap ==$
"""
        result, ir = process_text(content)

        # Should work without errors
        assert "\\color{red}" not in result, (
            f"Unexpected error. Result: {result}"
        )
        # 37824 * 0.015 = 567.36
        assert "567" in result, (
            f"Expected ~567 in result. Result: {result}"
        )


class TestValueDefinitionsWithUnits:
    """Test that value definitions with units still work correctly."""

    def test_value_definition_with_unit_suffix(self):
        """
        x := 5 V (volt as unit suffix) should work.
        """
        content = """
$x := 5\\ V$
$x ==$
"""
        result, ir = process_text(content)

        # Should work - V as unit suffix on number is valid
        assert "\\color{red}" not in result, (
            f"Unexpected error for value with unit. Result: {result}"
        )
        # Result should show 5 with volt unit
        assert "5" in result, f"Expected 5 in result. Result: {result}"

    def test_value_definition_with_compound_unit(self):
        """
        accel := 9.81 m/s^2 should work.

        Note: Use 'accel' instead of 'a' because 'a' is a unit (year) in Pint.
        """
        content = """
$accel := 9.81\\ \\frac{m}{s^2}$
$accel ==$
"""
        result, ir = process_text(content)

        # Should work
        assert "\\color{red}" not in result, (
            f"Unexpected error for compound unit. Result: {result}"
        )
        assert "9.81" in result or "9.8" in result, (
            f"Expected ~9.81 in result. Result: {result}"
        )


class TestUnitConflictErrors:
    """Test that unit-conflict errors are raised when defining variables with unit names."""

    def test_V_definition_raises_conflict_error(self):
        """
        V := 37824 should error because V conflicts with volt unit.
        """
        content = "$V := 37824$"
        result, ir = process_text(content)

        # Should contain an error about unit conflict
        assert "\\color{red}" in result, (
            f"Expected error for V/volt conflict. Result: {result}"
        )
        # Error should mention volt or unit conflict
        assert "volt" in result.lower() or "conflict" in result.lower() or "reserved" in result.lower(), (
            f"Error should mention volt/conflict/reserved. Result: {result}"
        )

    def test_subscripted_V_avoids_conflict(self):
        """
        V_tot := 37824 should work (subscript disambiguates from volt).
        """
        content = """
$V_{tot} := 37824$
$V_{tot} ==$
"""
        result, ir = process_text(content)

        # Should work without errors
        assert "\\color{red}" not in result, (
            f"Unexpected error for V_tot. Result: {result}"
        )
        assert "37824" in result, (
            f"Expected 37824 in result. Result: {result}"
        )

    def test_m_definition_raises_conflict_error(self):
        """
        m := 10 should error because m conflicts with meter unit.
        """
        content = "$m := 10$"
        result, ir = process_text(content)

        # Should contain an error about unit conflict
        assert "\\color{red}" in result, (
            f"Expected error for m/meter conflict. Result: {result}"
        )


class TestFormulaWithMultipleSymbols:
    """Test formulas with multiple symbols including potential unit conflicts."""

    def test_formula_with_undefined_and_defined_symbols(self):
        """
        Formula with mix of defined and undefined symbols should error.

        Note: Use subscripted variable names to avoid Pint unit conflicts.
        """
        content = """
$x_1 := 10$
$result := x_1 \\cdot y_1 \\cdot z_1$
"""
        result, ir = process_text(content)

        # Should error because y_1 and z_1 are undefined
        assert "\\color{red}" in result, (
            f"Expected error for undefined y_1 or z_1. Result: {result}"
        )

    def test_formula_all_symbols_defined(self):
        """
        Formula with all symbols defined should work.

        Note: Use subscripted variable names to avoid Pint unit conflicts.
        """
        content = """
$x_1 := 10$
$y_1 := 20$
$z_1 := 30$
$result := x_1 \\cdot y_1 \\cdot z_1$
$result ==$
"""
        result, ir = process_text(content)

        # Should work without errors
        assert "\\color{red}" not in result, (
            f"Unexpected error. Result: {result}"
        )
        # 10 * 20 * 30 = 6000
        # ISS-039: With thousands separator, it's 6\,000
        assert "6\\,000" in result or "6000" in result, (
            f"Expected 6000 or 6\\,000 in result. Result: {result}"
        )


class TestEvaluationOfUndefinedSymbol:
    """Test evaluation (==) of undefined symbols."""

    def test_evaluate_undefined_symbol_raises_error(self):
        """
        x == where x is undefined should error.
        """
        content = "$x ==$"
        result, ir = process_text(content)

        # Should error - x is undefined
        assert "\\color{red}" in result, (
            f"Expected error for undefined x evaluation. Result: {result}"
        )
