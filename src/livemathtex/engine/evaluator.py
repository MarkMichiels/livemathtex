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
        Normalize a LaTeX symbol name to match what our _compute() produces.

        Converts:
          - \\Delta_h -> Delta_h
          - \\Delta T_h -> Delta_T_h (Greek + space + symbol becomes combined)
          - \\theta_1 -> theta_1
          - \\dot{m}_h -> dot{m}_h (keeps structure but removes leading backslash)
          - T_{h,in} -> T_{h,in} (unchanged, already compatible)
        """
        if not name:
            return name

        import re

        # Handle Greek letter + space + symbol pattern: \Delta T_h -> Delta_T_h
        greek_space_pattern = r'^\\(Delta|Theta|Omega|Sigma|Pi|alpha|beta|gamma|delta|theta|omega|sigma|pi|phi|psi|lambda|mu|nu|epsilon|rho|tau)\s+([a-zA-Z](?:_\{?[a-zA-Z0-9,]+\}?)?)$'
        match = re.match(greek_space_pattern, name)
        if match:
            greek = match.group(1)
            following = match.group(2)
            return f"{greek}_{following}"

        # Common Greek letters that latex2sympy converts
        # Pattern: \Greek -> Greek (strip backslash, keep name)
        greek_pattern = r'^\\([a-zA-Z]+)'
        match = re.match(greek_pattern, name)
        if match:
            # \Delta_h -> Delta_h
            return name[1:]  # Just remove the leading backslash

        return name

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

        # VALIDATION: Check if variable name conflicts with a unit
        # Extract the base name (without subscripts or function args)
        base_name = target
        if target:
            # Remove subscript notation: x_1 -> x, mass_2 -> mass
            base_match = re.match(r'^([a-zA-Z_]+)', target)
            if base_match:
                base_name = base_match.group(1)

            # Check for conflict with reserved unit names
            if base_name in self.RESERVED_UNIT_NAMES:
                raise EvaluationError(
                    f"Variable name '{target}' conflicts with SI unit '{base_name}'. "
                    f"Use a different name like '{base_name}_val' or 'my_{base_name}'."
                )

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
        import re

        modified_latex = expression_latex

        # Pre-process: Convert Greek letter + following symbol patterns to single symbols
        # This handles cases like "\Delta T_h" which latex2sympy would split into Delta * T_h
        # We convert to a form like "\text{Delta_T_h}" that's treated as one symbol
        greek_space_pattern = r'\\(Delta|Theta|Omega|Sigma|Pi|alpha|beta|gamma|delta|theta|omega|sigma|pi|phi|psi|lambda|mu|nu|epsilon|rho|tau)\s+([a-zA-Z](?:_\{?[a-zA-Z0-9,]+\}?)?)'

        def greek_replacement(m):
            greek = m.group(1)
            following = m.group(2)
            # Create a combined symbol name that we'll track
            combined = f"{greek}_{following}"
            return f'\\text{{{combined}}}'

        modified_latex = re.sub(greek_space_pattern, greek_replacement, modified_latex)

        # Pre-process: Protect SI units from being split
        for unit in sorted(self.SI_UNITS, key=len, reverse=True):
            if len(unit) > 1 and f'\\text{{{unit}}}' not in modified_latex:
                modified_latex = re.sub(rf'\b{re.escape(unit)}\b', rf'\\text{{{unit}}}', modified_latex)

        # Pre-process: Replace known multi-letter variable names with \text{} wrapper
        # to prevent latex2sympy from splitting them into individual letters
        # BUT: Don't wrap names with subscripts (like m_1) - KaTeX can't handle \text{m_1}
        known_names = sorted(self.symbols.all_names(), key=len, reverse=True)

        for name in known_names:
            # Skip single letters (they're fine) and subscripted names (e.g., m_1, F_2)
            # Subscripted names are valid LaTeX and don't need \text{} wrapping
            if len(name) > 1 and '_' not in name:
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
        Protects multi-letter variable names and SI units from being split.
        """
        import re

        try:
            modified = latex_str

            # Pre-process: Convert Greek letter + following symbol patterns to single symbols
            greek_space_pattern = r'\\(Delta|Theta|Omega|Sigma|Pi|alpha|beta|gamma|delta|theta|omega|sigma|pi|phi|psi|lambda|mu|nu|epsilon|rho|tau)\s+([a-zA-Z](?:_\{?[a-zA-Z0-9,]+\}?)?)'

            def greek_replacement(m):
                greek = m.group(1)
                following = m.group(2)
                combined = f"{greek}_{following}"
                return f'\\text{{{combined}}}'

            modified = re.sub(greek_space_pattern, greek_replacement, modified)

            # Pre-process: Protect SI units from being split
            for unit in sorted(self.SI_UNITS, key=len, reverse=True):
                if len(unit) > 1 and f'\\text{{{unit}}}' not in modified:
                    modified = re.sub(rf'\b{re.escape(unit)}\b', rf'\\text{{{unit}}}', modified)

            # Pre-process: Wrap known multi-letter variable names in \text{}
            # BUT: Don't wrap names with subscripts (like m_1) - KaTeX can't handle \text{m_1}
            known_names = sorted(self.symbols.all_names(), key=len, reverse=True)

            for name in known_names:
                if len(name) > 1 and '_' not in name and f'\\text{{{name}}}' not in modified:
                    modified = re.sub(rf'\b{re.escape(name)}\b', rf'\\text{{{name}}}', modified)

            expr = latex2sympy(modified)
            return self._format_result(expr)
        except:
             return latex_str

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

            # Helper to format number
            def fmt_num(n):
                if hasattr(n, 'is_number') and n.is_number:
                     # Convert to float to avoid \frac{}{}
                     # Using .4g or similar as preferred? User used 9.8.
                     # Let's try to preserve reasonable precision or just str(float(n))?
                     # .15g usually preserves value well without trailing zeros?
                     # User Example: 9.8 -> 9.8.
                     return f"{float(n):.10g}"
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
