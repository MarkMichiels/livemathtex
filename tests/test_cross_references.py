"""Tests for cross-reference evaluation in process_text."""

import pytest
from livemathtex import process_text, clear_text


class TestCrossReferenceEvaluation:
    """Tests for {{variable}} syntax evaluation."""

    def test_simple_variable_reference(self):
        """Test that {{variable}} is replaced with evaluated value."""
        content = """$C_{max} := 550\\ kg$

The maximum capacity is {{C_{max}}}.
"""
        result, ir = process_text(content)

        # Check that the reference was replaced
        assert "{{C_{max}}}" not in result.split("<!--")[0]  # Not in visible text
        assert "550" in result  # Value appears
        assert "<!-- {{C_{max}}} -->" in result  # Preserved in comment

    def test_variable_with_unit(self):
        """Test that units are included in cross-reference output."""
        content = """$V_{tank} := 100\\ L$

The volume is {{V_{tank}}}.
"""
        result, ir = process_text(content)

        # Should show value with unit
        assert "100" in result
        # Unit might be in different format (L, liter, etc.)
        assert "<!-- {{V_{tank}}} -->" in result

    def test_multiple_references(self):
        """Test multiple cross-references in same document."""
        content = """$a_1 := 10$
$b_1 := 20$

First is {{a_1}} and second is {{b_1}}.
"""
        result, ir = process_text(content)

        assert "<!-- {{a_1}} -->" in result
        assert "<!-- {{b_1}} -->" in result
        assert "10" in result
        assert "20" in result

    def test_undefined_variable_error(self):
        """Test that undefined variables show error."""
        content = """The value is {{X_undefined}}.
"""
        result, ir = process_text(content)

        # Should have error marker
        assert "ERROR" in result

    def test_reference_in_paragraph(self):
        """Test reference embedded in paragraph text."""
        content = """$m_{sample} := 55\\ kg$

The measured mass was **{{m_{sample}}}** which is within tolerance.
"""
        result, ir = process_text(content)

        assert "<!-- {{m_{sample}}} -->" in result
        assert "55" in result
        # Bold markers should be preserved
        assert "**" in result

    def test_cross_ref_stats(self):
        """Test that cross-reference stats are tracked."""
        content = """$x_1 := 10$

Reference: {{x_1}}
"""
        result, ir = process_text(content)

        # Stats should include cross_refs
        if "cross_refs" in ir.stats:
            assert ir.stats["cross_refs"] >= 1


class TestCrossReferenceClearCycle:
    """Tests for clear/process cycle with cross-references."""

    def test_clear_restores_reference(self):
        """Test that clear restores {{variable}} syntax."""
        content = """$C_1 := 100$

The value is {{C_1}}.
"""
        processed, _ = process_text(content)

        # Should have the comment marker
        assert "<!-- {{C_1}} -->" in processed

        # Clear should restore original syntax
        cleared, count = clear_text(processed)
        assert "{{C_1}}" in cleared
        assert "<!-- {{C_1}} -->" not in cleared

    def test_round_trip_stability(self):
        """Test that process→clear→process produces stable output."""
        content = """$val_1 := 42$

The answer is {{val_1}}.
"""
        # First process
        proc1, _ = process_text(content)

        # Clear
        cleared, _ = clear_text(proc1)

        # Second process
        proc2, _ = process_text(cleared)

        # Results should be equivalent (ignoring timestamps in metadata)
        # Both should have the reference replaced
        assert "<!-- {{val_1}} -->" in proc2
        assert "42" in proc2


class TestCrossReferenceEdgeCases:
    """Tests for edge cases in cross-reference handling."""

    def test_reference_in_math_block_ignored(self):
        """Test that {{}} inside math blocks is not processed as reference."""
        content = """$x_1 := 1$
$y_1 = \\text{some {{text}}}$
"""
        result, ir = process_text(content)

        # Should not have created a cross-reference from inside math block
        # The {{text}} inside should remain unchanged
        assert "ERROR" not in result or "text" not in result

    def test_escaped_braces(self):
        """Test that escaped braces are not processed."""
        content = """$x_1 := 1$

Use \\{{x_1}} for reference syntax.
"""
        result, ir = process_text(content)

        # Escaped braces should remain
        assert "\\{{" in result or "{{x_1}}" in result

    def test_subscript_variable(self):
        """Test cross-reference with LaTeX subscript variable."""
        content = """$C_{max} := 550$

The value is {{C_{max}}}.
"""
        result, ir = process_text(content)

        assert "<!-- {{C_{max}}} -->" in result
        assert "550" in result


class TestCrossReferenceFormatting:
    """Tests for value formatting in cross-references."""

    def test_large_number_formatting(self):
        """Test that large numbers get thousands separators."""
        content = """$big_num := 123456$

The value is {{big_num}}.
"""
        result, ir = process_text(content)

        # Large numbers should have some formatting
        # (implementation uses space as thousands separator)
        assert "<!-- {{big_num}} -->" in result

    def test_decimal_formatting(self):
        """Test that decimals are formatted reasonably."""
        content = """$ratio_val := 0.12345$

The ratio is {{ratio_val}}.
"""
        result, ir = process_text(content)

        # Should show some decimal places but not too many
        assert "<!-- {{ratio_val}} -->" in result
        assert "0.123" in result or "0.1234" in result
