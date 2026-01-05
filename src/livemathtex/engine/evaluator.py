"""
LiveMathTeX Evaluator - Core calculation engine.

Symbol Normalization follows the Cortex-JS / MathJSON standard:
https://github.com/cortex-js/compute-engine

IMPORTANT: When encountering symbol parsing or unit issues, consult:
- Local reference: src/livemathtex/ir/CORTEX_REFERENCE.md
- Cortex-JS clone: /home/mark/Repositories/cortex-compute-engine/
- Key files to study:
  - parse-symbol.ts: How they parse LaTeX symbols
  - serializer.ts (lines 441-557): How they serialize back to LaTeX
  - definitions-symbols.ts: Greek letter mappings

Key conventions (from Cortex-JS parse-symbol.ts):
- Greek letters: \\alpha -> alpha, \\Delta -> Delta
- Subscripts use '_': x_1, T_{h,in} -> T_h_in
- Superscripts use '__': x^2 -> x__2
- Modifiers append: x_dot, x_hat, x_vec, x_bar

This allows consistent internal representation while preserving
LaTeX display forms for rendering.
"""

from typing import Dict, Any, Optional, List
import sympy
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
from ..parser.models import Calculation
from ..utils.errors import EvaluationError, UndefinedVariableError
from ..ir.schema import LivemathIR, SymbolEntry, BlockResult
from ..ir.normalize import (
    normalize_symbol, denormalize_symbol, GREEK_LETTERS_REVERSE,
    GREEK_LETTERS, latex_to_internal
)

class Evaluator:
    """
    Executes calculations using SymPy and a SymbolTable.
    """

    # Build reserved names from SymPy units module
    RESERVED_UNIT_NAMES = set()
    for _name in dir(u):
        _obj = getattr(u, _name, None)
        if isinstance(_obj, (u.Quantity,)):
            RESERVED_UNIT_NAMES.add(_name)
    # Add common single-letter and abbreviation units
    RESERVED_UNIT_NAMES.update({
        'm', 's', 'g', 'A', 'K', 'N', 'J', 'W', 'V', 'C', 'F', 'H', 'T',
        'Pa', 'Hz', 'kg', 'mol', 'cd', 'rad', 'sr', 'Wb', 'lx', 'Bq', 'Gy',
        'km', 'cm', 'mm', 'nm', 'pm', 'ms', 'ns', 'ps', 'mg', 'ug',
    })

    def __init__(self):
        self.symbols = SymbolTable()
        self._ir: Optional[LivemathIR] = None  # Current IR being processed

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
                self.symbols.set(name, entry.value)

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
                # Try to extract numeric value
                try:
                    if hasattr(entry.value, 'evalf'):
                        numeric = float(entry.value.evalf())
                        ir_entry.value = numeric
                    elif isinstance(entry.value, (int, float)):
                        ir_entry.value = float(entry.value)
                except:
                    pass

        ir.stats = stats
        self._ir = None
        return ir

    def _get_display_latex(self, internal_name: str, original_latex: str) -> str:
        """
        Get the display LaTeX for a symbol, using IR mapping if available.

        Falls back to denormalize_symbol if no IR mapping exists.
        """
        if self._ir and internal_name in self._ir.symbols:
            return self._ir.symbols[internal_name].mapping.latex_display
        return denormalize_symbol(internal_name)

    def evaluate(self, calculation: Calculation) -> str:
        """
        Process a single calculation node and return the result string (LaTeX).
        """
        try:
            if calculation.operation == "ERROR":
                # Return error on new line, formatted for markdown readability
                err_msg = self._escape_latex_text(calculation.error_message or "Unknown error")
                return f"{calculation.latex}\n\\\\ \\color{{red}}{{\\text{{\n    Error: {err_msg}}}}}"
            elif calculation.operation == ":=":
                return self._handle_assignment(calculation)
            elif calculation.operation == "==":
                return self._handle_evaluation(calculation)
            elif calculation.operation == ":=_==":
                 return self._handle_assignment_evaluation(calculation)
            elif calculation.operation == "=>":
                return self._handle_symbolic(calculation)
            else:
                return ""
        except Exception as e:
            # Return error on new line, formatted for markdown readability
            err_msg = self._escape_latex_text(str(e))
            return f"{calculation.latex}\n\\\\ \\color{{red}}{{\\text{{\n    Error: {err_msg}}}}}"

    def _normalize_symbol_name(self, name: str) -> str:
        """
        Normalize a LaTeX symbol name to internal representation.

        Follows Cortex-JS / MathJSON standard (parse-symbol.ts):
        - Greek letters: \\Delta -> Delta, \\alpha -> alpha
        - Subscripts: T_{h,in} -> T_h_in (commas become underscores)
        - Greek + space: \\Delta T_h -> Delta_T_h

        Uses the normalize module for consistent handling.

        Examples:
            "\\Delta_h"   -> "Delta_h"
            "\\Delta T_h" -> "Delta_T_h"
            "\\theta_1"   -> "theta_1"
            "T_{h,in}"    -> "T_h_in"
            "eta_p"       -> "eta_p"
        """
        if not name:
            return name

        # Use the normalize module for consistent handling
        mapping = normalize_symbol(name)
        return mapping.internal_name

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

    def _handle_assignment(self, calc: Calculation) -> str:
        content = calc.latex
        rhs_raw = content

        if ":=" in content:
            lhs_part, rhs_part = content.split(":=", 1)
            lhs = lhs_part.strip()
            # If '==' is present (shouldn't be in this handler usually, but safety check)
            rhs_raw = rhs_part.split("==")[0].strip() if "==" in rhs_part else rhs_part.strip()

            # Normalize input
            rhs_normalized = self._normalize_latex(rhs_raw)
        else:
             lhs = None # Should not happen

        # Execute logic (setting symbols)
        # Keep original target for display, normalize for storage
        original_target = calc.target
        # NORMALIZE target name: convert LaTeX Greek letters to plain text
        # e.g., \Delta_h -> Delta_h, \theta_1 -> theta_1
        target = self._normalize_symbol_name(calc.target)
        import re

        # NOTE: Variable names CAN overlap with SI unit names (like g, m, s, K, L)
        # The symbol table takes priority over unit lookup in _compute()
        # So if you define $g := 9.81$, then use $F := m \cdot g$,
        # the 'g' will be looked up from symbol table first, not as gram unit

        func_match = re.match(r'^\s*([a-zA-Z_]\w*)\s*\(\s*([a-zA-Z_]\w*)\s*\)\s*$', target) if target else None

        if func_match:
            func_name = func_match.group(1)
            arg_name = func_match.group(2)
            arg_sym = sympy.Symbol(arg_name)
            # Use local override to prevent variable substitution during definition
            expr = self._compute(rhs_raw, local_overrides={arg_name: arg_sym})
            func_obj = sympy.Lambda(arg_sym, expr)
            self.symbols.set(func_name, func_obj, raw_latex=rhs_raw)

            # Use original target for display (preserves \Delta etc.)
            assignment_latex = f"{original_target} := {self._normalize_latex(rhs_raw)}"

        elif target:
            value = self._compute(rhs_raw)
            self.symbols.set(target, value, raw_latex=rhs_raw)
            # Use original LaTeX form for display, normalized form for storage
            assignment_latex = f"{original_target} := {self._normalize_latex(rhs_raw)}"

        else:
            return content

        return assignment_latex

    def _handle_evaluation(self, calc: Calculation) -> str:
        content = calc.latex
        lhs_part, result_part = content.split("==", 1)
        lhs = lhs_part.strip()

        value = self._compute(lhs)

        # Check for undefined variables (symbols that weren't substituted)
        self._check_undefined_symbols(value, lhs)

        # Use unit_comment from parser
        value, suffix = self._apply_conversion(value, calc.unit_comment)

        result_latex = self._format_result(value)

        # Format LHS too? "x * y" -> "x \cdot y"
        # The user said "input mee formatten". LHS of evaluation is input.
        lhs_normalized = self._normalize_latex(lhs)

        return f"{lhs_normalized} == {result_latex}"

    def _handle_assignment_evaluation(self, calc: Calculation) -> str:
        content = calc.latex
        part1, part2 = content.split(":=", 1)
        lhs = part1.strip()  # Original LaTeX form for display
        rhs_part, result_part = part2.split("==", 1)
        rhs = rhs_part.strip()

        value = self._compute(rhs)

        # Check for undefined variables (symbols that weren't substituted)
        self._check_undefined_symbols(value, rhs)

        # Store with normalized name (e.g., \Delta T_h -> Delta_T_h)
        normalized_lhs = self._normalize_symbol_name(lhs)
        self.symbols.set(normalized_lhs, value, raw_latex=rhs)

        # Use unit_comment
        value, suffix = self._apply_conversion(value, calc.unit_comment)

        result_latex = self._format_result(value)
        rhs_normalized = self._normalize_latex(rhs)

        return f"{lhs} := {rhs_normalized} == {result_latex}"

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

            # Check if it's a known unit
            unit_mapping = {'kg', 'g', 'm', 's', 'N', 'J', 'W', 'Pa', 'Hz', 'V', 'A', 'K', 'mol'}
            if clean_name in unit_mapping:
                continue
            if hasattr(u, clean_name):
                unit_val = getattr(u, clean_name)
                if isinstance(unit_val, (u.Unit, u.Quantity)):
                    continue

            # It's not a unit, so it's undefined
            undefined.append(clean_name)

        if undefined:
            raise EvaluationError(f"Undefined variable(s): {', '.join(sorted(undefined))}")

    def _normalize_unit_string(self, unit_str: str) -> str:
        """
        Normalize Unicode characters in unit strings to LaTeX notation.

        Converts:
        - Unicode superscripts: ² → ^2, ³ → ^3
        - Unicode subscripts: ₀ → _0, ₁ → _1
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

        for unicode_char, latex in superscript_map.items():
            unit_str = unit_str.replace(unicode_char, latex)
        for unicode_char, latex in subscript_map.items():
            unit_str = unit_str.replace(unicode_char, latex)

        return unit_str

    def _apply_conversion(self, value: Any, target_unit_latex: str):
        """
        Attempts to convert value to the target unit defined by latex string.
        Returns (new_value, suffix_string)
        """
        if not target_unit_latex:
            return value, ""

        try:
            # Normalize Unicode characters (e.g., m³/s → m^3/s)
            normalized_unit = self._normalize_unit_string(target_unit_latex)

            # We need to parse the unit string 'N' or 'm/s' into a SymPy unit expression
            target_unit = self._compute(normalized_unit)

            from sympy.physics.units import convert_to, kg, m, s, A, K, mol, cd

            # Strategy for partial conversion:
            # 1. Calculate ratio: value / target
            # 2. Convert ratio to base units (so that it simplifies)
            # 3. Result = ratio_base * target

            ratio = value / target_unit
            # List of SI base units to simplify the remainder into
            base_units = [kg, m, s, A, K, mol, cd]

            ratio_base = convert_to(ratio, base_units)

            new_value = ratio_base * target_unit

            return new_value, "" # No suffix needed, renderer handles comment
        except Exception as e:
            # Fallback if conversion fails
            return value, ""

    def _handle_symbolic(self, calc: Calculation) -> str:
        """Handle $expr =>$"""
        content = calc.latex
        lhs = content.split("=>")[0].strip()

        # For symbolic, we just parse and return the latex of the expression,
        # but simplified or acted upon (e.g. diff).
        # But wait, how do we trigger 'diff'?
        # User writes "$diff(f(x), x) =>$"
        # So we just compute 'lhs' as usual. _compute handles function calls like diff if mapped.

        value = self._compute(lhs)
        result_latex = self._simplify_subscripts(sympy.latex(value))
        return f"{lhs} => {result_latex}"

    # Common SI units that need protection from being split by latex2sympy
    SI_UNITS = [
        # Mass
        'kg', 'mg',
        # Length
        'mm', 'cm', 'km',
        # Time
        'ms', 'min',
        # Pressure
        'Pa', 'bar',
        # Frequency
        'Hz',
        # Amount
        'mol',
    ]

    def _compute(self, expression_latex: str, local_overrides: Dict[str, Any] = None) -> Any:
        r"""
        Parse and compute a LaTeX expression.

        Pre-processing follows Cortex-JS philosophy: normalize LaTeX BEFORE parsing
        to work around latex2sympy limitations.

        Key transformations:
        1. Add braces to subscripts: x_y -> x_{y} (consistency)
        2. Wrap multi-letter names in \text{} (prevents T*D*H splitting)

        NOTE: With our local latex2sympy fork (libs/latex2sympy), the \cdot bug is fixed
        and no longer requires conversion to *.
        """
        import re

        modified_latex = expression_latex

        # =================================================================
        # STEP 1: Structural normalization
        # =================================================================

        # 1a. Add explicit braces around subscripts without braces for consistency
        # Pattern: letter_letter (not already letter_{...})
        # NOTE: With our local latex2sympy fork, this is optional but improves consistency
        modified_latex = re.sub(
            r'([a-zA-Z])_([a-zA-Z0-9])(?![a-zA-Z0-9])',
            r'\1_{\2}',
            modified_latex
        )

        # NOTE: \cdot -> * replacement REMOVED - fixed in local latex2sympy fork
        # See: libs/latex2sympy/PS.g4 - DIFFERENTIAL rule no longer captures \cdot

        # =================================================================
        # STEP 2: Greek letter normalization
        # =================================================================

        # Convert Greek letter + following symbol patterns to single symbols
        # "\Delta T_h" -> "\text{Delta_T_h}"
        greek_space_pattern = r'\\(Delta|Theta|Omega|Sigma|Pi|alpha|beta|gamma|delta|theta|omega|sigma|pi|phi|psi|lambda|mu|nu|epsilon|rho|tau)\s+([a-zA-Z](?:_\{?[a-zA-Z0-9,]+\}?)?)'

        def greek_replacement(m):
            greek = m.group(1)
            following = m.group(2)
            combined = f"{greek}_{following}"
            return f'\\text{{{combined}}}'

        modified_latex = re.sub(greek_space_pattern, greek_replacement, modified_latex)

        # =================================================================
        # STEP 3: Protect multi-letter sequences from being split
        # =================================================================

        # 3a. Protect SI units (longest first to avoid partial matches)
        for unit in sorted(self.SI_UNITS, key=len, reverse=True):
            if len(unit) > 1 and f'\\text{{{unit}}}' not in modified_latex:
                modified_latex = re.sub(rf'\b{re.escape(unit)}\b', rf'\\text{{{unit}}}', modified_latex)

        # 3b. Protect known variable names from symbol table
        known_names = sorted(self.symbols.all_names(), key=len, reverse=True)

        for name in known_names:
            if '\\text{' + name + '}' in modified_latex:
                continue

            if '_' in name:
                base, subscript = name.split('_', 1)
                if len(base) > 1:
                    protected = '\\text{' + base + '}_{' + subscript + '}'
                    if protected in modified_latex:
                        continue
                    pattern = rf'(?<!\\text\{{){re.escape(name)}\b'
                    modified_latex = re.sub(
                        pattern,
                        lambda m, b=base, s=subscript: f'\\text{{{b}}}_{{{s}}}',
                        modified_latex
                    )
            elif len(name) > 1:
                protected = '\\text{' + name + '}'
                if protected not in modified_latex:
                    pattern = rf'(?<!\\text\{{){re.escape(name)}\b'
                    modified_latex = re.sub(
                        pattern,
                        lambda m, n=name: '\\text{' + n + '}',
                        modified_latex
                    )

        # 3c. Protect ANY remaining multi-letter sequences (2+ letters)
        # This catches new variable names not yet in symbol table
        #
        # IMPORTANT: First protect LaTeX commands from partial matching
        # Problem: \frac gets matched as \f + rac (rac is 2+ letters after f)
        # Solution: Temporarily replace LaTeX commands with placeholders

        # LaTeX commands to protect from multi-letter wrapping
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

        # Replace \command with placeholder
        # Requirements: No underscores (become subscripts), no multi-letter sequences (get wrapped)
        # Solution: Use numbers only: ⌘0⌘, ⌘1⌘, etc.
        placeholders = {}
        for i, cmd in enumerate(latex_commands):
            placeholder = f'⌘{i}⌘'  # Unicode char won't match regex
            placeholders[placeholder] = f'\\{cmd}'
            modified_latex = modified_latex.replace(f'\\{cmd}', placeholder)

        # Now wrap remaining multi-letter sequences
        # NOTE: \b doesn't work with underscore, use lookahead instead
        def wrap_multiletter(match):
            word = match.group(1)
            return f'\\text{{{word}}}'

        modified_latex = re.sub(
            r'([a-zA-Z]{2,})(?=_|\s|$|\*|\{|\+|\-|\/|\)|\^|\,)',
            lambda m: wrap_multiletter(m),
            modified_latex
        )

        # Restore LaTeX commands
        for placeholder, cmd in placeholders.items():
            modified_latex = modified_latex.replace(placeholder, cmd)

        try:
            expr = latex2sympy(modified_latex)
        except Exception as e:
            raise EvaluationError(f"Failed to parse LaTeX '{expression_latex}': {e}")

        subs_dict = {}

        # 1. Handle Symbols (Variables + Units)
        for sym in expr.free_symbols:
            sym_name = str(sym)

            # Clean name: convert to internal representation
            # Following Cortex-JS / MathJSON standard for symbol normalization
            import re

            # Handle \text{base}_subscript pattern -> base_subscript
            # This is how we protect multi-letter names with subscripts
            subscript_match = re.match(r'^\\text\{([^}]+)\}_(.+)$', sym_name)
            if subscript_match:
                base = subscript_match.group(1)
                subscript = subscript_match.group(2)
                clean_name = f"{base}_{subscript}"
            else:
                # Simple \text{name} or \mathrm{name} wrapper -> name
                match = re.match(r'^\\(text|mathrm)\{([^}]+)\}$', sym_name)
                if match:
                    clean_name = match.group(2)
                else:
                    clean_name = sym_name

            # Normalize any remaining LaTeX patterns (Greek letters, etc.)
            # This ensures \Delta_T_h stored as Delta_T_h is found when
            # latex2sympy produces a symbol like Delta_T_h or \text{Delta_T_h}
            if clean_name and (clean_name.startswith('\\') or '_' in clean_name):
                clean_name = latex_to_internal(clean_name)

            # Debug
            # print(f"DEBUG: sym='{sym_name}' clean='{clean_name}'")

            # 0. Check overrides
            if local_overrides and clean_name in local_overrides:
                subs_dict[sym] = local_overrides[clean_name]
                continue

            # 1. Check in Symbol Table (try multiple name formats)
            # latex2sympy converts \Delta_h -> Delta_h, so we need to match
            known = self.symbols.get(clean_name)
            if not known:
                # Try with backslash prefix (for Greek letters stored as \Delta_h)
                known = self.symbols.get('\\' + clean_name)
            if known:
                subs_dict[sym] = known.value
                continue

            # 2. Check in SymPy Units (with common abbreviation mapping)
            unit_mapping = {
                # Mass
                'kg': u.kilogram,
                'g': u.gram,
                'mg': u.milligram,
                # Length
                'm': u.meter,
                'mm': u.millimeter,
                'cm': u.centimeter,
                'km': u.kilometer,
                # Time
                's': u.second,
                'ms': u.millisecond,
                'min': u.minute,
                'h': u.hour,
                # Force/Energy/Power
                'N': u.newton,
                'J': u.joule,
                'W': u.watt,
                # Pressure
                'Pa': u.pascal,
                'bar': u.bar,
                # Frequency/Electrical
                'Hz': u.hertz,
                'V': u.volt,
                'A': u.ampere,
                # Temperature/Amount
                'K': u.kelvin,
                'mol': u.mole,
            }

            if clean_name in unit_mapping:
                subs_dict[sym] = unit_mapping[clean_name]
                continue
            elif hasattr(u, clean_name):
                unit_val = getattr(u, clean_name)
                if isinstance(unit_val, (u.Unit, u.Quantity)):
                   subs_dict[sym] = unit_val
                   continue

        # 2. Handle Functions (f(x))
        # latex2sympy parses "f(5)" as Function("f")(5)
        # We need to replace Function("f") with our Lambda.
        # Note: expr.free_symbols does NOT include functions.
        for func in expr.atoms(sympy.Function):
            func_name = str(func.func) # 'f'

            if local_overrides and func_name in local_overrides:
                 # Substitute the function object itself?
                 # subs({Function('f'): lambda_obj}) works
                 subs_dict[func.func] = local_overrides[func_name]
                 continue

            known = self.symbols.get(func_name)
            if known:
                # We expect known.value to be a Lambda or something callable
                subs_dict[func.func] = known.value

        if subs_dict:
            expr = expr.subs(subs_dict)

        return expr

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

    def _format_result(self, value: Any) -> str:
        """Format the result for output (simplify, evalf numericals)."""

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
            # Use 4 significant figures for scientific/engineering relevance
            # Full precision is preserved in IR JSON for further calculations
            def fmt_num(n):
                if hasattr(n, 'is_number') and n.is_number:
                     # Convert to float with 4 significant figures
                     # Avoids \frac{}{} and excessive decimals like 0.0002777777778
                     return f"{float(n):.4g}"
                return self._simplify_subscripts(sympy.latex(n))

            # If rest is 1, it's just a number
            if rest == 1:
                return fmt_num(coeff)

            # If coeff is 1, it's just units/symbols
            if coeff == 1:
                return self._simplify_subscripts(sympy.latex(rest, mul_symbol='dot'))

            # Mixed
            c_str = fmt_num(coeff)
            r_str = self._simplify_subscripts(sympy.latex(rest, mul_symbol='dot'))

            # User request: No dot between numeric and unit. Use space.
            return f"{c_str} {r_str}"

        return self._simplify_subscripts(sympy.latex(value, mul_symbol='dot'))
