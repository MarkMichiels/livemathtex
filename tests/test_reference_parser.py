"""Tests for the cross-reference parser."""

import pytest
from livemathtex.parser.reference_parser import (
    Reference,
    extract_references,
    find_math_block_ranges,
    is_in_excluded_range,
    find_processed_references,
    restore_references,
)


class TestFindMathBlockRanges:
    """Tests for math block range detection."""

    def test_inline_math(self):
        content = "Text $x = 1$ more"
        ranges = find_math_block_ranges(content)
        assert any(5 <= start and end <= 12 for start, end in ranges)

    def test_display_math(self):
        content = "Text $$x = 1$$ more"
        ranges = find_math_block_ranges(content)
        assert any(5 <= start and end <= 14 for start, end in ranges)

    def test_code_block_fenced(self):
        content = "Text ```code``` more"
        ranges = find_math_block_ranges(content)
        assert any(start == 5 and end == 15 for start, end in ranges)

    def test_inline_code(self):
        content = "Text `code` more"
        ranges = find_math_block_ranges(content)
        assert any(5 <= start and end <= 11 for start, end in ranges)


class TestExtractReferences:
    """Tests for reference extraction."""

    def test_simple_variable(self):
        content = "The value is {{C_{max}}}."
        refs = extract_references(content)
        assert len(refs) == 1
        assert refs[0].content == "C_{max}"
        assert refs[0].start == 13
        assert refs[0].end == 24  # {{C_{max}}} is 11 chars: 13+11=24

    def test_multiple_references(self):
        content = "Start {{A}} middle {{B}} end"
        refs = extract_references(content)
        assert len(refs) == 2
        assert refs[0].content == "A"
        assert refs[1].content == "B"

    def test_expression(self):
        content = "Ratio is {{T_2030 / C_max * 100}}%"
        refs = extract_references(content)
        assert len(refs) == 1
        assert refs[0].content == "T_2030 / C_max * 100"

    def test_no_references(self):
        content = "Plain text without any references."
        refs = extract_references(content)
        assert len(refs) == 0

    def test_skip_in_math_block(self):
        # References inside math blocks should be ignored
        content = "Text $x = {{A}}$ more"
        refs = extract_references(content)
        assert len(refs) == 0

    def test_skip_in_code_block(self):
        content = "Text ```{{A}}``` more"
        refs = extract_references(content)
        assert len(refs) == 0

    def test_skip_in_inline_code(self):
        content = "Text `{{A}}` more"
        refs = extract_references(content)
        assert len(refs) == 0

    def test_escaped_reference(self):
        # Escaped \{{ should not be captured
        content = r"Text \{{not a ref}} more"
        refs = extract_references(content)
        assert len(refs) == 0

    def test_reference_with_subscript(self):
        content = "Value: {{P_{LED,out}}}"
        refs = extract_references(content)
        assert len(refs) == 1
        assert refs[0].content == "P_{LED,out}"

    def test_reference_with_greek_letter(self):
        content = r"Rate: {{\gamma_{max}}}"
        refs = extract_references(content)
        assert len(refs) == 1
        assert refs[0].content == r"\gamma_{max}"


class TestFindProcessedReferences:
    """Tests for finding already-processed references."""

    def test_simple_processed(self):
        content = "Value is 550 kg<!-- {{C_{max}}} -->"
        results = find_processed_references(content)
        assert len(results) == 1
        start, end, ref_content = results[0]
        assert ref_content == "C_{max}"
        # Only matches "550 kg<!-- {{C_{max}}} -->" not "Value is "
        assert start == 9

    def test_multiple_processed(self):
        content = "A is 100<!-- {{A}} --> and B is 200<!-- {{B}} -->"
        results = find_processed_references(content)
        assert len(results) == 2
        assert results[0][2] == "A"
        assert results[1][2] == "B"

    def test_no_processed(self):
        content = "Plain text without processed references"
        results = find_processed_references(content)
        assert len(results) == 0


class TestRestoreReferences:
    """Tests for restoring processed references back to original syntax."""

    def test_simple_restore(self):
        content = "Value is 550 kg<!-- {{C_{max}}} -->"
        restored, count = restore_references(content)
        # Preserves text before the value, restores {{ref}} for the value part
        assert restored == "Value is {{C_{max}}}"
        assert count == 1

    def test_multiple_restore(self):
        content = "A is 100<!-- {{A}} --> and B is 200<!-- {{B}} -->"
        restored, count = restore_references(content)
        assert restored == "A is {{A}} and B is {{B}}"
        assert count == 2

    def test_no_references_to_restore(self):
        content = "Plain text"
        restored, count = restore_references(content)
        assert restored == "Plain text"
        assert count == 0

    def test_expression_restore(self):
        content = "Ratio: 93.8%<!-- {{T / C * 100}} -->"
        restored, count = restore_references(content)
        assert restored == "Ratio: {{T / C * 100}}"
        assert count == 1


class TestRoundTrip:
    """Tests for process → restore round-trip consistency."""

    def test_roundtrip_preserves_content(self):
        """After restore, content should be ready for re-processing."""
        # Simulate processed content
        processed = "The capacity is 550 kg<!-- {{C_{max}}} -->."
        restored, _ = restore_references(processed)
        assert restored == "The capacity is {{C_{max}}}."
        # Should have original reference ready for next process cycle
