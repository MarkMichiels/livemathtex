"""
Snapshot tests for LiveMathTeX examples.

These tests verify that processing examples/*/input.md produces the expected
output in examples/*/output.md. This is the critical regression safety net
for any refactoring or migration work.

Test Philosophy:
- Each example directory is a test case
- input.md is processed through the full pipeline
- Output is compared against output.md
- Any difference fails the test (snapshot testing)
"""

import pytest
from pathlib import Path
import difflib

from livemathtex.core import process_text
from livemathtex.engine.units import reset_unit_registry


def get_example_ids() -> list[str]:
    """Get list of example directory names for parametrization."""
    examples_path = Path(__file__).parent.parent / "examples"
    return [
        d.name
        for d in sorted(examples_path.iterdir())
        if d.is_dir() and (d / "input.md").exists()
    ]


EXAMPLE_IDS = get_example_ids()


def normalize_output(text: str) -> str:
    """
    Normalize output for comparison.

    Handles:
    - Trailing whitespace
    - Timestamp lines (they change on each run)
    - Line ending normalization
    """
    lines = []
    for line in text.split('\n'):
        # Skip timestamp meta line (changes on each run)
        if '<!-- livemathtex-meta -->' in line:
            continue
        # Strip trailing whitespace
        lines.append(line.rstrip())

    # Remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()

    return '\n'.join(lines)


def diff_strings(expected: str, actual: str) -> str:
    """Generate a unified diff between expected and actual strings."""
    expected_lines = expected.split('\n')
    actual_lines = actual.split('\n')

    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile='expected (output.md)',
        tofile='actual (generated)',
        lineterm=''
    )
    return '\n'.join(diff)


@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_snapshot(example_name: str, examples_dir: Path) -> None:
    """
    Test that processing input.md produces the expected output.md.

    This is a snapshot test: the output must match exactly (after normalization).
    If the behavior should change, update output.md to reflect the new expected output.
    """
    example_dir = examples_dir / example_name
    input_file = example_dir / "input.md"
    expected_output_file = example_dir / "output.md"

    # Skip if no output.md exists (example may be work-in-progress)
    if not expected_output_file.exists():
        pytest.skip(f"No output.md found for {example_name}")

    # Reset unit registry to ensure clean state between tests
    reset_unit_registry()

    # Read input file and process
    input_content = input_file.read_text(encoding='utf-8')
    actual_output, ir = process_text(input_content, source=str(input_file))

    # Read expected output
    expected_output = expected_output_file.read_text(encoding='utf-8')

    # Normalize both for comparison
    normalized_expected = normalize_output(expected_output)
    normalized_actual = normalize_output(actual_output)

    # Compare
    if normalized_expected != normalized_actual:
        diff = diff_strings(normalized_expected, normalized_actual)
        pytest.fail(
            f"Output mismatch for example '{example_name}':\n\n{diff}\n\n"
            f"If this change is intentional, update {expected_output_file}"
        )


@pytest.mark.parametrize("example_name", EXAMPLE_IDS)
def test_example_no_crash(example_name: str, examples_dir: Path) -> None:
    """
    Smoke test: verify that processing doesn't crash.

    Even if output doesn't match, the pipeline should not raise exceptions.
    """
    example_dir = examples_dir / example_name
    input_file = example_dir / "input.md"

    # Reset unit registry to ensure clean state between tests
    reset_unit_registry()

    # Read input file and process
    input_content = input_file.read_text(encoding='utf-8')

    # Should not raise any exceptions
    output, ir = process_text(input_content, source=str(input_file))

    # Basic sanity checks
    assert output is not None
    assert len(output) > 0
    assert ir is not None


class TestExampleCoverage:
    """Tests for example coverage and consistency."""

    def test_all_examples_have_input(self, examples_dir: Path) -> None:
        """Every example directory should have an input.md file."""
        for subdir in examples_dir.iterdir():
            if subdir.is_dir() and subdir.name != "images":
                input_file = subdir / "input.md"
                assert input_file.exists(), f"Missing input.md in {subdir.name}"

    def test_all_examples_have_output(self, examples_dir: Path) -> None:
        """Every example with input.md should have output.md."""
        for subdir in examples_dir.iterdir():
            if subdir.is_dir() and (subdir / "input.md").exists():
                output_file = subdir / "output.md"
                assert output_file.exists(), (
                    f"Missing output.md in {subdir.name}. "
                    f"Generate it with: livemathtex {subdir / 'input.md'}"
                )


class TestIROutput:
    """Tests for Intermediate Representation (IR) output."""

    @pytest.mark.parametrize("example_name", EXAMPLE_IDS)
    def test_ir_structure(self, example_name: str, examples_dir: Path) -> None:
        """Verify IR has expected structure."""
        example_dir = examples_dir / example_name
        input_file = example_dir / "input.md"

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text(input_content, source=str(input_file))

        # Check IR has expected fields (IR v2.0 structure)
        assert ir is not None
        assert hasattr(ir, 'symbols')
        assert hasattr(ir, 'stats')
        assert hasattr(ir, 'custom_units')

        # Check stats are populated
        assert ir.stats is not None
        assert 'definitions' in ir.stats
        assert 'evaluations' in ir.stats

        # Check symbols is a dict
        assert isinstance(ir.symbols, dict)
