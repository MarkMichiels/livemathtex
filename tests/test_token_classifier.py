"""
Tests for token_classifier module.

Tests TokenClassifier, TokenType, ImplicitMultInfo, and the
detect_implicit_multiplication() functionality.

Addresses ISS-018 and ISS-022.
"""

import pytest
from sympy import Symbol, symbols

from livemathtex.engine.token_classifier import (
    TokenClassifier,
    TokenType,
    ImplicitMultInfo,
    SINGLE_LETTER_UNITS,
    KNOWN_FUNCTIONS,
)
from livemathtex.engine.symbols import SymbolTable


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def symbol_table():
    """Create a symbol table with some pre-defined symbols."""
    table = SymbolTable()
    table.set("PPE_def", 100, latex_name="PPE_{def}")
    table.set("x", 5, latex_name="x")
    table.set("y", 10, latex_name="y")
    return table


@pytest.fixture
def classifier(symbol_table):
    """Create a TokenClassifier with the symbol table."""
    return TokenClassifier(symbol_table)


@pytest.fixture
def empty_classifier():
    """Create a TokenClassifier with empty symbol table."""
    return TokenClassifier(SymbolTable())


# =============================================================================
# TokenClassifier.classify() tests
# =============================================================================

class TestClassify:
    """Tests for TokenClassifier.classify() method."""

    def test_classify_known_unit_kg(self, classifier):
        """kg should be classified as UNIT."""
        assert classifier.classify("kg") == TokenType.UNIT

    def test_classify_known_unit_MWh(self, classifier):
        """MWh should be classified as UNIT."""
        assert classifier.classify("MWh") == TokenType.UNIT

    def test_classify_known_unit_mol(self, classifier):
        """mol should be classified as UNIT."""
        assert classifier.classify("mol") == TokenType.UNIT

    def test_classify_known_variable(self, classifier):
        """Defined variables should be classified as VARIABLE."""
        # Note: classifier uses symbol table which has latex names
        # The lookup is by latex_name, so check against what's defined
        assert classifier.classify("x") == TokenType.VARIABLE

    def test_classify_known_function_sin(self, classifier):
        """sin should be classified as FUNCTION."""
        assert classifier.classify("sin") == TokenType.FUNCTION

    def test_classify_known_function_cos(self, classifier):
        """cos should be classified as FUNCTION."""
        assert classifier.classify("cos") == TokenType.FUNCTION

    def test_classify_known_function_log(self, classifier):
        """log should be classified as FUNCTION."""
        assert classifier.classify("log") == TokenType.FUNCTION

    def test_classify_unknown_single_letter(self, empty_classifier):
        """Single letter not defined should be UNKNOWN."""
        assert empty_classifier.classify("z") == TokenType.UNKNOWN

    def test_classify_empty_string(self, classifier):
        """Empty string should be UNKNOWN."""
        assert classifier.classify("") == TokenType.UNKNOWN

    def test_classify_none(self, classifier):
        """None should be UNKNOWN."""
        assert classifier.classify(None) == TokenType.UNKNOWN


# =============================================================================
# TokenClassifier.is_multi_letter_identifier() tests
# =============================================================================

class TestIsMultiLetterIdentifier:
    """Tests for TokenClassifier.is_multi_letter_identifier() method."""

    def test_ppe_is_multi_letter(self, empty_classifier):
        """PPE should be identified as multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("PPE") is True

    def test_par_is_multi_letter(self, empty_classifier):
        """PAR should be identified as multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("PAR") is True

    def test_abc_is_multi_letter(self, empty_classifier):
        """ABC should be identified as multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("ABC") is True

    def test_single_letter_x_not_multi(self, empty_classifier):
        """Single letter 'x' is not multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("x") is False

    def test_single_letter_A_not_multi(self, empty_classifier):
        """Single letter 'A' is not multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("A") is False

    def test_unit_kg_not_multi(self, empty_classifier):
        """Known unit 'kg' is not multi-letter identifier."""
        assert empty_classifier.is_multi_letter_identifier("kg") is False

    def test_function_sin_not_multi(self, empty_classifier):
        """Known function 'sin' is not multi-letter identifier."""
        assert empty_classifier.is_multi_letter_identifier("sin") is False

    def test_empty_string_not_multi(self, empty_classifier):
        """Empty string is not multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("") is False

    def test_numbers_only_not_multi(self, empty_classifier):
        """Numbers only is not multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("123") is False

    def test_mixed_alphanumeric_ok(self, empty_classifier):
        """Mixed alphanumeric like PPE1 should be multi-letter."""
        assert empty_classifier.is_multi_letter_identifier("PPE1") is True


# =============================================================================
# TokenClassifier.has_unit_conflict() tests
# =============================================================================

class TestHasUnitConflict:
    """Tests for TokenClassifier.has_unit_conflict() method."""

    def test_A_conflicts_with_ampere(self, classifier):
        """'A' should conflict with ampere."""
        assert classifier.has_unit_conflict("A") == "ampere"

    def test_V_conflicts_with_volt(self, classifier):
        """'V' should conflict with volt."""
        assert classifier.has_unit_conflict("V") == "volt"

    def test_W_conflicts_with_watt(self, classifier):
        """'W' should conflict with watt."""
        assert classifier.has_unit_conflict("W") == "watt"

    def test_m_conflicts_with_meter(self, classifier):
        """'m' should conflict with meter."""
        assert classifier.has_unit_conflict("m") == "meter"

    def test_s_conflicts_with_second(self, classifier):
        """'s' should conflict with second."""
        assert classifier.has_unit_conflict("s") == "second"

    def test_x_no_conflict(self, classifier):
        """'x' should have no unit conflict."""
        assert classifier.has_unit_conflict("x") is None

    def test_z_no_conflict(self, classifier):
        """'z' should have no unit conflict."""
        assert classifier.has_unit_conflict("z") is None


# =============================================================================
# TokenClassifier.detect_implicit_multiplication() tests
# =============================================================================

class TestDetectImplicitMultiplication:
    """Tests for TokenClassifier.detect_implicit_multiplication() method."""

    def test_detect_ppe_as_implicit_mult(self, empty_classifier):
        """PPE should be detected as P*P*E implicit multiplication."""
        P, E = symbols("P E")
        result = empty_classifier.detect_implicit_multiplication("x := PPE", {P, E})

        assert result is not None
        assert result.intended_symbol == "PPE"
        assert result.split_as == "P*P*E"
        assert "P" in result.undefined_letters or "E" in result.undefined_letters

    def test_detect_par_with_ampere_conflict(self, empty_classifier):
        """PAR should be detected with 'A' flagged as unit conflict."""
        P, A, R = symbols("P A R")
        result = empty_classifier.detect_implicit_multiplication("x := PAR", {P, A, R})

        assert result is not None
        assert result.intended_symbol == "PAR"
        assert result.split_as == "P*A*R"
        assert "A" in result.unit_conflicts

    def test_detect_abc_as_implicit_mult(self, empty_classifier):
        """ABC should be detected as A*B*C."""
        A, B, C = symbols("A B C")
        result = empty_classifier.detect_implicit_multiplication("y := ABC", {A, B, C})

        assert result is not None
        assert result.intended_symbol == "ABC"
        assert result.split_as == "A*B*C"

    def test_no_detection_for_single_letters(self, empty_classifier):
        """Single letter expressions should not trigger detection."""
        a = Symbol("a")
        result = empty_classifier.detect_implicit_multiplication("x := a", {a})

        assert result is None

    def test_no_detection_for_defined_symbol(self, classifier):
        """If symbol is defined, no detection needed."""
        # classifier has 'x' defined
        result = classifier.detect_implicit_multiplication("y := x", {Symbol("x")})

        assert result is None

    def test_no_detection_when_no_multi_letter_in_latex(self, empty_classifier):
        """If no multi-letter sequence in LaTeX, no detection."""
        a, b = symbols("a b")
        result = empty_classifier.detect_implicit_multiplication("x := a + b", {a, b})

        assert result is None

    def test_detection_with_complex_expression(self, empty_classifier):
        """Multi-letter detection works in more complex expressions."""
        P, A, R, x = symbols("P A R x")
        result = empty_classifier.detect_implicit_multiplication(
            "y := x + PAR * 2", {P, A, R, x}
        )

        assert result is not None
        assert result.intended_symbol == "PAR"


# =============================================================================
# End-to-end error message tests
# =============================================================================

class TestEndToEndErrorMessages:
    """Test that processing produces expected error messages."""

    def test_error_message_mentions_ppe(self):
        """Processing '$x := PPE$' should mention 'PPE' in error."""
        from livemathtex.core import process_text

        result, ir = process_text("$x := PPE$")

        assert "PPE" in result
        assert "implicit multiplication" in result

    def test_error_message_shows_split(self):
        """Error message should show the split pattern."""
        from livemathtex.core import process_text

        result, ir = process_text("$x := PPE$")

        # Should show something like "P*P*E"
        assert "P*P" in result  # PPE becomes P*P (E absorbed by euler's constant)

    def test_error_message_mentions_par(self):
        """Processing '$x := PAR$' should mention 'PAR' in error."""
        from livemathtex.core import process_text

        result, ir = process_text("$x := PAR$")

        assert "PAR" in result
        assert "implicit multiplication" in result

    def test_ampere_conflict_mentioned(self):
        """PAR error should mention ampere conflict for 'A'."""
        from livemathtex.core import process_text

        result, ir = process_text("$x := PAR$")

        assert "ampere" in result

    def test_defined_ppe_works(self):
        """If PPE is defined, using it should work correctly."""
        from livemathtex.core import process_text

        result, ir = process_text("$PPE := 100$\n$x := PPE$")

        # Should not have error
        assert "Error" not in result
        assert "implicit multiplication" not in result

    def test_subscript_syntax_works(self):
        """Using subscript syntax like PPE_{eff} should work."""
        from livemathtex.core import process_text

        result, ir = process_text("$PPE_{eff} := 100$\n$x := PPE_{eff}$")

        # Should not have error for the variable definition
        # (the evaluation might show Error if not using ==)
        assert "implicit multiplication" not in result

    def test_single_letter_undefined_still_correct(self):
        """Single undefined letter still shows normal error."""
        from livemathtex.core import process_text

        result, ir = process_text("$x := z$")

        assert "Error" in result
        assert "Undefined variable" in result
        # Should NOT mention implicit multiplication for single letter
        assert "implicit multiplication" not in result


# =============================================================================
# Regression tests - ensure existing behavior preserved
# =============================================================================

class TestRegressions:
    """Regression tests to ensure existing functionality is preserved."""

    def test_defined_variable_evaluation_works(self):
        """Defined variables should still evaluate correctly."""
        from livemathtex.core import process_text

        # Use x_1 instead of 'a' since 'a' conflicts with 'year' unit
        result, ir = process_text("$x_1 := 5$\n$b_1 := x_1 * 2 == ?$")

        assert "== 10" in result
        assert "Error" not in result

    def test_unit_definitions_still_work(self):
        """Unit definitions should still work."""
        from livemathtex.core import process_text

        result, ir = process_text("$m_1 := 10\\ kg$\n$m_1 == ?$")

        assert "kg" in result
        assert "Error" not in result

    def test_formula_with_defined_symbols_works(self):
        """Formulas with all defined symbols should work."""
        from livemathtex.core import process_text

        result, ir = process_text("$x := 3$\n$y := 4$\n$z := x + y == ?$")

        assert "== 7" in result
        assert "Error" not in result

    def test_known_units_not_flagged(self):
        """Known multi-letter units should not trigger implicit mult detection."""
        from livemathtex.core import process_text

        # MWh is a known unit
        result, ir = process_text("$E := 100\\ MWh$\n$E == ?$")

        assert "implicit multiplication" not in result
        assert "MWh" in result

    def test_process_stability(self):
        """Processing should be stable and idempotent."""
        from livemathtex.core import process_text
        import re

        input_text = "$x := 5$\n$y := x * 2 == ?$"
        result1, _ = process_text(input_text)
        result2, _ = process_text(input_text)

        # Remove timestamp from metadata for comparison (timestamps differ by seconds)
        def strip_timestamp(s):
            return re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', s)

        # Should produce same result (ignoring timestamp)
        assert strip_timestamp(result1) == strip_timestamp(result2)
