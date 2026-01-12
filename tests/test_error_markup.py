"""Tests for error markup detection and cleanup (ISS-016)."""

import pytest
from livemathtex import process_text, detect_error_markup


class TestDetectErrorMarkup:
    """Test error markup detection function."""

    def test_no_errors(self):
        """Clean content should return no errors."""
        content = '$E := 100\\ J$'
        result = detect_error_markup(content)
        assert result['has_errors'] is False
        assert result['count'] == 0
        assert result['has_meta'] is False

    def test_detect_color_red(self):
        """Should detect \\color{red} error markup."""
        content = '$E == \\color{red}{\\text{Error: undefined}}$'
        result = detect_error_markup(content)
        assert result['has_errors'] is True
        assert result['count'] >= 1
        assert 'color{red}' in result['patterns']

    def test_detect_inline_error(self):
        """Should detect inline Error: text."""
        content = '$E == \\text{(Error: something)}$'
        result = detect_error_markup(content)
        assert result['has_errors'] is True
        assert 'text{Error}' in result['patterns']

    def test_detect_meta(self):
        """Should detect livemathtex-meta comment."""
        content = '> *livemathtex: info* <!-- livemathtex-meta -->'
        result = detect_error_markup(content)
        assert result['has_meta'] is True
        assert 'livemathtex-meta' in result['patterns']

    def test_detect_multiple_errors(self):
        """Should count multiple error occurrences."""
        content = '''$x == \\color{red}{error1}$
$y == \\color{red}{error2}$
$z == \\text{(Error: third)}$'''
        result = detect_error_markup(content)
        assert result['has_errors'] is True
        assert result['count'] == 3  # 2 color{red} + 1 text{Error}


class TestProcessTextAutoClean:
    """Test that process_text() auto-cleans error markup."""

    def test_auto_cleans_error_markup(self):
        """process_text() should auto-clean existing error markup."""
        # Content with error markup from previous run
        content = '''$E := 100\\ J$
$E ==
\\\\ \\color{red}{\\text{Error: something}}$'''

        result, _ = process_text(content)

        # Should NOT contain original error
        assert '\\color{red}' not in result
        # Should have new evaluation (100 J)
        assert '100' in result

    def test_auto_cleans_meta(self):
        """process_text() should remove livemathtex-meta before processing."""
        content = '''$E := 100\\ J$

---

> *livemathtex: 2026-01-12 | 1 definition | no errors | 0.01s* <!-- livemathtex-meta -->
'''
        result, _ = process_text(content)

        # Should have exactly one meta block (the new one)
        assert result.count('livemathtex-meta') == 1

    def test_reprocess_with_errors_produces_clean_output(self):
        """Re-processing output with errors should produce clean new output."""
        # First: create a definition that will work
        content = '$x := 42$\n$x ==$'
        result1, _ = process_text(content)

        # result1 should have evaluation
        assert '42' in result1 or 'x ==' in result1

        # Re-processing should produce same consistent result
        result2, _ = process_text(result1)

        # Should not accumulate errors or meta blocks
        assert result2.count('livemathtex-meta') == 1

    def test_auto_clean_preserves_valid_content(self):
        """Auto-cleaning should not remove valid content."""
        # Content with error markup AND valid expressions
        # Use subscripted names to avoid unit conflicts (a=year, b=barn)
        content = '''$a_1 := 10$
$a_1 ==
\\\\ \\color{red}{\\text{Error: old error}}$
$b_1 := 20$
$b_1 ==$'''

        result, _ = process_text(content)

        # Valid definitions should be processed
        assert '$a_1 := 10$' in result or '$a_{1} := 10$' in result
        assert '$b_1 := 20$' in result or '$b_{1} := 20$' in result
        # Error should be cleaned
        assert '\\color{red}' not in result
        # New evaluations should be present
        assert '10' in result
        assert '20' in result
