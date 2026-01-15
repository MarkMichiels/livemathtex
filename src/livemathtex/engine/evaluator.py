"""
LiveMathTeX Evaluator - Core calculation engine.

Symbol Normalization uses a simple v_{n} / f_{n} naming scheme:
- Variables: v_{0}, v_{1}, v_{2}, ...
- Functions: f_{0}, f_{1}, f_{2}, ...

This approach ensures 100% latex2sympy compatibility:
- Original: "P_{LED,out} * N_{MPC}"
- Internal: "v_{0} * v_{1}"

The NameGenerator in symbols.py manages the bidirectional mapping:
- latex_name (P_{LED,out}) <-> internal_id (v_{0})

See ARCHITECTURE.md for full documentation.
"""

from typing import Dict, Any, Optional, List, Tuple
import logging
import re
import sympy

logger = logging.getLogger(__name__)
import sympy.physics.units as u
from sympy.parsing.latex import parse_latex

try:
    from latex2sympy2 import latex2sympy
except ImportError:
    def latex2sympy(latex_str):
        try:
            return sympy.sympify(latex_str)
        except:
            return sympy.Symbol(latex_str)

from .symbols import SymbolTable
from .pint_backend import (
    get_sympy_unit_registry as get_unit_registry,
    UnitRegistry,
    evaluate_sympy_ast_with_pint,
    build_pint_symbol_map,
    PintEvaluationError,
    get_unit_registry as get_pint_registry,
    format_unit_latex,
)
from .token_classifier import TokenClassifier
from .expression_evaluator import evaluate_expression_tree, EvaluationError as CustomEvaluationError
from ..parser.models import Calculation
from ..parser.expression_tokenizer import ExpressionTokenizer
from ..parser.expression_parser import ExpressionParser, ParseError
from ..utils.errors import EvaluationError, UndefinedVariableError, UnitConversionWarning
from ..ir.schema import LivemathIR, SymbolEntry
from ..config import LivemathConfig

# Greek letter mappings for display purposes
GREEK_LETTERS = {
    '\\alpha': 'alpha', '\\beta': 'beta', '\\gamma': 'gamma', '\\delta': 'delta',
    '\\epsilon': 'epsilon', '\\zeta': 'zeta', '\\eta': 'eta', '\\theta': 'theta',
    '\\iota': 'iota', '\\kappa': 'kappa', '\\lambda': 'lambda', '\\mu': 'mu',
    '\\nu': 'nu', '\\xi': 'xi', '\\pi': 'pi', '\\rho': 'rho', '\\sigma': 'sigma',
    '\\tau': 'tau', '\\upsilon': 'upsilon', '\\phi': 'phi', '\\chi': 'chi',
    '\\psi': 'psi', '\\omega': 'omega',
    '\\Alpha': 'Alpha', '\\Beta': 'Beta', '\\Gamma': 'Gamma', '\\Delta': 'Delta',
    '\\Epsilon': 'Epsilon', '\\Zeta': 'Zeta', '\\Eta': 'Eta', '\\Theta': 'Theta',
    '\\Iota': 'Iota', '\\Kappa': 'Kappa', '\\Lambda': 'Lambda', '\\Mu': 'Mu',
    '\\Nu': 'Nu', '\\Xi': 'Xi', '\\Pi': 'Pi', '\\Rho': 'Rho', '\\Sigma': 'Sigma',
    '\\Tau': 'Tau', '\\Upsilon': 'Upsilon', '\\Phi': 'Phi', '\\Chi': 'Chi',
    '\\Psi': 'Psi', '\\Omega': 'Omega',
}
GREEK_LETTERS_REVERSE = {v: k for k, v in GREEK_LETTERS.items()}

class Evaluator:
    """
    Executes calculations using SymPy and a SymbolTable.
    """

    # ISSUE-002: RESERVED_UNIT_NAMES removed.
    # Unit detection now uses Pint backend: is_known_unit(), is_unit_token(),
    # and check_variable_name_conflict() from pint_backend.py.

    def __init__(self, config: Optional[LivemathConfig] = None):
        """
        Initialize the evaluator with optional configuration.

        Args:
            config: LivemathConfig instance. If None, uses defaults.
        """
        self.config = config or LivemathConfig()
        self.symbols = SymbolTable()
        self.classifier = TokenClassifier(self.symbols)
        self._ir: Optional[LivemathIR] = None  # Current IR being processed
        self._warning_count = 0  # ISS-017: Track warnings separately from errors

    def get_warning_count(self) -> int:
        """Return the number of warnings encountered during evaluation."""
        return self._warning_count

    def reset_warning_count(self) -> None:
        """Reset the warning counter."""
        self._warning_count = 0

    def _format_warning(self, message: str) -> str:
        """Format a warning message with orange color for LaTeX display."""
        # Use \color{orange} for warnings (distinct from \color{red} for errors)
        escaped_msg = self._escape_latex_text(message)
        return f"\\color{{orange}}{{\\text{{{escaped_msg}}}}}"

    def evaluate_ir(self, ir: LivemathIR, calculations: List[Calculation]) -> LivemathIR:
        """
        Evaluate all calculations and update the IR.

        This is the main entry point for IR-based evaluation.

        Args:
            ir: The LivemathIR to update with results
            calculations: List of Calculation objects to process

        Returns:
            Updated LivemathIR with symbol values and block results
        """
        self._ir = ir

        # Pre-load symbols from IR into SymbolTable
        for name, entry in ir.symbols.items():
            if entry.value is not None:
                latex_name = entry.mapping.latex_original if entry.mapping else ""
                self.symbols.set(name, entry.value, latex_name=latex_name)

        # Process each calculation
        stats = {"definitions": 0, "evaluations": 0, "symbolic": 0, "errors": 0}

        for i, calc in enumerate(calculations):
            result_latex = self.evaluate(calc)

            # Update the corresponding block in IR
            if i < len(ir.blocks):
                ir.blocks[i].latex_output = result_latex
                if calc.operation == "ERROR" or "\\color{red}" in result_latex:
                    ir.blocks[i].error = calc.error_message or "Evaluation error"
                    stats["errors"] += 1

            # Update stats
            if calc.operation == ":=":
                stats["definitions"] += 1
            elif calc.operation == "==":
                stats["evaluations"] += 1
            elif calc.operation == ":=_==":
                stats["definitions"] += 1
                stats["evaluations"] += 1
            elif calc.operation == "=>":
                stats["symbolic"] += 1

        # Update IR with symbol values from SymbolTable
        for name in self.symbols.all_names():
            entry = self.symbols.get(name)
            if entry and name in ir.symbols:
                ir_entry = ir.symbols[name]

                # Update internal_name in mapping to v_{n} format
                if entry.internal_id:
                    ir_entry.mapping.internal_name = entry.internal_id

                # Try to extract numeric value
                try:
                    if hasattr(entry.value, 'evalf'):
                        numeric = float(entry.value.evalf())
                        ir_entry.value = numeric
                    elif isinstance(entry.value, (int, float)):
                        ir_entry.value = float(entry.value)
                except:
                    pass

                # Update unit information
                if entry.unit is not None:
                    ir_entry.unit = str(entry.unit)
                if entry.unit_latex:
                    ir_entry.unit_latex = entry.unit_latex

        ir.stats = stats
        self._ir = None
        return ir

    def _get_display_latex(self, internal_name: str, original_latex: str) -> str:
        """
        Get the display LaTeX for a symbol.

        Priority:
        1. IR mapping (if available)
        2. SymbolTable latex_name
        3. Original LaTeX (fallback)
        """
        # Check IR mapping
        if self._ir and internal_name in self._ir.symbols:
            return self._ir.symbols[internal_name].mapping.latex_display

        # Check SymbolTable for latex_name
        entry = self.symbols.get(internal_name)
        if entry and entry.latex_name:
            return entry.latex_name

        # Fallback to original
        return original_latex if original_latex else internal_name

    def evaluate(
        self,
        calculation: Calculation,
        config_overrides: Optional[Dict[str, Any]] = None,
        line: int = 0
    ) -> str:
        """
        Process a single calculation node and return the result string (LaTeX).

        Args:
            calculation: The calculation to evaluate
            config_overrides: Optional expression-level config overrides
                             (e.g., {"digits": 6, "format": "scientific"})
            line: Source line number for tracking

        Returns:
            LaTeX string with the calculation result
        """
        self._current_line = line  # Store for use in handlers
        # Apply expression-level config overrides for this calculation
        calc_config = self.config
        if config_overrides:
            calc_config = self.config.with_overrides(config_overrides)

        try:
            if calculation.operation == "ERROR":
                # Return error on new line, formatted for markdown readability
                err_msg = self._escape_latex_text(calculation.error_message or "Unknown error")
                return f"{calculation.latex}\n\\\\ \\color{{red}}{{\\text{{\n    Error: {err_msg}}}}}"
            elif calculation.operation == ":=":
                return self._handle_assignment(calculation)
            elif calculation.operation == "==":
                return self._handle_evaluation(calculation, config=calc_config)
            elif calculation.operation == ":=_==":
                 return self._handle_assignment_evaluation(calculation, config=calc_config)
            elif calculation.operation == "=>":
                return self._handle_symbolic(calculation)
            elif calculation.operation == "value":
                return self._handle_value_display(calculation, config=calc_config)
            elif calculation.operation == "===":
                return self._handle_unit_definition(calculation)
            else:
                return ""
        except Exception as e:
            # Return error on new line, formatted for markdown readability
            err_msg = self._escape_latex_text(str(e))
            return f"{calculation.latex}\n\\\\ \\color{{red}}{{\\text{{\n    Error: {err_msg}}}}}"

    def _normalize_symbol_name(self, name: str) -> str:
        """
        Normalize a LaTeX symbol name to internal dict key.

        Simple normalization for symbol table keys:
        - Strip whitespace
        - Replace Greek LaTeX commands with names
        - Replace commas and braces for consistency

        Examples:
            "\\Delta_h"   -> "Delta_h"
            "T_{h,in}"    -> "T_h_in"
            "P_{LED,out}" -> "P_LED_out"
        """
        if not name:
            return name

        result = name.strip()

        # Replace Greek letter commands with names
        for latex_cmd, greek_name in GREEK_LETTERS.items():
            result = result.replace(latex_cmd, greek_name)

        # Normalize subscript content
        result = result.replace(',', '_')
        result = result.replace('{', '')
        result = result.replace('}', '')

        # Remove remaining backslashes
        result = result.replace('\\', '')

        # Clean up multiple underscores
        while '__' in result:
            result = result.replace('__', '_')

        return result

    def _check_unit_name_conflict(self, normalized_name: str, display_name: str) -> None:
        """
        Check if a variable name conflicts with a known unit.

        This prevents ambiguity where 'g' could mean both 'gram' (unit) and
        'gravitational acceleration' (variable).

        Uses Pint's comprehensive unit database for detection, which covers
        thousands of units including prefixes and aliases.

        Args:
            normalized_name: Internal normalized name (e.g., 'g', 'L_pipe')
            display_name: LaTeX display name (e.g., 'g', 'L_{pipe}')

        Raises:
            EvaluationError: If the name conflicts with a known unit
        """
        from .pint_backend import check_variable_name_conflict

        # Check the full name first (e.g., 'L_pipe', 'g_acc')
        # These are OK because they have subscripts that distinguish them
        # Only check the BASE name (before underscore) for conflicts

        # Extract base name (part before underscore)
        if '_' in normalized_name:
            # Has subscript - this is explicitly disambiguated, allow it
            # e.g., 'g_{acc}' is fine even though 'g' is a unit
            return

        if '{' in display_name and '_' in display_name:
            # LaTeX subscript like 'L_{pipe}' - also disambiguated
            return

        # Use Pint backend for comprehensive unit detection
        error = check_variable_name_conflict(normalized_name)
        if error is not None:
            # Convert the error message to an exception
            raise EvaluationError(error)

    def _get_unit_description(self, unit_name: str) -> str:
        """Get a human-readable description of a unit."""
        descriptions = {
            # Mass
            'kg': 'kilogram', 'g': 'gram', 'mg': 'milligram',
            # Length
            'm': 'meter', 'cm': 'centimeter', 'mm': 'millimeter', 'km': 'kilometer',
            # Time
            's': 'second', 'h': 'hour', 'min': 'minute',
            # Volume
            'L': 'liter', 'l': 'liter', 'mL': 'milliliter',
            # Power/Energy
            'W': 'watt', 'kW': 'kilowatt', 'J': 'joule',
            # Pressure
            'Pa': 'pascal', 'bar': 'bar', 'kPa': 'kilopascal',
            # Electrical
            'V': 'volt', 'A': 'ampere',
            # Temperature
            'K': 'kelvin',
            # Force
            'N': 'newton',
            # Frequency
            'Hz': 'hertz',
        }
        return descriptions.get(unit_name, 'unit')

    def _escape_latex_text(self, text: str) -> str:
        """Escape special LaTeX characters in text."""
        # Special chars: \ { } $ & # ^ _ % ~
        # We perform simple replacements.
        # Note: Backslash must be first.
        replacements = {
            '\\': r'\textbackslash{}',
            '{': r'\{',
            '}': r'\}',
            '$': r'\$',
            '&': r'\&',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '%': r'\%',
            '~': r'\textasciitilde{}',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    # =========================================================================
    # v3.0 Classification Methods
    # =========================================================================

    def _is_value_definition(self, rhs: str) -> bool:
        r"""
        Check if RHS is a direct value (number with optional unit).

        A value definition is one where the RHS is just a number,
        possibly followed by a unit. No other symbol references.

        Examples:
            "50"           -> True (plain number)
            "50\ m³/h"     -> True (number with unit)
            "3.14159"      -> True (decimal)
            "1.5e-3"       -> True (scientific notation)
            "a + b"        -> False (formula with symbol references)
            "v_1 * 2"      -> False (formula)
            "\\pi"         -> False (mathematical constant, treat as formula)

        Args:
            rhs: The right-hand side of the definition

        Returns:
            True if this is a value definition, False if it's a formula
        """
        import re

        # Strip LaTeX whitespace and leading/trailing whitespace
        rhs_clean = rhs.strip()
        rhs_clean = re.sub(r'\\[,;:\s]+', ' ', rhs_clean)  # LaTeX spacing
        rhs_clean = rhs_clean.strip()

        # Check for number patterns
        # Matches: 50, 50.0, .5, 3.14159, 1.5e-3, 1E10, -5.2, +3.0
        number_pattern = r'^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$'

        # Check if it's a pure number
        if re.match(number_pattern, rhs_clean):
            return True

        # Check for number followed by unit
        # Split on first non-numeric character after the number
        value_unit_pattern = r'^([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*(.*)$'
        match = re.match(value_unit_pattern, rhs_clean)
        if match:
            number_part = match.group(1)
            unit_part = match.group(2).strip()

            # If there's a unit part, check if it looks like a unit (not a variable)
            if unit_part:
                # Units are typically short (1-5 chars) or have / or * or ^
                # Examples: m, kg, m/s, m²/h, €/kWh
                # Not a unit: x + y, v_1 * 2
                if '=' in unit_part or '+' in unit_part or '-' in unit_part:
                    # Has operators suggesting formula
                    return False

                # Check if unit part contains variable references
                # Variables in LaTeX: single letters, letters with subscripts
                variable_pattern = r'[a-zA-Z](?:_\{[^}]+\}|_[a-zA-Z0-9])?(?:\s*[+\-*/]\s*)'
                if re.search(variable_pattern, unit_part):
                    return False

                # Looks like a unit (or at least not obviously a formula)
                return True

        # Check for common formula patterns
        # Variables: single letters or letters with subscripts
        # Operators: + - * / ^
        # If RHS contains any symbol reference, it's a formula
        known_symbols = set(self.symbols.all_names())
        latex_mappings = self.symbols.get_all_latex_to_internal()

        # Check each token in RHS
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\{[^}]+\}', rhs_clean)
        for token in tokens:
            normalized = self._normalize_symbol_name(token)
            if normalized in known_symbols:
                return False
            if token in latex_mappings:
                return False

        # If no variables found and it's not purely a number, be conservative
        # and treat it as a formula (e.g., \pi, \sqrt{2})
        if not re.match(number_pattern, rhs_clean.split()[0] if rhs_clean else ''):
            return False

        return True

    def _find_dependencies(self, rhs: str, exclude_params: Optional[List[str]] = None) -> List[str]:
        """
        Find all symbol references in an expression.

        Searches for references to previously defined symbols and returns
        their clean IDs.

        Args:
            rhs: The expression to search
            exclude_params: Parameter names to exclude (for function definitions)

        Returns:
            List of clean IDs that this expression depends on
        """
        import re

        exclude = set(exclude_params or [])
        dependencies = []
        seen = set()

        # Get all known symbols
        latex_to_internal = self.symbols.get_all_latex_to_internal()

        # Find all potential symbol references in the expression
        # Look for: single letters, letters with subscripts, Greek letters
        potential_refs = re.findall(
            r'\\?[a-zA-Z]+(?:_\{[^}]+\}|_[a-zA-Z0-9]+)?',
            rhs
        )

        for ref in potential_refs:
            # Skip if it's in the exclude list (function parameters)
            normalized = self._normalize_symbol_name(ref)
            if normalized in exclude:
                continue

            # Check if this matches a known symbol
            internal_id = latex_to_internal.get(ref)
            if internal_id and internal_id not in seen:
                dependencies.append(internal_id)
                seen.add(internal_id)
            elif normalized in self.symbols.all_names():
                # Fallback: check normalized name
                sym = self.symbols.get(normalized)
                if sym and sym.internal_id and sym.internal_id not in seen:
                    dependencies.append(sym.internal_id)
                    seen.add(sym.internal_id)

        return dependencies

    def _convert_expression_to_clean_ids(self, rhs: str, exclude_params: Optional[List[str]] = None) -> str:
        """
        Convert a LaTeX expression to use clean IDs.

        Replaces all symbol references with their clean IDs (v1, f1, etc.)
        for storage in the IR.

        Args:
            rhs: The expression to convert
            exclude_params: Parameter names to keep as-is (e.g., x, y)

        Returns:
            Expression with clean IDs
        """
        import re

        exclude = set(exclude_params or [])
        result = rhs

        # Get all known symbols
        latex_to_internal = self.symbols.get_all_latex_to_internal()

        # Sort by length (longest first) to avoid partial replacements
        sorted_mappings = sorted(latex_to_internal.items(), key=lambda x: -len(x[0]))

        for latex_name, internal_id in sorted_mappings:
            normalized = self._normalize_symbol_name(latex_name)
            if normalized not in exclude:
                # Replace in the expression
                # Use word boundaries where possible
                pattern = re.escape(latex_name)
                result = re.sub(pattern, internal_id, result)

        return result

    def _handle_assignment(self, calc: Calculation) -> str:
        content = calc.latex
        rhs_raw = content

        if ":=" in content:
            lhs_part, rhs_part = content.split(":=", 1)
            lhs = lhs_part.strip()
            # If '==' is present (shouldn't be in this handler usually, but safety check)
            rhs_raw = rhs_part.split("==")[0].strip() if "==" in rhs_part else rhs_part.strip()
        else:
             lhs = None # Should not happen

        # Execute logic (setting symbols)
        # Keep original target for display, normalize for storage
        original_target = calc.target
        # NORMALIZE target name: convert LaTeX Greek letters to plain text
        # e.g., \Delta_h -> Delta_h, \theta_1 -> theta_1
        target = self._normalize_symbol_name(calc.target)
        import re
        from .pint_backend import (
            sympy_strip_unit_from_value as strip_unit_from_value,
            get_sympy_unit_registry as get_unit_registry,
        )

        # CHECK: Prevent variable names that conflict with known unit names
        # This avoids ambiguity like 'g' meaning both 'gram' and 'gravity'
        # We check if the FULL variable name (including subscript) would be recognized as a unit
        self._check_unit_name_conflict(target, original_target)

        func_match = re.match(r'^\s*([a-zA-Z_]\w*)\s*\(\s*([a-zA-Z_]\w*)\s*\)\s*$', target) if target else None

        if func_match:
            # v3.0: Function definitions are stored as formulas, not sympy.Lambda
            # The formula will be evaluated by substituting the parameter value when called
            func_name = func_match.group(1)
            arg_name = func_match.group(2)

            # v3.0: Track function as formula with parameter (only in clean ID mode)
            dependencies = []
            formula_expr = ""
            if getattr(self.symbols, '_use_clean_ids', False):
                dependencies = self._find_dependencies(rhs_raw, exclude_params=[arg_name])
                formula_expr = self._convert_expression_to_clean_ids(rhs_raw, exclude_params=[arg_name])

            # Extract just the function name from original_target for latex_name
            func_latex_match = re.match(r'^([^(]+)\s*\(', original_target)
            func_latex_name = func_latex_match.group(1).strip() if func_latex_match else original_target

            self.symbols.set(
                func_name,
                value=None,  # v3.0: No sympy.Lambda, use formula_expression instead
                raw_latex=rhs_raw,
                latex_name=func_latex_name,
                valid=True,
                line=getattr(self, '_current_line', 0),
                # v3.0 formula tracking
                is_formula=True,
                formula_expression=formula_expr if formula_expr else rhs_raw,
                depends_on=dependencies,
                parameters=[arg_name],
                parameter_latex=[arg_name],
            )

            # Use original target for display (preserves \Delta etc.)
            # IMPORTANT: Keep original RHS - don't normalize/re-evaluate definitions
            assignment_latex = f"{original_target} := {rhs_raw}"

        elif target:
            # v3.0: Use Pint for all calculations - no sympy fallback
            from .pint_backend import format_pint_unit

            # Compute the expression using Pint
            pint_result = self._compute_with_pint(rhs_raw)

            # Extract magnitude and unit from Pint result
            original_value = float(pint_result.magnitude)
            result_unit_str = format_pint_unit(pint_result.units)
            result_unit_latex = result_unit_str if result_unit_str != 'dimensionless' else ""

            # Convert to SI base units
            base_result = pint_result.to_base_units()
            si_value = float(base_result.magnitude)
            si_unit_str = format_pint_unit(base_result.units)
            # Create sympy unit placeholder for storage (temporary - will be removed in later phase)
            si_unit = si_unit_str if si_unit_str != 'dimensionless' else None
            valid = True  # Pint handles all conversions

            # v3.0: Classify and track dependencies (only in clean ID mode)
            is_formula_flag = False
            dependencies = []
            formula_expression = ""
            if getattr(self.symbols, '_use_clean_ids', False):
                is_value = self._is_value_definition(rhs_raw)
                is_formula_flag = not is_value
                if is_formula_flag:
                    dependencies = self._find_dependencies(rhs_raw)
                    formula_expression = self._convert_expression_to_clean_ids(rhs_raw)

            # Store with normalized name, including both original and SI values
            normalized_target = self._normalize_symbol_name(target)
            self.symbols.set(
                normalized_target,
                value=si_value,
                unit=si_unit,
                raw_latex=rhs_raw,
                latex_name=original_target,
                original_value=original_value,
                original_unit=result_unit_latex or None,
                valid=valid,
                line=getattr(self, '_current_line', 0),
                # v3.0 formula tracking (only populated in clean ID mode)
                is_formula=is_formula_flag,
                formula_expression=formula_expression,
                depends_on=dependencies,
            )

            # IMPORTANT: Keep original RHS - don't normalize/re-evaluate definitions
            # User explicitly requested: "Als het een definitie is, moet je gewoon laten staan"
            assignment_latex = f"{original_target} := {rhs_raw}"

        else:
            return content

        return assignment_latex

    def _handle_evaluation(self, calc: Calculation, config: Optional[LivemathConfig] = None) -> str:
        """Handle evaluation: $expr ==$"""
        cfg = config or self.config
        content = calc.latex
        lhs_part, result_part = content.split("==", 1)
        lhs = lhs_part.strip()

        # ISS-024 FIX: Use Pint for evaluation to ensure proper unit cancellation
        # ISS-037 FIX: Don't fall back to SymPy for dimensionless results - Pint handles them correctly
        # v3.0: No fallback to SymPy - custom parser handles everything
        pint_result = self._compute_with_pint(lhs)
        result_latex = self._format_pint_result(pint_result, calc.unit_comment, cfg)

        # Format LHS too? "x * y" -> "x \cdot y"
        # The user said "input mee formatten". LHS of evaluation is input.
        lhs_normalized = self._normalize_latex(lhs)

        return f"{lhs_normalized} == {result_latex}"

    def _format_pint_result(self, pint_result: 'pint.Quantity', unit_hint: Optional[str], config: LivemathConfig) -> str:
        """
        Format a Pint Quantity result to LaTeX.

        Args:
            pint_result: The Pint Quantity to format
            unit_hint: Optional unit hint from comment (e.g., "MWh")
            config: Configuration for formatting

        Returns:
            LaTeX formatted string
        """
        import pint
        from .pint_backend import clean_latex_unit

        ureg = get_pint_registry()

        # Apply unit conversion if specified
        if unit_hint:
            target_unit = clean_latex_unit(unit_hint)
            target_unit = target_unit.replace('€', 'EUR').replace('$', 'USD')
            try:
                pint_result = pint_result.to(target_unit)
            except pint.DimensionalityError as e:
                # Increment warning counter and show warning
                self._warning_count += 1
                si_value = self._format_pint_quantity_latex(pint_result.to_base_units(), config)
                warning_msg = f"Warning: Cannot convert to '{unit_hint}' - dimensions incompatible"
                return f"{si_value}\n\\\\ {self._format_warning(warning_msg)}"
            except Exception:
                pass  # Keep original units if conversion fails silently

        return self._format_pint_quantity_latex(pint_result, config)

    def _format_pint_quantity_latex(self, qty: 'pint.Quantity', config: LivemathConfig) -> str:
        """
        Format a Pint Quantity as LaTeX.

        Args:
            qty: Pint Quantity to format
            config: Configuration for formatting

        Returns:
            LaTeX string like "1\\,234.5\\ \\text{MWh}"
        """
        import pint

        # Get magnitude and unit
        magnitude = qty.magnitude
        unit = qty.units

        # Format magnitude with config settings
        digits = config.digits if config else 4

        # Check for very small numbers that should use scientific notation
        if abs(magnitude) < 0.001 and magnitude != 0:
            # Use scientific notation
            formatted_value = f"{magnitude:.{digits}e}"
        elif abs(magnitude) >= 10000:
            # Large numbers - use thousand separators
            formatted_value = f"{magnitude:,.{digits}f}"
            # Convert to LaTeX thousand separator
            formatted_value = formatted_value.replace(',', '\\,')
        else:
            # Normal numbers
            formatted_value = f"{magnitude:.{digits}f}"

        # Strip trailing zeros if they're just .0000
        if '.' in formatted_value:
            formatted_value = formatted_value.rstrip('0').rstrip('.')

        # Format unit as LaTeX
        unit_str = str(unit)
        if unit_str == 'dimensionless' or unit == qty._REGISTRY.dimensionless:
            return formatted_value
        else:
            # Convert Pint unit to LaTeX using format_unit_latex
            unit_latex = format_unit_latex(unit)
            return f"{formatted_value}\\ \\text{{{unit_latex}}}"

    def _pint_unit_to_latex(self, unit_str: str) -> str:
        """
        Convert a Pint unit string to LaTeX format.

        Args:
            unit_str: Pint unit string like "megawatt_hour"

        Returns:
            LaTeX like "\\text{MWh}"
        """
        # Common unit mappings
        unit_map = {
            'kilogram': 'kg',
            'gram': 'g',
            'milligram': 'mg',
            'meter': 'm',
            'kilometer': 'km',
            'centimeter': 'cm',
            'millimeter': 'mm',
            'second': 's',
            'hour': 'h',
            'minute': 'min',
            'day': 'd',
            'year': 'yr',
            'watt': 'W',
            'kilowatt': 'kW',
            'megawatt': 'MW',
            'joule': 'J',
            'kilojoule': 'kJ',
            'megajoule': 'MJ',
            'kilowatt_hour': 'kWh',
            'megawatt_hour': 'MWh',
            'liter': 'L',
            'milliliter': 'mL',
            'mole': 'mol',
            'euro': '€',
            'EUR': '€',
            'kelvin': 'K',
            'ampere': 'A',
            'volt': 'V',
            'pascal': 'Pa',
            'bar': 'bar',
        }

        # Check for compound units with / or *
        if '/' in unit_str or '*' in unit_str or '**' in unit_str:
            # Parse compound unit
            result = unit_str
            for pint_name, latex_name in sorted(unit_map.items(), key=lambda x: len(x[0]), reverse=True):
                result = result.replace(pint_name, latex_name)
            # Convert ** to ^
            result = result.replace('**', '^')
            # Wrap in \text{} for safety
            return f"\\text{{{result}}}"

        # Simple unit
        latex = unit_map.get(unit_str, unit_str)
        return f"\\text{{{latex}}}"

    def _handle_assignment_evaluation(self, calc: Calculation, config: Optional[LivemathConfig] = None) -> str:
        """Handle combined assignment and evaluation: $var := expr ==$"""
        cfg = config or self.config
        content = calc.latex
        part1, part2 = content.split(":=", 1)
        lhs = part1.strip()  # Original LaTeX form for display
        rhs_part, result_part = part2.split("==", 1)
        rhs = rhs_part.strip()

        from .pint_backend import format_pint_unit

        # v3.0: Use Pint for all calculations - no sympy fallback
        pint_result = self._compute_with_pint(rhs)

        # Extract magnitude and unit from Pint result
        original_value = float(pint_result.magnitude)
        original_unit_str = format_pint_unit(pint_result.units)
        original_unit = original_unit_str if original_unit_str != 'dimensionless' else None

        # Convert to SI base units
        base_result = pint_result.to_base_units()
        si_value = float(base_result.magnitude)
        si_unit_str = format_pint_unit(base_result.units)
        si_unit = si_unit_str if si_unit_str != 'dimensionless' else None

        # Store with normalized name (e.g., \Delta T_h -> Delta_T_h)
        normalized_lhs = self._normalize_symbol_name(lhs)

        self.symbols.set(
            normalized_lhs,
            value=si_value,
            unit=si_unit,
            raw_latex=rhs,
            latex_name=lhs,
            original_value=original_value,
            original_unit=original_unit,
            valid=True,
            line=getattr(self, '_current_line', 0)
        )

        # Format result using Pint
        result_latex = self._format_pint_result(pint_result, calc.unit_comment, cfg)

        # IMPORTANT: Keep original RHS LaTeX for definitions
        # Don't re-format it - user's notation should be preserved
        # Only the result (after ==) gets formatted

        return f"{lhs} := {rhs} == {result_latex}"

    def _check_undefined_symbols(self, value: Any, original_latex: str) -> None:
        """Check if the computed value contains undefined symbols."""
        import sympy
        import re
        from sympy.physics import units as u

        if not hasattr(value, 'free_symbols'):
            return  # It's a pure number, no symbols

        # Get symbols that are still in the expression (weren't substituted)
        remaining_symbols = value.free_symbols

        # Filter out known SI units (they're expected to remain)
        undefined = []
        for sym in remaining_symbols:
            sym_name = str(sym)
            # Clean \text{} wrapper
            clean_name = re.sub(r'^\\(text|mathrm)\{([^}]+)\}$', r'\2', sym_name).strip()

            # Check if it's a known unit using Pint backend (comprehensive check)
            from .pint_backend import is_unit_token
            if is_unit_token(clean_name):
                continue
            # Also check SymPy built-in units as fallback
            if hasattr(u, clean_name):
                unit_val = getattr(u, clean_name)
                if isinstance(unit_val, (u.Unit, u.Quantity)):
                    continue

            # It's not a unit, so it's undefined
            undefined.append(clean_name)

        if undefined:
            # Check for implicit multiplication pattern (ISS-018, ISS-022)
            impl_info = self.classifier.detect_implicit_multiplication(
                original_latex, remaining_symbols
            )

            if impl_info:
                # Generate specialized error message mentioning the multi-letter identifier
                msg = f"Undefined variable '{impl_info.intended_symbol}'."
                msg += f" Note: '{impl_info.intended_symbol}' was parsed as implicit multiplication ({impl_info.split_as})."
                msg += f" Define '${impl_info.intended_symbol} := ...$' before use, or use a structured name like '{impl_info.intended_symbol}_{{...}}'."

                if impl_info.unit_conflicts:
                    conflict_details = []
                    for letter in impl_info.unit_conflicts:
                        unit_name = self.classifier.has_unit_conflict(letter)
                        if unit_name:
                            conflict_details.append(f"'{letter}' is also a unit ({unit_name})")
                    if conflict_details:
                        msg += f" ({'; '.join(conflict_details)})"

                raise EvaluationError(msg)

            # Fallback to generic error message
            if len(undefined) == 1:
                var = undefined[0]
                raise EvaluationError(f"Undefined variable '{var}'. Define it before use.")
            else:
                vars_list = ', '.join(f"'{v}'" for v in sorted(undefined))
                raise EvaluationError(f"Undefined variables: {vars_list}. Define them before use.")

    def _check_dimensional_compatibility(self, value: Any, original_latex: str) -> None:
        """
        Check if an Add/Sub expression has dimensionally compatible terms.

        ISSUE-006: Detect incompatible unit operations like kg + m.

        Args:
            value: The computed SymPy expression
            original_latex: Original LaTeX for error messages

        Raises:
            EvaluationError: If incompatible units are being added/subtracted
        """
        from sympy import Add
        from sympy.physics.units import Quantity
        from .pint_backend import get_sympy_unit_dimensionality, are_dimensions_compatible

        if not hasattr(value, 'args'):
            return  # Not an expression with arguments

        # Recursively check all Add expressions in the tree
        self._check_add_dimensional_compatibility(value)

    def _check_add_dimensional_compatibility(self, expr: Any) -> None:
        """
        Recursively check Add expressions for dimensional compatibility.

        Args:
            expr: A SymPy expression to check

        Raises:
            EvaluationError: If incompatible units are being added/subtracted
        """
        from sympy import Add
        from sympy.physics.units import Quantity
        from .pint_backend import get_sympy_unit_dimensionality, are_dimensions_compatible

        if not hasattr(expr, 'args'):
            return

        # Check if this is an Add expression
        if isinstance(expr, Add):
            # Get dimensionality of each term
            term_dims = []
            term_units = []

            for term in expr.args:
                dim = get_sympy_unit_dimensionality(term)
                term_dims.append(dim)

                # Get the unit part of the term for error message
                unit_str = "(dimensionless)"
                if hasattr(term, 'as_coeff_Mul'):
                    try:
                        coeff, unit_part = term.as_coeff_Mul()
                        if unit_part != 1:
                            # Use the full unit expression
                            unit_str = str(unit_part)
                    except Exception:
                        pass
                # Fallback: if as_coeff_Mul didn't work, try atoms
                if unit_str == "(dimensionless)" and hasattr(term, 'atoms'):
                    quantities = term.atoms(Quantity)
                    if quantities:
                        # Sort for deterministic output
                        unit_str = str(sorted(quantities, key=str)[0])
                term_units.append(unit_str)

            # Check if all terms have compatible dimensions
            if len(term_dims) >= 2:
                first_dim = term_dims[0]
                for i, dim in enumerate(term_dims[1:], 1):
                    if not are_dimensions_compatible(first_dim, dim):
                        # Found incompatible dimensions
                        unit1 = term_units[0]
                        unit2 = term_units[i]
                        raise EvaluationError(
                            f"Cannot add/subtract incompatible units: {unit1} and {unit2}. "
                            f"Dimensions must match for addition/subtraction."
                        )

        # Recursively check sub-expressions
        for arg in expr.args:
            self._check_add_dimensional_compatibility(arg)

    def _extract_unit_from_value(self, value: Any) -> Tuple[Optional[Any], str]:
        """
        Extract the unit from a computed value (e.g., 208.5*euro -> (euro, "€")).

        Returns:
            Tuple of (sympy_unit or None, unit_latex_string)
        """
        from sympy.physics.units import Quantity
        from .pint_backend import format_unit_latex

        if not hasattr(value, 'as_coeff_Mul'):
            return None, ""

        try:
            coeff, rest = value.as_coeff_Mul()

            # Check if rest contains unit Quantities
            if hasattr(rest, 'atoms'):
                quantities = rest.atoms(Quantity)
                if quantities:
                    # This has units - rest is the unit expression
                    unit_latex = format_unit_latex(rest)
                    return rest, unit_latex
        except:
            pass

        return None, ""

    def _convert_to_si(self, value: Any, unit: Any) -> Tuple[Any, Any, bool]:
        """
        Convert a value with its unit to SI base units.

        Args:
            value: The numeric value (without unit)
            unit: The SymPy unit expression

        Returns:
            Tuple of (si_value, si_unit, valid)
            - si_value: Numeric value in SI
            - si_unit: SI unit expression (or None if dimensionless)
            - valid: True if conversion was successful and round-trip validated
        """
        from sympy.physics.units import convert_to
        import sympy.physics.units as u

        if unit is None:
            # No unit - dimensionless value
            return value, None, True

        try:
            # Combine value and unit for conversion
            full_value = value * unit

            # Convert to SI base units
            si_base = [u.kg, u.meter, u.second, u.ampere, u.kelvin, u.mole, u.candela]
            converted = convert_to(full_value, si_base)

            # Extract coefficient and unit part
            if hasattr(converted, 'as_coeff_Mul'):
                si_coeff, si_unit_part = converted.as_coeff_Mul()

                # Evaluate coefficient to float
                if hasattr(si_coeff, 'evalf'):
                    si_coeff = si_coeff.evalf()
                si_value = float(si_coeff) if si_coeff != 1 else float(value)

                # Unit part (may be 1 for dimensionless)
                si_unit = si_unit_part if si_unit_part != 1 else None

                # Round-trip validation: convert back and check
                valid = self._validate_round_trip(value, unit, si_value, si_unit)

                return si_value, si_unit, valid
            else:
                # No clear separation - use original
                return value, unit, True

        except Exception:
            # Conversion failed - keep original
            return value, unit, False

    def _validate_round_trip(
        self, orig_value: Any, orig_unit: Any, si_value: float, si_unit: Any
    ) -> bool:
        """
        Validate that SI conversion is dimensionally correct.

        Returns True if the SI conversion preserves the physical quantity.

        Note: We don't do numeric round-trip because compound units like
        meter/1000 (from 'mm') don't convert back properly in SymPy.
        Instead, we verify that the product of original value*unit equals
        the SI value*unit (dimensionally).
        """
        from sympy.physics.units import convert_to
        import sympy.physics.units as u

        try:
            if si_unit is None or orig_unit is None:
                return True

            # Verify dimensional consistency: both should convert to same SI value
            si_base = [u.kg, u.meter, u.second, u.ampere, u.kelvin, u.mole, u.candela]

            # Original in SI
            orig_full = orig_value * orig_unit
            orig_si = convert_to(orig_full, si_base)

            # Our computed SI value
            computed_si = si_value * si_unit
            computed_si_converted = convert_to(computed_si, si_base)

            # Extract numeric values
            def get_numeric(expr):
                if hasattr(expr, 'as_coeff_Mul'):
                    coeff, _ = expr.as_coeff_Mul()
                    if hasattr(coeff, 'evalf'):
                        return float(coeff.evalf())
                    return float(coeff)
                return float(expr)

            orig_num = get_numeric(orig_si)
            computed_num = get_numeric(computed_si_converted)

            # Check relative error
            if abs(orig_num) > 1e-10:
                rel_error = abs(computed_num - orig_num) / abs(orig_num)
                return rel_error < 0.001  # 0.1% tolerance
            else:
                return abs(computed_num - orig_num) < 1e-10

        except Exception:
            # If validation fails, assume conversion is OK
            return True

    def _normalize_unit_string(self, unit_str: str) -> str:
        """
        Normalize Unicode characters in unit strings to LaTeX notation.

        Converts:
        - Unicode superscripts: ² → ^2, ³ → ^3
        - Unicode subscripts: ₀ → _0, ₁ → _1
        - Unicode middle dot: · → * (multiplication)
        - Common unit symbols: µ → micro (for parsing)
        """
        # Unicode superscripts to LaTeX
        superscript_map = {
            '⁰': '^0', '¹': '^1', '²': '^2', '³': '^3', '⁴': '^4',
            '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9',
            '⁻': '^-',
        }
        # Unicode subscripts to LaTeX
        subscript_map = {
            '₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4',
            '₅': '_5', '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9',
        }
        # Unicode operators
        operator_map = {
            '·': '*',  # Middle dot to multiplication
            '×': '*',  # Multiplication sign to asterisk
        }

        for unicode_char, latex in superscript_map.items():
            unit_str = unit_str.replace(unicode_char, latex)
        for unicode_char, latex in subscript_map.items():
            unit_str = unit_str.replace(unicode_char, latex)
        for unicode_char, replacement in operator_map.items():
            unit_str = unit_str.replace(unicode_char, replacement)

        return unit_str

    def _parse_unit_with_prefix(self, unit_str: str):
        """
        Parse a unit string that may include SI prefixes (kW, MHz, mm, etc.)

        Handles common SI prefixes: k(ilo), M(ega), G(iga), m(illi), µ/u(micro), n(ano)
        Also handles LaTeX notation like \\text{kW}
        """
        import sympy.physics.units as u
        from sympy.physics.units.prefixes import kilo, mega, giga, milli, micro, nano, centi

        # Strip LaTeX wrappers: \text{kW} -> kW
        if unit_str.startswith('\\text{') and unit_str.endswith('}'):
            unit_str = unit_str[6:-1]  # Remove \text{ and }

        # SI prefix mapping
        prefix_map = {
            'k': kilo,    # kilo (10³)
            'M': mega,    # mega (10⁶) - capital M
            'G': giga,    # giga (10⁹)
            'c': centi,   # centi (10⁻²)
            # Note: 'm' is ambiguous (meter vs milli) - handle specially
            'µ': micro,   # micro (10⁻⁶)
            'u': micro,   # micro alternative
            'n': nano,    # nano (10⁻⁹)
        }

        # Common base units with their SymPy objects
        base_units = {
            'W': u.W, 'watt': u.W,
            'Hz': u.Hz, 'hertz': u.Hz,
            'N': u.N, 'newton': u.N,
            'J': u.J, 'joule': u.J,
            'Pa': u.Pa, 'pascal': u.Pa,
            'V': u.V, 'volt': u.V,
            'A': u.A, 'ampere': u.A,
            'F': u.F, 'farad': u.F,
            'Ω': u.ohm, 'ohm': u.ohm,
            'g': u.g, 'gram': u.g,
            # Note: 'm' (meter) handled separately
        }

        # Check for prefixed units (e.g., kW, MHz, mm)
        for prefix_char, prefix_val in prefix_map.items():
            if unit_str.startswith(prefix_char) and len(unit_str) > 1:
                base_part = unit_str[1:]
                if base_part in base_units:
                    return prefix_val * base_units[base_part]

        # Special case: mm (millimeter) - 'm' prefix with 'm' base
        if unit_str == 'mm':
            return milli * u.m

        # No prefix found, try direct lookup
        if unit_str in base_units:
            return base_units[unit_str]

        # Fallback to _compute for complex expressions
        return None

    # NOTE: _apply_conversion() function removed in v3.0 (Phase 28)
    # Unit conversion is now handled by Pint in _format_pint_result()

    def _extract_unit_string(self, value: Any) -> str:
        """
        Extract a human-readable unit string from a sympy value.
        Returns the unit part of a value with units, or 'dimensionless' if none.
        """
        from sympy.physics.units import Quantity
        from sympy.physics.units import convert_to, kg, m, s, A, K, mol, cd
        import sympy

        if not hasattr(value, 'atoms'):
            return 'dimensionless'

        # Get unit atoms from the value
        quantities = value.atoms(Quantity)
        if not quantities:
            return 'dimensionless'

        # Convert to SI base units and extract the unit part
        try:
            base_units = [kg, m, s, A, K, mol, cd]
            si_form = convert_to(value, base_units)
            # Get the unit part by dividing out the numeric coefficient
            if hasattr(si_form, 'as_coeff_Mul'):
                coeff, unit_part = si_form.as_coeff_Mul()
                if unit_part != 1:
                    # ISS-023 fix: Use regex to remove \text{} wrappers properly
                    return re.sub(r'\\text\{([^}]+)\}', r'\1', sympy.latex(unit_part))
        except:
            pass

        # Fallback: just list the quantities
        return ', '.join(str(q) for q in quantities)

    def _format_si_value(self, value: Any) -> str:
        """
        Format a value in SI base units for display in warning messages.
        Returns a string like '650.67 mol' or '42 kg*m/s**2'.
        """
        from sympy.physics.units import convert_to, kg, m, s, A, K, mol, cd
        import sympy

        try:
            base_units = [kg, m, s, A, K, mol, cd]
            si_form = convert_to(value, base_units)

            # Format with reasonable precision
            if hasattr(si_form, 'evalf'):
                si_form = si_form.evalf(6)

            # Convert to LaTeX-friendly string
            result = sympy.latex(si_form)
            # Clean up for display
            # ISS-023 fix: Use regex to remove \text{} wrappers properly (don't remove all })
            result = re.sub(r'\\text\{([^}]+)\}', r'\1', result.replace('\\cdot', '*'))
            return result
        except:
            # Fallback to string representation
            return str(value)

    def _handle_symbolic(self, calc: Calculation) -> str:
        """Handle $expr =>$

        v3.0: Symbolic operations (differentiation, etc.) are not supported
        in the Pint-based evaluator. This feature requires sympy which has
        been removed to fix stability issues (ISS-035, ISS-036, etc.).
        """
        content = calc.latex
        lhs = content.split("=>")[0].strip()

        raise EvaluationError(
            f"Symbolic operations (=>) are not supported in v3.0. "
            f"Expression: {lhs}"
        )

    def _handle_value_display(self, calc: Calculation, config: Optional[LivemathConfig] = None) -> str:
        """
        Handle value display: $ $ <!-- value:VAR [unit] :precision -->

        Returns just the numeric value (not the formula), optionally converted to
        the specified unit and formatted with the specified precision.

        The variable name and unit are in LaTeX notation, parsed using latex2sympy.

        Args:
            calc: The calculation containing value display info
            config: Config to use for formatting (defaults to self.config)
        """
        cfg = config or self.config
        var_name = calc.target.strip() if calc.target else calc.latex.strip()

        # Normalize the variable name (handle Greek letters, subscripts, etc.)
        normalized_name = self._normalize_symbol_name(var_name)

        # Look up the variable
        stored = self.symbols.get(normalized_name)
        if not stored:
            # Try with backslash for Greek letters
            stored = self.symbols.get('\\' + normalized_name)

        if not stored:
            raise EvaluationError(f"Undefined variable: {var_name}")

        value = stored.value
        # Get original value and unit for Pint-based conversion (ISSUE-001 fix)
        original_value = getattr(stored, 'original_value', None)
        original_unit = getattr(stored, 'original_unit', None)

        # Apply unit conversion if specified (unit is in LaTeX notation)
        if calc.unit_comment:
            # Use Pint-based conversion with original_value and original_unit
            # This ensures custom units (EUR, kWh, MWh) work correctly
            numeric_value = self._get_numeric_in_unit_latex(
                value, calc.unit_comment,
                from_unit=original_unit,
                original_value=original_value
            )
        else:
            numeric_value = self._extract_numeric_value(value)

        # Format the result using config
        result = self._format_numeric(numeric_value, calc.precision, config=cfg)

        return result

    def _handle_unit_definition(self, calc: Calculation) -> str:
        """
        Handle unit definition: $$ unit === expr $$

        Defines a custom unit using the === syntax:
        - Base unit:     € === €           (new unit)
        - Derived unit:  mbar === bar/1000 (scaled from existing)
        - Compound unit: kWh === kW * h    (product of units)
        - Alias:         dag === day       (rename existing)

        Args:
            calc: The calculation containing unit definition
                  calc.target = left side (unit name being defined)
                  calc.original_result = right side (definition expression)

        Returns:
            The original LaTeX (unit definitions don't produce output)
        """
        from .pint_backend import define_custom_unit_from_latex, is_pint_unit

        unit_name = calc.target.strip() if calc.target else ""
        definition = calc.original_result.strip() if calc.original_result else ""

        if not unit_name:
            raise EvaluationError("Unit definition requires a unit name on the left side of ===")

        # ISS-009 FIX: Check if unit already exists in Pint BEFORE we define it.
        # This must be done before define_custom_unit_from_latex which adds to Pint registry.
        if is_pint_unit(unit_name):
            raise EvaluationError(
                f"Cannot redefine existing unit '{unit_name}'. "
                f"Choose a different name for your custom unit."
            )

        # Build the full definition string for the unit registry
        full_definition = f"{unit_name} === {definition}"

        # Register in Pint backend for value: directive conversions (ISSUE-001 fix)
        define_custom_unit_from_latex(unit_name, definition)

        # Also register in SymPy registry for calculation purposes
        registry = get_unit_registry()
        unit_def = registry.define_unit(full_definition)

        if unit_def:
            # Unit was defined successfully
            # Return the original LaTeX unchanged (unit definitions are declarations)
            return calc.latex
        else:
            raise EvaluationError(f"Failed to define unit: {unit_name}")

    def _get_numeric_in_unit_latex(
        self,
        value: Any,
        unit_latex: str,
        from_unit: Optional[str] = None,
        original_value: Optional[float] = None
    ) -> float:
        """
        Convert a dimensioned value to a target unit (in LaTeX notation) and return the numeric part.

        Uses Pint backend for unit conversion, which supports custom units (EUR, kWh, etc.)
        and complex unit expressions (MWh, EUR/kWh, m³/h).

        Example: 50*meter**3/hour, "m³/h" → 50.0
        Example: 2859*watt, "kW" → 2.859
        Example: 5000*kWh, "MWh" → 5.0  (ISSUE-001 fix)

        Args:
            value: The SymPy expression (possibly with units, may be SI-converted)
            unit_latex: Target unit in LaTeX notation
            from_unit: Optional source unit string (from symbol's original_unit)
            original_value: Optional original numeric value (before SI conversion)
        """
        from .pint_backend import convert_value_to_unit

        # Try Pint-based conversion first (supports custom units like EUR, MWh, etc.)
        # Use original_value if available (before SI conversion) for accurate conversion
        if from_unit and original_value is not None:
            result = convert_value_to_unit(original_value, from_unit, unit_latex)
            if result is not None:
                return result

        # Extract numeric value from SymPy expression
        numeric_value = self._extract_numeric_value(value)

        # Fallback: try SymPy-based conversion for standard units
        from sympy.physics.units import convert_to
        from sympy.physics import units as u
        import sympy

        try:
            # Normalize Unicode characters (e.g., m³ → m^3)
            normalized_unit = self._normalize_unit_string(unit_latex)

            # First try to parse as prefixed unit (kW, MHz, mm, etc.)
            target_unit = self._parse_unit_with_prefix(normalized_unit)

            # If that didn't work, try parsing as expression
            if target_unit is None:
                target_unit = self._parse_unit_expression(normalized_unit)

            if target_unit is None:
                return numeric_value

            # First convert both value and target to SI base units
            base_units = [u.kg, u.meter, u.second, u.ampere, u.kelvin, u.mole, u.candela]

            try:
                value_si = convert_to(value, base_units)
                target_si = convert_to(target_unit, base_units)
            except:
                value_si = value
                target_si = target_unit

            # Calculate ratio: value / target_unit (should give dimensionless number)
            ratio = value_si / target_si

            # Simplify and evaluate
            ratio_simplified = sympy.simplify(ratio)
            if hasattr(ratio_simplified, 'evalf'):
                ratio_simplified = ratio_simplified.evalf()

            # Extract numeric value
            if hasattr(ratio_simplified, 'is_number') and ratio_simplified.is_number:
                return float(ratio_simplified)
            else:
                # If still has symbols, try as_coeff_Mul
                if hasattr(ratio_simplified, 'as_coeff_Mul'):
                    coeff, _ = ratio_simplified.as_coeff_Mul()
                    return float(coeff.evalf()) if hasattr(coeff, 'evalf') else float(coeff)
                return float(ratio_simplified)

        except Exception as e:
            # Fallback: return the extracted numeric without conversion
            return numeric_value

    def _get_numeric_in_unit(self, value: Any, target_unit_latex: str) -> float:
        """
        Convert a dimensioned value to a target unit and return just the numeric part.

        Example: 50*meter**3/hour → "m³/h" → 50.0
        Example: 2859*watt → "kW" → 2.859
        """
        from sympy.physics.units import convert_to
        from sympy.physics import units as u
        import sympy

        try:
            # Normalize Unicode characters (e.g., m³/s → m^3/s)
            normalized_unit = self._normalize_unit_string(target_unit_latex)

            # Parse the target unit - use _parse_unit_expression for proper unit parsing
            target_unit = self._parse_unit_expression(normalized_unit)

            if target_unit is None:
                # Fallback: just extract numeric from value without conversion
                return self._extract_numeric_value(value)

            # Calculate ratio: value / target_unit (should give dimensionless number)
            ratio = value / target_unit

            # Convert to SI base units to get pure number
            base_units = [u.kg, u.meter, u.second, u.ampere, u.kelvin, u.mole, u.candela]
            ratio_base = convert_to(ratio, base_units)

            # Simplify to remove any remaining unit symbols
            ratio_simplified = sympy.simplify(ratio_base)

            # Extract numeric value
            if hasattr(ratio_simplified, 'evalf'):
                result = float(ratio_simplified.evalf())
            else:
                result = float(ratio_simplified)

            return result
        except Exception as e:
            # Fallback: try to extract numeric without conversion
            return self._extract_numeric_value(value)

    def _parse_unit_expression(self, unit_str: str) -> Any:
        """
        Parse a unit string into SymPy unit expression.

        Handles: m/s, m³/h, kW, mm, etc.
        
        ISSUE-002: Uses pint_to_sympy_with_prefix() for dynamic conversion
        instead of hardcoded unit_map.
        """
        from .pint_backend import pint_to_sympy_with_prefix
        
        # Use Pint backend for dynamic unit conversion
        result = pint_to_sympy_with_prefix(unit_str)
        if result is not None:
            return result
        
        # Fallback: try prefixed units via SymPy directly
        prefixed = self._parse_unit_with_prefix(unit_str)
        if prefixed is not None:
            return prefixed
        
        return None

    def _parse_single_unit(self, unit_str: str, unit_map: dict = None) -> Any:
        """Parse a single unit with optional exponent like m^3 or m³.
        
        ISSUE-002: unit_map parameter is deprecated, uses pint_to_sympy_with_prefix().
        """
        from .pint_backend import pint_to_sympy_with_prefix
        
        # Handle exponents
        if '^' in unit_str:
            base, exp_str = unit_str.split('^')
            base = base.strip()
            exp = int(exp_str.strip())
            
            base_unit = pint_to_sympy_with_prefix(base)
            if base_unit is not None:
                return base_unit ** exp
        
        # Try direct conversion via Pint
        result = pint_to_sympy_with_prefix(unit_str)
        if result is not None:
            return result
        
        # Fallback: try prefixed units via SymPy directly
        prefixed = self._parse_unit_with_prefix(unit_str)
        if prefixed is not None:
            return prefixed

        return None

    def _extract_numeric_value(self, value: Any) -> float:
        """Extract the numeric value from a possibly dimensioned or symbolic expression.

        For pure numeric expressions (including those with log, exp, etc.),
        we evaluate numerically first.

        For dimensioned values (with units), we extract the coefficient.
        """
        import sympy
        from sympy.physics.units import Quantity

        # First try: evaluate the full expression numerically
        # This handles symbolic expressions like log(), exp(), etc. correctly
        try:
            result = value.evalf()
            if result.is_number:
                return float(result)
        except:
            pass

        # Second try: for dimensioned values, extract coefficient
        # Only use as_coeff_Mul if the "rest" contains units (Quantities)
        try:
            if hasattr(value, 'as_coeff_Mul'):
                coeff, rest = value.as_coeff_Mul()
                # Check if rest contains unit Quantities
                if hasattr(rest, 'atoms'):
                    quantities = rest.atoms(Quantity)
                    if quantities:
                        # This is a dimensioned value, extract coefficient
                        if coeff.is_number:
                            return float(coeff.evalf())
        except:
            pass

        # Fallback: try direct float conversion
        try:
            return float(value)
        except:
            return float(value.evalf())

    def _format_numeric(
        self,
        value: float,
        precision: Optional[int] = None,
        config: Optional[LivemathConfig] = None
    ) -> str:
        """
        Format a numeric value with the specified precision.

        Args:
            value: The numeric value to format
            precision: Override precision (from calculation, e.g. <!-- value:x :3 -->)
            config: Config to use (defaults to self.config)

        Returns:
            Formatted string representation
        """
        cfg = config or self.config
        digits = precision if precision is not None else cfg.digits

        # Check format type from config
        if cfg.format == "scientific":
            return self._format_scientific(value, digits)
        elif cfg.format == "engineering":
            return self._format_engineering(value, digits)
        elif cfg.format == "decimal":
            result = f"{value:.{digits}f}"
            # Strip trailing zeros unless explicitly requested
            if not cfg.trailing_zeros and '.' in result:
                result = result.rstrip('0').rstrip('.')
            # Add thousands separators
            return self._add_thousands_separator(result)
        else:  # "general" - auto-choose based on threshold
            # trailing_zeros=False means we should strip trailing zeros
            return self._format_general(value, digits, cfg.exponential_threshold,
                                        strip_trailing=not cfg.trailing_zeros)

    def _format_scientific(self, value: float, digits: int) -> str:
        """Format number in scientific notation (e.g., 1.234e5)."""
        if value == 0:
            return "0"
        return f"{value:.{digits-1}e}"

    def _format_engineering(self, value: float, digits: int) -> str:
        """Format number in engineering notation (exponent multiple of 3)."""
        if value == 0:
            return "0"

        from math import log10, floor

        # Get exponent as multiple of 3
        exp = floor(log10(abs(value)))
        eng_exp = (exp // 3) * 3

        # Adjust mantissa
        mantissa = value / (10 ** eng_exp)

        # Format mantissa with appropriate decimals
        decimals = max(0, digits - 1 - (exp - eng_exp))
        mantissa_str = f"{mantissa:.{decimals}f}"

        if eng_exp == 0:
            return mantissa_str
        else:
            return f"{mantissa_str}e{eng_exp}"

    def _format_general(self, value: float, digits: int, threshold: int, strip_trailing: bool = True) -> str:
        """
        Format number in general notation.

        Uses scientific notation when magnitude exceeds threshold.
        Strips trailing zeros by default: 40.00 → 40, 40.10 → 40.1
        """
        if value == 0:
            return "0"

        from math import log10, floor

        magnitude = floor(log10(abs(value)))

        # Switch to scientific notation if magnitude exceeds threshold
        if abs(magnitude) >= threshold:
            return self._format_scientific(value, digits)

        # Otherwise use significant figures format (strip trailing zeros)
        return self._format_significant(value, digits, strip_trailing=strip_trailing)

    def _format_significant(self, value: float, sig_figs: int, strip_trailing: bool = True) -> str:
        """Format a number with the specified number of significant figures.

        Args:
            value: The numeric value to format
            sig_figs: Number of significant figures
            strip_trailing: If True, remove trailing zeros (40.00 → 40)
        """
        if value == 0:
            return "0"

        from math import log10, floor

        # Calculate order of magnitude
        magnitude = floor(log10(abs(value)))

        # Round to significant figures
        rounded = round(value, sig_figs - 1 - magnitude)

        # Format appropriately - always use decimal format here
        # (scientific notation threshold is handled by _format_general)
        if magnitude >= sig_figs - 1:
            # Integer-like (no decimals needed)
            result = f"{rounded:.0f}"
        else:
            # Decimal format
            decimals = max(0, sig_figs - 1 - magnitude)
            result = f"{rounded:.{decimals}f}"

        # Strip trailing zeros if requested: 40.00 → 40, 40.10 → 40.1
        if strip_trailing and '.' in result:
            result = result.rstrip('0').rstrip('.')

        # Add thousands separators (thin space \, in LaTeX)
        result = self._add_thousands_separator(result)

        return result

    def _add_thousands_separator(self, number_str: str) -> str:
        """Add thin space (\\,) as thousands separator for readability.

        144000000 → 144\\,000\\,000
        1234.5678 → 1\\,234.5678
        """
        if '.' in number_str:
            integer_part, decimal_part = number_str.split('.')
        else:
            integer_part = number_str
            decimal_part = None

        # Handle negative numbers
        negative = integer_part.startswith('-')
        if negative:
            integer_part = integer_part[1:]

        # Only add separators if >= 5 digits (10000+)
        if len(integer_part) >= 5:
            # Insert thin space every 3 digits from the right
            parts = []
            while len(integer_part) > 3:
                parts.insert(0, integer_part[-3:])
                integer_part = integer_part[:-3]
            parts.insert(0, integer_part)
            integer_part = r'\,'.join(parts)

        # Reconstruct
        result = ('-' if negative else '') + integer_part
        if decimal_part is not None:
            result += '.' + decimal_part

        return result

    # Common SI units that need protection from being split by latex2sympy
    SI_UNITS = [
        # Mass
        'kg', 'mg',
        # Length
        'mm', 'cm', 'km',
        # Time
        'ms', 'min', 'hour',
        # Pressure
        'Pa', 'bar',
        # Frequency
        'Hz',
        # Amount
        'mol',
    ]

    def _latex_var_to_internal(self, latex_var: str) -> str:
        """
        Convert a LaTeX variable name to a simple internal name.

        Examples:
            "P_{LED,out}" → "P_LED_out"
            "\\eta_{driver}" → "eta_driver"
            "N_{headers/MPC}" → "N_headers_per_MPC"
            "LED_{R2}" → "LED_R2"
        """
        import re

        result = latex_var

        # 1. Replace Greek letters with their names
        for greek_cmd, greek_name in [
            ('\\eta', 'eta'), ('\\alpha', 'alpha'), ('\\beta', 'beta'),
            ('\\gamma', 'gamma'), ('\\delta', 'delta'), ('\\epsilon', 'epsilon'),
            ('\\theta', 'theta'), ('\\lambda', 'lambda'), ('\\mu', 'mu'),
            ('\\nu', 'nu'), ('\\pi', 'pi'), ('\\rho', 'rho'), ('\\sigma', 'sigma'),
            ('\\tau', 'tau'), ('\\phi', 'phi'), ('\\psi', 'psi'), ('\\omega', 'omega'),
            ('\\Delta', 'Delta'), ('\\Theta', 'Theta'), ('\\Omega', 'Omega'),
            ('\\Sigma', 'Sigma'), ('\\Pi', 'Pi'), ('\\Phi', 'Phi'), ('\\Psi', 'Psi'),
        ]:
            result = result.replace(greek_cmd, greek_name)

        # 2. Remove LaTeX commands and braces
        result = result.replace('\\text{', '').replace('\\mathrm{', '')
        result = result.replace('\\mathit{', '').replace('}', '')
        result = result.replace('{', '').replace('\\', '')

        # 3. Normalize separators
        result = result.replace('/', '_per_')
        result = result.replace(',', '_')

        # 4. Remove spaces
        result = result.replace(' ', '')

        return result

    def _rewrite_with_internal_ids(self, expression_latex: str) -> str:
        """
        Replace all known LaTeX variable names with their internal IDs (v_{n}).

        This is the key to 100% latex2sympy compatibility:
        - Original: "N_{MPC} \\cdot P_{PSU,out}"
        - Internal: "v_{0} * v_{1}"

        The v_{n} format always parses correctly in latex2sympy.

        IMPORTANT: Only replace whole variable names, not parts of LaTeX commands!
        E.g., don't replace 'a' inside '\frac{a}{b}' for the 'a' in 'frac'.
        """
        import re

        result = expression_latex

        # Get all LaTeX -> internal ID mappings
        mappings = self.symbols.get_all_latex_to_internal()

        # Sort by LaTeX length descending to avoid partial matches
        sorted_mappings = sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True)

        # Replace each LaTeX form with its internal ID
        for latex_form, internal_id in sorted_mappings:
            # Escape special regex characters in LaTeX
            escaped = re.escape(latex_form)

            # Use word boundaries to avoid replacing parts of commands
            # For single letters: use negative lookbehind for backslash and letters
            # For multi-char: simpler matching is OK
            if len(latex_form) == 1 and latex_form.isalpha():
                # Single letter: don't match if preceded by backslash or letter
                # or followed by letter (to avoid \frac -> \frv_{0}c)
                pattern = rf'(?<!\\)(?<![a-zA-Z]){escaped}(?![a-zA-Z])'
            else:
                # Multi-char patterns like N_{MPC}: direct replacement is safe
                pattern = escaped

            result = re.sub(pattern, internal_id, result)

        # Convert LaTeX operators to simple operators
        result = result.replace(r'\cdot', '*')
        result = result.replace(r'\times', '*')
        result = result.replace(r'\div', '/')

        return result

    # NOTE: _compute() function removed in v3.0 (Phase 28)
    # The latex2sympy-based computation has been replaced by the custom parser
    # which uses Pint for unit handling. All computation now goes through
    # _compute_with_pint() -> _evaluate_with_custom_parser().

    def _evaluate_with_custom_parser(self, expression_latex: str) -> 'pint.Quantity':
        """
        Evaluate a LaTeX expression using the custom tokenizer/parser pipeline.

        This is the v3.0 Pure Pint Architecture path that bypasses latex2sympy
        and SymPy entirely. Uses:
        - ExpressionTokenizer (Phase 23)
        - ExpressionParser (Phase 24)
        - evaluate_expression_tree (Phase 25)

        Args:
            expression_latex: LaTeX expression to evaluate

        Returns:
            Pint Quantity with the computed result

        Raises:
            ParseError: If tokenization or parsing fails
            CustomEvaluationError: If evaluation fails
        """
        import pint
        ureg = get_pint_registry()

        # Step 1: Rewrite expression with internal IDs (v_{n} format)
        # This ensures multi-letter variables like "Cap" become "v_{0}" which
        # the tokenizer handles correctly
        modified_latex = self._rewrite_with_internal_ids(expression_latex)

        # Build symbol map from our symbol table
        # Map internal IDs (v_{n}) to Pint Quantities
        symbol_map = {}
        for name in self.symbols.all_names():
            entry = self.symbols.get(name)
            if entry:
                pint_qty = self._symbol_to_pint_quantity(entry, ureg)
                if pint_qty is not None:
                    # Store under internal_id for parser lookup (v_{0}, v_{1}, etc.)
                    if hasattr(entry, 'internal_id') and entry.internal_id:
                        symbol_map[entry.internal_id] = pint_qty
                    # Also store under latex_name and original name for fallback
                    if hasattr(entry, 'latex_name') and entry.latex_name:
                        symbol_map[entry.latex_name] = pint_qty
                    symbol_map[name] = pint_qty

        # Tokenize the rewritten expression
        tokenizer = ExpressionTokenizer(modified_latex)
        tokens = tokenizer.tokenize()

        # Parse
        parser = ExpressionParser(tokens)
        tree = parser.parse()

        # Evaluate
        result = evaluate_expression_tree(tree, symbol_map, ureg)
        return result

    def _compute_with_pint(self, expression_latex: str) -> 'pint.Quantity':
        """
        Parse and compute a LaTeX expression using Pint for unit handling.

        Uses the v3.0 Pure Pint Architecture: custom tokenizer -> parser -> Pint evaluation.
        No fallback to latex2sympy - the custom parser handles everything.

        Args:
            expression_latex: LaTeX expression to parse

        Returns:
            A Pint Quantity with the computed result

        Raises:
            EvaluationError: If evaluation fails
        """
        return self._evaluate_with_custom_parser(expression_latex)

    def _symbol_to_pint_quantity(self, entry: Any, ureg: 'pint.UnitRegistry') -> 'Optional[pint.Quantity]':
        """
        Convert a SymbolValue entry to a Pint Quantity.

        Args:
            entry: A SymbolValue from the symbol table
            ureg: Pint unit registry

        Returns:
            Pint Quantity or None if conversion fails
        """
        try:
            # Get numeric value
            if hasattr(entry, 'original_value') and entry.original_value is not None:
                value = entry.original_value
            elif hasattr(entry, 'value'):
                import sympy
                if hasattr(entry.value, 'is_number') and entry.value.is_number:
                    value = float(entry.value)
                else:
                    try:
                        value = float(sympy.N(entry.value))
                    except Exception:
                        return None
            else:
                return None

            # Get unit
            unit_str = None
            if hasattr(entry, 'original_unit') and entry.original_unit:
                unit_str = entry.original_unit
            elif hasattr(entry, 'unit') and entry.unit:
                unit_str = str(entry.unit)

            # Create Pint Quantity
            if unit_str:
                from .pint_backend import clean_latex_unit
                unit_str = clean_latex_unit(unit_str)
                unit_str = unit_str.replace('€', 'EUR').replace('$', 'USD')
                unit_str = unit_str.replace('²', '**2').replace('³', '**3')
                try:
                    return value * ureg(unit_str)
                except Exception:
                    return value * ureg.dimensionless
            else:
                return value * ureg.dimensionless

        except Exception:
            return None

    def _normalize_latex(self, latex_str: str) -> str:
        """
        Parses LaTeX and re-emits it standardly formatted,
        WITHOUT evaluating variables (symbols remain symbols).

        Uses same pre-processing as _compute() for consistency.
        """
        import re

        try:
            modified = latex_str

            # Same pre-processing as _compute():
            # 1. Add braces to subscripts
            modified = re.sub(
                r'([a-zA-Z])_([a-zA-Z0-9])(?![a-zA-Z0-9])',
                r'\1_{\2}',
                modified
            )

            # NOTE: \cdot -> * replacement REMOVED - fixed in local latex2sympy fork

            # 2. Greek letter + following symbol
            greek_space_pattern = r'\\(Delta|Theta|Omega|Sigma|Pi|alpha|beta|gamma|delta|theta|omega|sigma|pi|phi|psi|lambda|mu|nu|epsilon|rho|tau)\s+([a-zA-Z](?:_\{?[a-zA-Z0-9,]+\}?)?)'

            def greek_replacement(m):
                greek = m.group(1)
                following = m.group(2)
                combined = f"{greek}_{following}"
                return f'\\text{{{combined}}}'

            modified = re.sub(greek_space_pattern, greek_replacement, modified)

            # 3. Protect SI units
            for unit in sorted(self.SI_UNITS, key=len, reverse=True):
                if len(unit) > 1 and f'\\text{{{unit}}}' not in modified:
                    modified = re.sub(rf'\b{re.escape(unit)}\b', rf'\\text{{{unit}}}', modified)

            # 4. Protect known variable names
            known_names = sorted(self.symbols.all_names(), key=len, reverse=True)

            for name in known_names:
                if '\\text{' + name + '}' in modified:
                    continue

                if '_' in name:
                    base, subscript = name.split('_', 1)
                    if len(base) > 1:
                        protected = '\\text{' + base + '}_{' + subscript + '}'
                        if protected in modified:
                            continue
                        pattern = rf'(?<!\\text\{{){re.escape(name)}\b'
                        modified = re.sub(
                            pattern,
                            lambda m, b=base, s=subscript: f'\\text{{{b}}}_{{{s}}}',
                            modified
                        )
                elif len(name) > 1:
                    protected = '\\text{' + name + '}'
                    if protected not in modified:
                        pattern = rf'(?<!\\text\{{){re.escape(name)}\b'
                        modified = re.sub(
                            pattern,
                            lambda m, n=name: '\\text{' + n + '}',
                            modified
                        )

            # 5. Wrap remaining multi-letter sequences
            # First protect LaTeX commands from partial matching
            latex_commands = [
                # Math functions
                'frac', 'sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'exp',
                'text', 'mathrm', 'mathit', 'cdot', 'times', 'div',
                'left', 'right', 'begin', 'end', 'over', 'int', 'sum',
                'prod', 'lim', 'infty', 'partial', 'nabla', 'vec', 'hat',
                'bar', 'dot', 'ddot', 'tilde', 'prime', 'quad', 'qquad',
                # Greek letters (lowercase)
                'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon',
                'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa',
                'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi',
                'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon',
                'phi', 'varphi', 'chi', 'psi', 'omega',
                # Greek letters (uppercase)
                'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta',
                'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu',
                'Nu', 'Xi', 'Pi', 'Rho', 'Sigma', 'Tau',
                'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
            ]

            placeholders = {}
            for i, cmd in enumerate(latex_commands):
                placeholder = f'⌘{i}⌘'  # Unicode char won't match regex
                placeholders[placeholder] = f'\\{cmd}'
                modified = modified.replace(f'\\{cmd}', placeholder)

            def wrap_multiletter(match):
                word = match.group(1)
                return f'\\text{{{word}}}'

            modified = re.sub(
                r'([a-zA-Z]{2,})(?=_|\s|$|\*|\{|\+|\-|\/|\)|\^|\,)',
                lambda m: wrap_multiletter(m),
                modified
            )

            for placeholder, cmd in placeholders.items():
                modified = modified.replace(placeholder, cmd)

            expr = latex2sympy(modified)
            return self._format_result_with_display(expr)
        except:
             return latex_str

    def _format_result_with_display(self, value: Any) -> str:
        """
        Format result with proper display LaTeX using IR mappings.

        This replaces internal symbol names (like Delta_T_h) with
        their proper LaTeX display form (like \\Delta_{T_h}).
        """
        result = self._format_result(value)

        # Post-process: Replace \text{Greek_X} patterns with proper LaTeX
        import re

        def replace_text_greek(match):
            content = match.group(1)
            # Check if it starts with a Greek letter name
            for greek_name, greek_cmd in GREEK_LETTERS_REVERSE.items():
                if content == greek_name:
                    return greek_cmd
                if content.startswith(greek_name + '_'):
                    subscript = content[len(greek_name) + 1:]
                    return f"{greek_cmd}_{{{subscript}}}"
            # Not a Greek letter, keep as \text{}
            return f"\\text{{{content}}}"

        result = re.sub(r'\\text\{([^}]+)\}', replace_text_greek, result)

        return result

    def _simplify_subscripts(self, latex_str: str) -> str:
        """Simplify LaTeX subscripts: a_{1} -> a_1 for single-char subscripts."""
        import re
        # Replace _{X} with _X where X is a single alphanumeric character
        return re.sub(r'_\{([a-zA-Z0-9])\}', r'_\1', latex_str)

    def _format_result(
        self,
        value: Any,
        skip_si_conversion: bool = False,
        config: Optional[LivemathConfig] = None
    ) -> str:
        """Format the result for output (simplify, evalf numericals).

        Args:
            value: The SymPy expression to format
            skip_si_conversion: If True, don't auto-convert to SI base units
                               (used when a specific unit was requested via comment)
            config: Config to use for formatting (defaults to self.config)
        """
        cfg = config or self.config
        from sympy.physics.units import convert_to, kg, m, s, A, K, mol, cd, N, J, W, Pa
        from sympy import pi, E, I

        # First: Evaluate symbolic constants (pi, e) to numeric values
        # This prevents things like "5.556 m/(π·s)" - should be "1.768 m/s"
        if hasattr(value, 'subs'):
            try:
                # Replace pi and e with their numeric values
                value = value.subs(pi, float(pi.evalf()))
                value = value.subs(E, float(E.evalf()))
            except:
                pass

        # Convert to SI base units (unless a specific unit was requested)
        # This simplifies things like m³/hour/mm² → m/s
        if not skip_si_conversion:
            try:
                # SI base units for conversion
                si_base = [kg, m, s, A, K, mol, cd]

                converted = convert_to(value, si_base)
                # If conversion succeeded and simplified, use it
                if converted != value:
                    value = converted
            except:
                pass  # Keep original if conversion fails

        # If value has no free symbols but contains functions (like log), evaluate numerically
        if hasattr(value, 'free_symbols') and len(value.free_symbols) == 0:
            if hasattr(value, 'evalf'):
                try:
                    numeric_val = value.evalf()
                    # Only use evalf if it returns a number
                    if hasattr(numeric_val, 'is_number') and numeric_val.is_number:
                        value = numeric_val
                except:
                    pass

        if hasattr(value, 'as_coeff_Mul'):
            coeff, rest = value.as_coeff_Mul()

            # If coeff is 1, it might be hidden in structure (e.g. (9.8*m)/s^2)
            if coeff == 1 and hasattr(value, 'expand'):
                 try:
                     expanded = value.expand()
                     e_coeff, e_rest = expanded.as_coeff_Mul()
                     if e_coeff != 1:
                         # Found a hidden coefficient! Use expanded form
                         value = expanded
                         coeff, rest = e_coeff, e_rest
                 except:
                     pass

            # Helper to format number for display
            # Uses config for digits and format settings
            def fmt_num(n):
                # First try to evaluate to a numeric value (handles pi, e, sqrt(2), etc.)
                if hasattr(n, 'evalf'):
                    try:
                        numeric = n.evalf()
                        if hasattr(numeric, 'is_number') and numeric.is_number:
                            return self._format_numeric(float(numeric), config=cfg)
                    except:
                        pass
                # Fallback: check if already a number
                if hasattr(n, 'is_number') and n.is_number:
                    return self._format_numeric(float(n), config=cfg)
                return self._simplify_subscripts(sympy.latex(n))

            # If rest is 1, it's just a number
            if rest == 1:
                return fmt_num(coeff)

            # If coeff is 1, it's just units/symbols
            if coeff == 1:
                return self._format_unit_part(rest)

            # Mixed: number + unit
            c_str = fmt_num(coeff)
            r_str = self._format_unit_part(rest)

            # Format as "number\ unit" for proper LaTeX spacing
            return f"{c_str}\\ {r_str}"

        return self._simplify_subscripts(sympy.latex(value, mul_symbol='dot'))

    def _format_unit_part(self, unit_expr: Any) -> str:
        """
        Format the unit part of a result for KaTeX-compatible LaTeX.

        Converts SymPy unit expressions to readable LaTeX:
        - euro -> €
        - kilogram -> kg
        - meter/second -> m/s
        - euro/(kilowatt*hour) -> €/kWh

        KaTeX requirements:
        - Powers must be outside \\text{}: \\text{m}^2 not \\text{m^2}
        - Use \\cdot for multiplication, not · character
        """
        from .pint_backend import format_unit_latex
        from sympy.physics.units import Quantity

        # Check if this contains unit Quantities
        if hasattr(unit_expr, 'atoms'):
            quantities = unit_expr.atoms(Quantity)
            if quantities:
                # Use our custom formatter
                formatted = format_unit_latex(unit_expr)
                if formatted:
                    # Make KaTeX compatible
                    formatted = self._make_katex_compatible(formatted)
                    return formatted

        # Fallback: use SymPy's latex
        return self._simplify_subscripts(sympy.latex(unit_expr, mul_symbol='dot'))

    def _make_katex_compatible(self, unit_str: str) -> str:
        """
        Convert unit string to KaTeX-compatible LaTeX.

        Handles:
        - m^2 -> \\text{m}^{2}
        - kg·m/s -> \\text{kg} \\cdot \\text{m/s}
        - € -> \\text{€}
        """
        import re

        # Replace Unicode middle dot with LaTeX cdot marker (temporary)
        unit_str = unit_str.replace('·', ' CDOT_MARKER ')

        # Handle powers: split on ^ and format properly
        # Pattern: unit^power (e.g., m^2, s^-1)
        if '^' in unit_str:
            # Split into parts around operators
            parts = re.split(r'(\s*/\s*|\s*CDOT_MARKER\s*)', unit_str)
            result_parts = []

            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if part == '/':
                    result_parts.append('/')
                    continue
                if part == 'CDOT_MARKER':
                    result_parts.append(r' \cdot ')
                    continue

                # Check for power
                if '^' in part:
                    base, power = part.split('^', 1)
                    result_parts.append(f"\\text{{{base}}}^{{{power}}}")
                else:
                    result_parts.append(f"\\text{{{part}}}")

            return ''.join(result_parts)

        # No powers - simple wrapping
        # But handle division and multiplication
        if '/' in unit_str or 'CDOT_MARKER' in unit_str:
            # Split by / and CDOT_MARKER, wrap each part
            parts = re.split(r'(/|CDOT_MARKER)', unit_str)
            result_parts = []

            for part in parts:
                part = part.strip()
                if part == '/':
                    result_parts.append('/')
                elif part == 'CDOT_MARKER':
                    result_parts.append(r' \cdot ')
                elif part:
                    result_parts.append(f"\\text{{{part}}}")

            return ''.join(result_parts)

        # Simple unit
        return f"\\text{{{unit_str}}}"
