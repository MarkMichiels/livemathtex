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

IR Schema Tests:
- v2.0: Legacy schema for backward compatibility
- v3.0: New schema with clean IDs, Pint integration, custom unit metadata
"""

import pytest
from pathlib import Path
import difflib

from livemathtex.core import process_text, process_text_v3
from livemathtex.engine.units import reset_unit_registry
from livemathtex.ir.schema import (
    LivemathIR, SymbolEntry, ValueWithUnit,
    LivemathIRV3, SymbolEntryV3, CustomUnitEntry, FormulaInfo
)


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
    def test_ir_v2_structure(self, example_name: str, examples_dir: Path) -> None:
        """Verify IR v2.0 has expected structure (backward compatibility)."""
        example_dir = examples_dir / example_name
        input_file = example_dir / "input.md"

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text(input_content, source=str(input_file))

        # Check IR v2.0 has expected fields
        assert ir is not None
        assert isinstance(ir, LivemathIR)
        assert hasattr(ir, 'symbols')
        assert hasattr(ir, 'stats')
        assert hasattr(ir, 'custom_units')

        # Check version
        assert ir.version == "2.0"

        # Check stats are populated
        assert ir.stats is not None
        assert 'definitions' in ir.stats
        assert 'evaluations' in ir.stats

        # Check symbols is a dict
        assert isinstance(ir.symbols, dict)

    @pytest.mark.parametrize("example_name", EXAMPLE_IDS)
    def test_ir_v3_structure(self, example_name: str, examples_dir: Path) -> None:
        """Verify IR v3.0 has expected structure with clean IDs and Pint integration."""
        example_dir = examples_dir / example_name
        input_file = example_dir / "input.md"

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text_v3(input_content, source=str(input_file))

        # Check IR v3.0 has expected fields
        assert ir is not None
        assert isinstance(ir, LivemathIRV3)
        assert ir.version == "3.0"

        # Check unit_backend is populated (Pint)
        assert 'name' in ir.unit_backend
        assert ir.unit_backend['name'] == 'pint'
        assert 'version' in ir.unit_backend

        # Check stats are populated
        assert ir.stats is not None
        assert 'definitions' in ir.stats
        assert 'evaluations' in ir.stats
        assert 'custom_units' in ir.stats

        # Check symbols structure
        assert isinstance(ir.symbols, dict)

        # Check each symbol has v3.0 structure
        for clean_id, entry in ir.symbols.items():
            assert isinstance(entry, SymbolEntryV3)
            assert hasattr(entry, 'latex_name')
            assert hasattr(entry, 'original')
            assert hasattr(entry, 'base')
            assert hasattr(entry, 'conversion_ok')
            assert isinstance(entry.original, ValueWithUnit)
            assert isinstance(entry.base, ValueWithUnit)

        # Check custom_units structure
        assert isinstance(ir.custom_units, dict)
        for unit_name, unit_entry in ir.custom_units.items():
            assert isinstance(unit_entry, CustomUnitEntry)
            assert hasattr(unit_entry, 'latex')
            assert hasattr(unit_entry, 'type')
            assert hasattr(unit_entry, 'pint_definition')
            assert hasattr(unit_entry, 'line')

    @pytest.mark.parametrize("example_name", EXAMPLE_IDS)
    def test_ir_v3_symbol_values(self, example_name: str, examples_dir: Path) -> None:
        """Verify IR v3.0 symbol values are properly populated."""
        example_dir = examples_dir / example_name
        input_file = example_dir / "input.md"

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text_v3(input_content, source=str(input_file))

        # Check that symbols have values
        for clean_id, entry in ir.symbols.items():
            # latex_name should be populated
            assert entry.latex_name, f"Symbol {clean_id} has no latex_name"

            # original value should exist for defined symbols
            if entry.original.value is not None:
                assert isinstance(entry.original.value, (int, float))

            # conversion_ok should be True for valid conversions
            if entry.conversion_ok:
                # If there was a unit, base should also have a value
                if entry.original.unit and entry.original.value is not None:
                    assert entry.base.value is not None, \
                        f"Symbol {clean_id} has unit but no base value"

    @pytest.mark.parametrize("example_name", EXAMPLE_IDS)
    def test_ir_v3_formulas(self, example_name: str, examples_dir: Path) -> None:
        """Verify IR v3.0 formula tracking (if any formulas exist)."""
        example_dir = examples_dir / example_name
        input_file = example_dir / "input.md"

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text_v3(input_content, source=str(input_file))

        # Check formulas have proper structure
        for clean_id, entry in ir.symbols.items():
            if entry.formula:
                assert isinstance(entry.formula, FormulaInfo)
                assert hasattr(entry.formula, 'expression')
                assert hasattr(entry.formula, 'depends_on')
                assert isinstance(entry.formula.depends_on, list)

                # If formula has parameters, check they're properly structured
                if entry.formula.parameters:
                    assert isinstance(entry.formula.parameters, list)
                    assert len(entry.formula.parameters) > 0

                    # parameter_latex should match parameters length
                    if entry.formula.parameter_latex:
                        assert len(entry.formula.parameter_latex) == len(entry.formula.parameters)


class TestIRV3Specific:
    """Tests for specific IR v3.0 features."""

    def test_engineering_units_custom_units(self, examples_dir: Path) -> None:
        """Test that engineering-units example extracts custom unit metadata."""
        example_dir = examples_dir / "engineering-units"
        input_file = example_dir / "input.md"

        if not input_file.exists():
            pytest.skip("engineering-units example not found")

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text_v3(input_content, source=str(input_file))

        # Check custom units were extracted (if any defined in example)
        # This test verifies the custom unit extraction mechanism works
        assert ir.custom_units is not None
        assert isinstance(ir.custom_units, dict)

        # If custom units are defined, check their structure
        for unit_name, entry in ir.custom_units.items():
            assert entry.latex, f"Custom unit {unit_name} has no latex"
            assert entry.type in ["base", "derived", "compound", "alias"], \
                f"Custom unit {unit_name} has invalid type: {entry.type}"
            assert entry.pint_definition, f"Custom unit {unit_name} has no pint_definition"
            assert entry.line > 0, f"Custom unit {unit_name} has no line number"

    def test_pint_unit_conversion(self, examples_dir: Path) -> None:
        """Test that Pint-based unit conversion works in IR v3.0."""
        # Use simple-units example which has unit conversions
        example_dir = examples_dir / "simple-units"
        input_file = example_dir / "input.md"

        if not input_file.exists():
            pytest.skip("simple-units example not found")

        reset_unit_registry()
        input_content = input_file.read_text(encoding='utf-8')
        _, ir = process_text_v3(input_content, source=str(input_file))

        # Check that at least some symbols have unit conversions
        symbols_with_units = [
            (clean_id, entry) for clean_id, entry in ir.symbols.items()
            if entry.original.unit
        ]

        if not symbols_with_units:
            pytest.skip("No symbols with units found in simple-units example")

        # Check each symbol with units has base conversion
        for clean_id, entry in symbols_with_units:
            if entry.conversion_ok:
                # Base value should be populated
                assert entry.base.value is not None, \
                    f"Symbol {clean_id} ({entry.latex_name}) missing base value"
                # Check that values are numeric
                assert isinstance(entry.original.value, (int, float))
                assert isinstance(entry.base.value, (int, float))

    def test_ir_v3_no_crash_all_examples(self, examples_dir: Path) -> None:
        """Smoke test: verify IR v3.0 processing doesn't crash for any example."""
        for subdir in sorted(examples_dir.iterdir()):
            if not subdir.is_dir():
                continue
            input_file = subdir / "input.md"
            if not input_file.exists():
                continue

            reset_unit_registry()
            input_content = input_file.read_text(encoding='utf-8')

            # Should not raise any exceptions
            try:
                output, ir = process_text_v3(input_content, source=str(input_file))
                assert output is not None
                assert ir is not None
                assert ir.version == "3.0"
            except Exception as e:
                pytest.fail(f"IR v3.0 processing crashed for {subdir.name}: {e}")
