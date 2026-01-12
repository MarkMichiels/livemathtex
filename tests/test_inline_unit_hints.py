"""Tests for inline unit hint syntax ($E == [kJ]$)."""

import pytest
from livemathtex import process_text
from livemathtex.parser.lexer import Lexer
from livemathtex.parser.models import MathBlock


class TestInlineUnitHintParsing:
    """Test parser extraction of inline unit hints."""

    def test_basic_inline_unit_extraction(self):
        """Test that [unit] is extracted from evaluation."""
        lexer = Lexer()
        doc = lexer.parse('$E == [kJ]$')

        calcs = []
        for block in doc.children:
            if isinstance(block, MathBlock):
                calcs.extend(lexer.extract_calculations(block))

        assert len(calcs) == 1
        assert calcs[0].unit_comment == 'kJ'
        assert calcs[0].original_result == ''  # [unit] removed

    def test_inline_unit_with_existing_result(self):
        """Test [unit] extraction when result already present."""
        lexer = Lexer()
        doc = lexer.parse('$E == 1000 [kJ]$')

        calcs = []
        for block in doc.children:
            if isinstance(block, MathBlock):
                calcs.extend(lexer.extract_calculations(block))

        assert len(calcs) == 1
        assert calcs[0].unit_comment == 'kJ'
        assert calcs[0].original_result == '1000'

    def test_compound_unit(self):
        """Test compound unit extraction like m/s."""
        lexer = Lexer()
        doc = lexer.parse('$v == [m/s]$')

        calcs = []
        for block in doc.children:
            if isinstance(block, MathBlock):
                calcs.extend(lexer.extract_calculations(block))

        assert len(calcs) == 1
        assert calcs[0].unit_comment == 'm/s'

    def test_combined_syntax_with_inline_unit(self):
        """Test var := expr == [unit] syntax."""
        lexer = Lexer()
        doc = lexer.parse('$E := 1000\\ J == [kJ]$')

        calcs = []
        for block in doc.children:
            if isinstance(block, MathBlock):
                calcs.extend(lexer.extract_calculations(block))

        assert len(calcs) == 1
        assert calcs[0].operation == ':=_=='
        assert calcs[0].unit_comment == 'kJ'


class TestInlineUnitHintConversion:
    """Test full pipeline with inline unit hints."""

    def test_basic_conversion(self):
        """Test J to kJ conversion via inline hint."""
        content = '$E := 1000000\\ J$\n$E == [kJ]$'
        result, _ = process_text(content)

        assert '$E == 1000\\ \\text{kJ}$' in result

    def test_velocity_conversion(self):
        """Test km/h to m/s conversion."""
        content = '$v := 36\\ \\frac{km}{h}$\n$v == [m/s]$'
        result, _ = process_text(content)

        assert '$v == 10\\ \\text{m/s}$' in result

    def test_time_conversion(self):
        """Test seconds to hours conversion."""
        content = '$t_1 := 3600\\ s$\n$t_1 == [h]$'
        result, _ = process_text(content)

        assert '$t_1 == 1\\ \\text{h}$' in result

    def test_energy_to_kwh(self):
        """Test joules to kWh conversion."""
        content = '$E := 3600000\\ J$\n$E == [kWh]$'
        result, _ = process_text(content)

        assert '$E == 1\\ \\text{kWh}$' in result

    def test_volume_flow_rate(self):
        """Test m³/h to L/s conversion."""
        content = '$Q := 3.6\\ \\frac{m^3}{h}$\n$Q == [L/s]$'
        result, _ = process_text(content)

        assert '$Q == 1\\ \\text{L/s}$' in result


class TestInlineVsHtmlComment:
    """Test precedence and compatibility between inline and HTML comment syntax."""

    def test_html_comment_still_works(self):
        """Verify HTML comment syntax backward compatibility."""
        content = '$E := 1000000\\ J$\n$E ==$ <!-- [kJ] -->'
        result, _ = process_text(content)

        assert '$E == 1000\\ \\text{kJ}$' in result
        assert '<!-- [kJ] -->' in result  # Comment preserved

    def test_html_comment_takes_precedence(self):
        """HTML comment should take precedence when both present."""
        # This is edge case - user shouldn't do this, but HTML wins
        content = '$E := 1000000\\ J$\n$E == [MJ]$ <!-- [kJ] -->'
        result, _ = process_text(content)

        # HTML comment [kJ] takes precedence over inline [MJ]
        assert '\\text{kJ}$' in result


class TestEdgeCases:
    """Test edge cases for inline unit hints."""

    def test_empty_brackets(self):
        """Empty brackets should not be treated as unit hint."""
        lexer = Lexer()
        doc = lexer.parse('$E == []$')

        calcs = []
        for block in doc.children:
            if isinstance(block, MathBlock):
                calcs.extend(lexer.extract_calculations(block))

        # Empty brackets [] are NOT a valid unit hint (need content inside)
        # They remain in original_result
        assert len(calcs) == 1
        assert calcs[0].unit_comment is None
        assert calcs[0].original_result == '[]'

    def test_brackets_not_at_end(self):
        """Brackets not at end should not be treated as unit hint."""
        lexer = Lexer()
        doc = lexer.parse('$x[1] + y[2] ==$')

        calcs = []
        for block in doc.children:
            if isinstance(block, MathBlock):
                calcs.extend(lexer.extract_calculations(block))

        # These are array indices, not unit hints
        assert len(calcs) == 1
        assert calcs[0].unit_comment is None

    def test_invalid_unit_in_brackets(self):
        """Invalid unit should produce an error in output."""
        content = '$E := 1000\\ J$\n$E == [invalid_unit_xyz]$'
        result, _ = process_text(content)

        # Should show an error for invalid unit
        assert 'Error' in result or 'error' in result.lower()

    def test_definition_only_no_unit_hint(self):
        """Pure definition should not be affected."""
        content = '$E := 1000\\ J$'
        result, _ = process_text(content)

        assert '$E := 1000\\ J$' in result
        # No unit conversion attempted
        assert 'kJ' not in result


class TestClearTextPreservesInlineUnitHints:
    """Test that clear_text() preserves inline unit hints."""

    def test_clear_preserves_inline_unit_hint(self):
        """clear_text() should preserve [unit] syntax."""
        from livemathtex.core import clear_text

        # Processed content with inline unit hint
        content = '$E := 1000000\\ J$\n$E == 1000\\ \\text{kJ}$ <!-- [kJ] -->'
        cleared, count = clear_text(content)

        # HTML comment should be preserved
        assert '<!-- [kJ] -->' in cleared
        assert '$E ==$' in cleared or '$E == [kJ]$' in cleared

    def test_clear_preserves_inline_unit_hint_inline_syntax(self):
        """clear_text() should preserve inline [unit] syntax."""
        from livemathtex.core import clear_text

        # Processed content with inline unit hint syntax
        content = '$E := 1000000\\ J$\n$E == 1000\\ \\text{kJ}$'
        # Simulate processed output with inline syntax
        processed = '$E := 1000000\\ J$\n$E == 1000\\ \\text{kJ}$'

        # After processing with inline hint, it would be:
        # $E == 1000\ \text{kJ}$ (no [kJ] visible, it's extracted)
        # But if user writes $E == [kJ]$ in input, clear should preserve it

        # Test with input that has inline hint
        input_with_hint = '$E := 1000000\\ J$\n$E == [kJ]$'
        cleared, count = clear_text(input_with_hint)

        # Should preserve the [kJ] hint
        assert '$E == [kJ]$' in cleared
        assert count == 0  # No evaluation to clear

    def test_clear_preserves_inline_unit_hint_after_processing(self):
        """After processing, clear should restore inline hint."""
        from livemathtex.core import clear_text, process_text

        # Input with inline hint
        input_content = '$E := 1000000\\ J$\n$E == [kJ]$'

        # Process it
        processed, _ = process_text(input_content)
        # Now processed has: $E == 1000\ \text{kJ}$

        # Clear it - should restore to $E == [kJ]$
        cleared, count = clear_text(processed)

        # Should have restored the inline hint
        assert '$E == [kJ]$' in cleared or '$E ==$' in cleared
        assert count == 1  # One evaluation cleared
