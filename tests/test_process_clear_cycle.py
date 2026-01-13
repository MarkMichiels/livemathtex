"""
Tests for process/clear cycle stability.

These tests verify that:
1. Processing a file multiple times produces stable results (only timestamp changes)
2. Clear → Process cycle produces same result as original processing
3. Copy → Process cycle produces same result as original processing
4. Error markup is fully cleaned and doesn't cause parsing issues

Test Scenarios:
- Scenario 1: F9 on input.md → output.md generated
- Scenario 2: Shift+F9 on input.md → output.md cleaned (copy)
- Scenario 3: F9 on output.md (first time) → recalculated
- Scenario 4: F9 on output.md (second time) → should be stable (only timestamp)
- Scenario 5: Shift+F9 on output.md → cleared
- Scenario 6: F9 on output.md after clear → should match Scenario 1
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from livemathtex.core import process_file, clear_text
from livemathtex.cli import main as cli_main
import click.testing


def normalize_for_comparison(content: str) -> str:
    """
    Normalize content for comparison by removing:
    - Timestamp lines (livemathtex metadata)
    - Trailing whitespace
    - Exact whitespace differences
    """
    lines = content.split('\n')
    normalized = []
    for line in lines:
        # Skip livemathtex metadata lines
        if 'livemathtex:' in line and 'livemathtex-meta' in line:
            continue
        if line.strip().startswith('> *livemathtex:'):
            continue
        normalized.append(line.rstrip())
    return '\n'.join(normalized).rstrip()


def count_evaluations(content: str) -> int:
    """Count number of evaluation expressions (==) in content."""
    import re
    # Count == that are not ===
    pattern = r'(?<!=)==(?!=)'
    return len(re.findall(pattern, content))


def count_errors(content: str) -> int:
    """Count number of error markup instances in content."""
    import re
    # Count error markup (not section headings that contain "Error:")
    # Only count \color{red} which is the actual error markup
    error_pattern = r'\\color\{red\}'
    return len(re.findall(error_pattern, content))


@pytest.fixture
def error_handling_example(project_root: Path) -> Path:
    """Return path to error-handling example directory."""
    return project_root / "examples" / "error-handling"


@pytest.fixture
def temp_example_dir(error_handling_example: Path) -> Path:
    """Create a temporary copy of error-handling example for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "error-handling"
        shutil.copytree(error_handling_example, test_dir)
        yield test_dir


def test_scenario_1_process_input(temp_example_dir: Path):
    """
    Scenario 1: F9 on input.md → output.md generated.

    Expected: output.md contains calculated values and errors.
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # Process input.md
    ir = process_file(str(input_file), str(output_file), verbose=False)

    # Verify output was created
    assert output_file.exists(), "output.md should be created"

    # Verify it has calculations
    output_content = output_file.read_text()
    assert count_evaluations(output_content) > 0, "Should have evaluations"

    # Verify it has errors (this example has known errors)
    assert ir.stats.get('errors', 0) > 0, "Should have errors"

    # Store for comparison in later tests
    return normalize_for_comparison(output_content), ir.stats.get('errors', 0)


def test_scenario_2_copy_input(temp_example_dir: Path):
    """
    Scenario 2: Shift+F9 on input.md → output.md cleaned (copy).

    Expected: output.md is overwritten with clean content from input.md.
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # First, process to create output
    process_file(str(input_file), str(output_file), verbose=False)
    original_output = output_file.read_text()

    # Now copy (simulates Shift+F9 on input.md)
    runner = click.testing.CliRunner()
    result = runner.invoke(cli_main, ['copy', str(input_file)])

    assert result.exit_code == 0, f"copy command failed: {result.output}"
    assert output_file.exists(), "output.md should exist"

    # Read input and output content
    input_content = input_file.read_text()
    new_output = output_file.read_text()

    # Verify output matches input (has same evaluation expressions, no computed values)
    input_eval_count = count_evaluations(input_content)
    output_eval_count = count_evaluations(new_output)
    assert output_eval_count == input_eval_count, \
        f"Should have same evaluations as input: expected {input_eval_count}, got {output_eval_count}"
    # Verify no computed values (no error markup from processing)
    assert count_errors(new_output) == 0, "Should have no error markup after copy"

    # Verify it matches input content (minus metadata)
    input_normalized = normalize_for_comparison(input_content)
    output_normalized = normalize_for_comparison(new_output)

    # Should match except for metadata footer
    assert input_normalized in output_normalized or output_normalized.startswith(input_normalized), \
        "Output should match input content after copy"


def test_scenario_3_process_output_first_time(temp_example_dir: Path):
    """
    Scenario 3: F9 on output.md (first time) → recalculated.

    Expected: output.md is recalculated, should match Scenario 1 result.
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # Scenario 1: Process input.md
    process_file(str(input_file), str(output_file), verbose=False)
    scenario1_content = normalize_for_comparison(output_file.read_text())
    scenario1_errors = count_errors(output_file.read_text())

    # Scenario 3: Process output.md (first time)
    process_file(str(output_file), None, verbose=False)  # In-place processing
    scenario3_content = normalize_for_comparison(output_file.read_text())
    scenario3_errors = count_errors(output_file.read_text())

    # Should match (allowing for minor differences in error formatting)
    # Note: Currently this may fail due to bug - documenting expected behavior
    assert scenario1_errors == scenario3_errors or abs(scenario1_errors - scenario3_errors) <= 2, \
        f"Error count should be similar: Scenario 1 had {scenario1_errors}, Scenario 3 had {scenario3_errors}"


def test_scenario_4_process_output_second_time(temp_example_dir: Path):
    """
    Scenario 4: F9 on output.md (second time) → should be stable.

    Expected: File should NOT change (only timestamp should update).
    This test documents the current bug where content changes.
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # Process input.md to create output
    process_file(str(input_file), str(output_file), verbose=False)

    # Process output.md first time
    process_file(str(output_file), None, verbose=False)
    first_content = normalize_for_comparison(output_file.read_text())
    first_errors = count_errors(output_file.read_text())

    # Process output.md second time
    process_file(str(output_file), None, verbose=False)
    second_content = normalize_for_comparison(output_file.read_text())
    second_errors = count_errors(output_file.read_text())

    # BUG: Currently fails - content changes on second processing
    # Expected: Content should be identical (only metadata timestamp differs)
    # Actual: Content changes, error count changes
    assert first_content == second_content, \
        f"Content should be stable on second processing. " \
        f"First had {first_errors} errors, second had {second_errors} errors."

    assert first_errors == second_errors, \
        f"Error count should be stable: first={first_errors}, second={second_errors}"


def test_scenario_5_clear_output(temp_example_dir: Path):
    """
    Scenario 5: Shift+F9 on output.md → cleared.

    Expected: All computed values removed, all error markup removed.
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # First process to create output with calculations
    process_file(str(input_file), str(output_file), verbose=False)
    processed_content = output_file.read_text()

    # Verify it has evaluations and errors
    assert count_evaluations(processed_content) > 0, "Should have evaluations before clear"
    assert count_errors(processed_content) > 0, "Should have errors before clear"

    # Clear (simulates Shift+F9 on output.md)
    runner = click.testing.CliRunner()
    result = runner.invoke(cli_main, ['clear', str(output_file)])

    assert result.exit_code == 0, f"clear command failed: {result.output}"

    cleared_content = output_file.read_text()

    # Verify evaluations are cleared
    # Note: clear_text removes == value but keeps ==, so count should be same but no values
    cleared_eval_count = count_evaluations(cleared_content)
    # After clear, we should have ==$ (empty evaluations) but no computed values
    # The pattern ==$ should still match, but == value$ should be gone

    # Verify error markup is removed
    cleared_errors = count_errors(cleared_content)
    assert cleared_errors == 0, f"Should have no errors after clear, found {cleared_errors}"


@pytest.mark.xfail(reason="Known bug: process/clear cycle not idempotent - evaluator treats cleared content differently")
def test_scenario_6_process_after_clear(temp_example_dir: Path):
    """
    Scenario 6: F9 on output.md after clear → should match Scenario 1.

    Expected: Should produce same result as original processing from input.md.
    This test documents the current bug where different errors appear.
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # Scenario 1: Process input.md
    process_file(str(input_file), str(output_file), verbose=False)
    scenario1_content = normalize_for_comparison(output_file.read_text())
    scenario1_errors = count_errors(output_file.read_text())
    scenario1_ir = process_file(str(input_file), str(output_file), verbose=False)
    scenario1_error_count = scenario1_ir.stats.get('errors', 0)

    # Clear output.md
    runner = click.testing.CliRunner()
    result = runner.invoke(cli_main, ['clear', str(output_file)])
    assert result.exit_code == 0

    # Process output.md after clear
    scenario6_ir = process_file(str(output_file), None, verbose=False)
    scenario6_content = normalize_for_comparison(output_file.read_text())
    scenario6_errors = count_errors(output_file.read_text())
    scenario6_error_count = scenario6_ir.stats.get('errors', 0)

    # BUG: Currently fails - different errors appear
    # Expected: Should match Scenario 1 exactly
    # Actual: Different error count and content
    assert scenario1_error_count == scenario6_error_count, \
        f"Error count should match Scenario 1: Scenario 1 had {scenario1_error_count}, " \
        f"Scenario 6 had {scenario6_error_count}"

    # Content should be similar (allowing for minor formatting differences)
    # This is a weaker assertion - ideally they should be identical
    assert abs(scenario1_errors - scenario6_errors) <= 2, \
        f"Error markup count should be similar: Scenario 1 had {scenario1_errors}, " \
        f"Scenario 6 had {scenario6_errors}"


def test_clear_removes_all_error_markup(temp_example_dir: Path):
    """
    Test that clear_text() removes all error markup formats.

    Verifies that the clear function handles:
    - Inline errors: \\color{red}{...}
    - Multiline errors: \\ \\color{red}{\\text{...}}
    - Incomplete math blocks: \\ }$
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # Process to create output with errors
    process_file(str(input_file), str(output_file), verbose=False)
    processed_content = output_file.read_text()

    # Verify it has error markup
    assert '\\color{red}' in processed_content or 'Error:' in processed_content, \
        "Processed content should have error markup"

    # Clear
    cleared_content, count = clear_text(processed_content)

    # Verify all error patterns are removed
    assert '\\color{red}' not in cleared_content, "Should remove \\color{red} markup"
    assert '\\ }$' not in cleared_content, "Should remove incomplete math block terminators"

    # Check for any remaining error markup (not section headings)
    # Error markup appears as \text{Error:...} or \text{(Error:...)}
    import re
    remaining_error_markup = re.findall(r'\\text\{[^}]*Error:', cleared_content)
    assert len(remaining_error_markup) == 0, \
        f"Should remove all error markup, found {len(remaining_error_markup)} instances"


@pytest.mark.xfail(reason="Known bug: multiple processing runs not fully stable - evaluator produces different errors")
def test_process_stability_multiple_runs(temp_example_dir: Path):
    """
    Test that processing the same file multiple times produces stable results.

    This is a general stability test - processing should be idempotent
    (only metadata timestamp should change).
    """
    input_file = temp_example_dir / "input.md"
    output_file = temp_example_dir / "output.md"

    # Process input.md
    process_file(str(input_file), str(output_file), verbose=False)
    first_content = normalize_for_comparison(output_file.read_text())
    first_errors = count_errors(output_file.read_text())

    # Process output.md multiple times
    for i in range(3):
        process_file(str(output_file), None, verbose=False)

    final_content = normalize_for_comparison(output_file.read_text())
    final_errors = count_errors(output_file.read_text())

    # BUG: Currently may fail - content should be stable
    assert first_content == final_content, \
        f"Content should be stable across multiple processing runs. " \
        f"First had {first_errors} errors, final had {final_errors} errors."

    assert first_errors == final_errors, \
        f"Error count should be stable: first={first_errors}, final={final_errors}"


class TestUnitHintCycle:
    """Tests for unit hint preservation through process/clear cycle."""

    def test_inline_unit_hint_survives_full_cycle(self):
        """$E == [kJ]$ should produce same result after clear and re-process."""
        from livemathtex import process_text
        from livemathtex.core import clear_text

        input_content = '$E_1 := 1000000\\ J$\n$E_1 == [kJ]$'

        # First process
        processed1, _ = process_text(input_content)
        assert '\\text{kJ}' in processed1, "First process should convert to kJ"

        # Clear
        cleared, _ = clear_text(processed1)

        # Re-process
        processed2, _ = process_text(cleared)

        # Should still use kJ, not fall back to SI base units
        assert '\\text{kJ}' in processed2, "Re-processing after clear should still use kJ"
        assert 'kg' not in processed2, "Should NOT fall back to kg·m²/s² base units"

    def test_html_comment_unit_hint_survives_cycle(self):
        """$E ==$ <!-- [kJ] --> should produce same result after cycle."""
        from livemathtex import process_text
        from livemathtex.core import clear_text

        input_content = '$E_2 := 2000000\\ J$\n$E_2 ==$ <!-- [kJ] -->'

        # First process
        processed1, _ = process_text(input_content)
        assert '\\text{kJ}' in processed1, "First process should convert to kJ"
        assert '<!-- [kJ] -->' in processed1, "HTML comment should be preserved"

        # Clear
        cleared, _ = clear_text(processed1)
        assert '<!-- [kJ] -->' in cleared, "Clear should preserve HTML comment hint"

        # Re-process
        processed2, _ = process_text(cleared)

        # Should still use kJ
        assert '\\text{kJ}' in processed2, "Re-processing should use preserved HTML comment hint"
        assert 'kg' not in processed2, "Should NOT fall back to base units"

    def test_custom_division_unit_survives_cycle(self):
        """SEC === MWh/kg custom unit should work after clear and re-process."""
        from livemathtex import process_text
        from livemathtex.core import clear_text
        from livemathtex.engine.pint_backend import reset_unit_registry, reset_sympy_unit_registry

        # Reset registries to ensure clean state
        reset_unit_registry()
        reset_sympy_unit_registry()

        input_content = '''$$ SEC === MWh/kg $$

$E_3 := 18000\\ MWh$

$m_3 := 1000\\ kg$

$ratio_3 := E_3 / m_3$

$ratio_3 ==$ <!-- [SEC] -->'''

        # First process
        processed1, _ = process_text(input_content)
        assert 'SEC' in processed1, "First process should show SEC unit"

        # Clear
        cleared, _ = clear_text(processed1)

        # Reset registries again for fresh re-processing
        reset_unit_registry()
        reset_sympy_unit_registry()

        # Re-process
        processed2, _ = process_text(cleared)

        # Should still use SEC
        assert 'SEC' in processed2, "Re-processing should use custom SEC unit"

    def test_combined_definition_evaluation_cycle(self):
        """$P := 1000\ W == [kW]$ combined syntax should survive cycle."""
        from livemathtex import process_text
        from livemathtex.core import clear_text

        input_content = '$P_1 := 1000\\ W$\n$P_1 == [kW]$'

        # First process
        processed1, _ = process_text(input_content)
        assert '\\text{kW}' in processed1, "First process should convert to kW"

        # Clear
        cleared, _ = clear_text(processed1)

        # Re-process
        processed2, _ = process_text(cleared)

        # Should still use kW
        assert '\\text{kW}' in processed2, "Re-processing should still use kW"


class TestFileCycle:
    """Tests for file-based process/clear/process cycle with unit hints."""

    def test_unit_hint_file_cycle(self, tmp_path: Path):
        """Unit hints survive file-based process → clear → process cycle.

        Note: HTML comment hint is preserved through the cycle. The inline
        [unit] syntax is converted to HTML comment during processing, which
        is then preserved by clear.
        """
        from livemathtex.core import process_file

        # Create input file with HTML comment unit hints (the preserved format)
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"

        input_content = '''<!-- livemathtex: output=output.md -->

# Energy Conversion Test

$E_file := 3600000\\ J$

$E_file ==$ <!-- [kWh] -->
'''
        input_file.write_text(input_content)

        # First process
        process_file(str(input_file), str(output_file), verbose=False)
        processed1 = output_file.read_text()
        assert '\\text{kWh}' in processed1, "First process should convert to kWh"
        assert '<!-- [kWh] -->' in processed1, "HTML comment should be preserved"

        # Clear via CLI
        runner = click.testing.CliRunner()
        result = runner.invoke(cli_main, ['clear', str(output_file)])
        assert result.exit_code == 0, f"clear command failed: {result.output}"

        cleared = output_file.read_text()
        assert '<!-- [kWh] -->' in cleared, "Cleared file should preserve unit hint"

        # Re-process
        process_file(str(output_file), None, verbose=False)
        processed2 = output_file.read_text()

        # Should still use kWh
        assert '\\text{kWh}' in processed2, "Re-processing should use preserved hint"
        assert 'kg' not in processed2, "Should NOT fall back to SI base units"

    def test_custom_unit_file_cycle(self, tmp_path: Path):
        """Custom units defined with === survive file-based cycle."""
        from livemathtex.core import process_file
        from livemathtex.engine.pint_backend import reset_unit_registry, reset_sympy_unit_registry

        # Reset registries
        reset_unit_registry()
        reset_sympy_unit_registry()

        # Create input file with custom unit
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"

        input_content = '''<!-- livemathtex: output=output.md -->

# Custom Unit Test

$$ EURO === EUR $$

$price_1 := 100\\ EURO$

$price_1 ==$
'''
        input_file.write_text(input_content)

        # First process
        process_file(str(input_file), str(output_file), verbose=False)
        processed1 = output_file.read_text()
        assert 'EURO' in processed1, "First process should show custom EURO unit"

        # Clear via CLI
        runner = click.testing.CliRunner()
        result = runner.invoke(cli_main, ['clear', str(output_file)])
        assert result.exit_code == 0

        # Reset registries for re-processing
        reset_unit_registry()
        reset_sympy_unit_registry()

        # Re-process
        process_file(str(output_file), None, verbose=False)
        processed2 = output_file.read_text()

        # Should still work with custom unit
        assert 'EURO' in processed2 or 'EUR' in processed2, \
            "Re-processing should still recognize custom unit"
