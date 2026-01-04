from typing import Dict, Any, Optional
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

class Evaluator:
    """
    Executes calculations using SymPy and a SymbolTable.
    """

    def __init__(self):
        self.symbols = SymbolTable()

    def evaluate(self, calculation: Calculation) -> str:
        """
        Process a single calculation node and return the result string (LaTeX).
        """
        try:
            if calculation.operation == "ERROR":
                # Return error with red color
                err_msg = self._escape_latex_text(calculation.error_message or "Unknown error")
                return f"{calculation.latex} \\\\ \\color{{red}}{{\\text{{⚠️ Error: {err_msg}}}}}"
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
            # Escape the error message so it doesn't break LaTeX rendering
            err_msg = self._escape_latex_text(str(e))
            # Use \\ for newline (in display math) or just append?
            # In inline math $, \\ might not work well depending on renderer, but usually acceptable.
            # We use \color{red} for visibility.
            return f"{calculation.latex} \\\\ \\color{{red}}{{\\text{{Error: {err_msg}}}}}"

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
            # Reconstruct content with normalized RHS
            # Note: This changes the 'source' for the next step?
            # Ideally we return this string.
        else:
             lhs = None # Should not happen

        # Execute logic (setting symbols)
        target = calc.target
        import re
        func_match = re.match(r'^\s*([a-zA-Z_]\w*)\s*\(\s*([a-zA-Z_]\w*)\s*\)\s*$', target) if target else None

        if func_match:
            func_name = func_match.group(1)
            arg_name = func_match.group(2)
            arg_sym = sympy.Symbol(arg_name)
            # Use local override to prevent variable substitution during definition
            expr = self._compute(rhs_raw, local_overrides={arg_name: arg_sym})
            func_obj = sympy.Lambda(arg_sym, expr)
            self.symbols.set(func_name, func_obj, raw_latex=rhs_raw)

            # For functions, normalization might be tricky if arguments are involved.
            # But converting expr back to latex usually works.
            # BUT: self._compute evaluated numbers. e.g. f(x) := x + 10/2 -> x + 5.
            # User wants "Formatted Input", not "Evaluated Input" maybe?
            # If I stick to _normalize_latex(rhs_raw), it uses pure parsing without eval.

            assignment_latex = f"{func_name}({arg_name}) := {self._normalize_latex(rhs_raw)}"

        elif target:
            value = self._compute(rhs_raw)
            self.symbols.set(target, value, raw_latex=rhs_raw)
            assignment_latex = f"{target} := {self._normalize_latex(rhs_raw)}"

        else:
            return content

        return assignment_latex

    def _handle_evaluation(self, calc: Calculation) -> str:
        content = calc.latex
        lhs_part, result_part = content.split("==", 1)
        lhs = lhs_part.strip()

        value = self._compute(lhs)

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
        lhs = part1.strip()
        rhs_part, result_part = part2.split("==", 1)
        rhs = rhs_part.strip()

        value = self._compute(rhs)
        self.symbols.set(lhs, value, raw_latex=rhs)

        # Use unit_comment
        value, suffix = self._apply_conversion(value, calc.unit_comment)

        result_latex = self._format_result(value)
        rhs_normalized = self._normalize_latex(rhs)

        return f"{lhs} := {rhs_normalized} == {result_latex}"

    def _apply_conversion(self, value: Any, target_unit_latex: str):
        """
        Attempts to convert value to the target unit defined by latex string.
        Returns (new_value, suffix_string)
        """
        if not target_unit_latex:
            return value, ""

        try:
            # We need to parse the unit string 'N' or 'm/s' into a SymPy unit expression
            target_unit = self._compute(target_unit_latex)

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
        result_latex = sympy.latex(value)
        return f"{lhs} => {result_latex}"

    def _compute(self, expression_latex: str, local_overrides: Dict[str, Any] = None) -> Any:
        import re

        # Pre-process: Replace known multi-letter variable names with \text{} wrapper
        # to prevent latex2sympy from splitting them into individual letters
        modified_latex = expression_latex

        # Get all known symbols sorted by length (longest first to avoid partial matches)
        known_names = sorted(self.symbols.all_names(), key=len, reverse=True)

        for name in known_names:
            if len(name) > 1:  # Only multi-letter names need protection
                # Wrap in \text{} which latex2sympy treats as single symbol
                # But only if not already wrapped
                if f'\\text{{{name}}}' not in modified_latex:
                    modified_latex = re.sub(rf'\b{re.escape(name)}\b', rf'\\text{{{name}}}', modified_latex)

        try:
            expr = latex2sympy(modified_latex)
        except Exception as e:
            raise EvaluationError(f"Failed to parse LaTeX '{expression_latex}': {e}")

        subs_dict = {}

        # 1. Handle Symbols (Variables + Units)
        for sym in expr.free_symbols:
            sym_name = str(sym)

            # Clean name: remove \text{} or \mathrm{} wrapper ONLY
            import re
            clean_name = re.sub(r'^\\(text|mathrm)\{([^}]+)\}$', r'\2', sym_name).strip()

            # Debug
            # print(f"DEBUG: sym='{sym_name}' clean='{clean_name}'")

            # 0. Check overrides
            if local_overrides and clean_name in local_overrides:
                subs_dict[sym] = local_overrides[clean_name]
                continue

            # 1. Check in Symbol Table
            known = self.symbols.get(clean_name)
            if known:
                subs_dict[sym] = known.value
                continue

            # 2. Check in SymPy Units
            if hasattr(u, clean_name):
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
        Protects multi-letter variable names from being split.
        """
        import re

        try:
            # Pre-process: Wrap known multi-letter names in \text{}
            modified = latex_str
            known_names = sorted(self.symbols.all_names(), key=len, reverse=True)

            for name in known_names:
                if len(name) > 1 and f'\\text{{{name}}}' not in modified:
                    modified = re.sub(rf'\b{re.escape(name)}\b', rf'\\text{{{name}}}', modified)

            expr = latex2sympy(modified)
            return self._format_result(expr)
        except:
             return latex_str

    def _format_result(self, value: Any) -> str:
        """Format the result for output (simplify, evalf numericals)."""

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

            # Helper to format number
            def fmt_num(n):
                if hasattr(n, 'is_number') and n.is_number:
                     # Convert to float to avoid \frac{}{}
                     # Using .4g or similar as preferred? User used 9.8.
                     # Let's try to preserve reasonable precision or just str(float(n))?
                     # .15g usually preserves value well without trailing zeros?
                     # User Example: 9.8 -> 9.8.
                     return f"{float(n):.10g}"
                return sympy.latex(n)

            # If rest is 1, it's just a number
            if rest == 1:
                return fmt_num(coeff)

            # If coeff is 1, it's just units/symbols
            if coeff == 1:
                return sympy.latex(rest, mul_symbol='dot')

            # Mixed
            c_str = fmt_num(coeff)
            r_str = sympy.latex(rest, mul_symbol='dot')

            # User request: No dot between numeric and unit. Use space.
            return f"{c_str} {r_str}" # Space separator

        return sympy.latex(value, mul_symbol='dot')
