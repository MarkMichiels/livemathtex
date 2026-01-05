"""
Symbol Normalization - Convert between LaTeX and internal representations.

This module follows the Cortex-JS / MathJSON standard for symbol representation.

IMPORTANT: When encountering symbol parsing issues, consult:
- Local reference: src/livemathtex/ir/CORTEX_REFERENCE.md
- Cortex-JS repo: /home/mark/Repositories/cortex-compute-engine/
- Key files:
  - parse-symbol.ts: LaTeX symbol parsing logic
  - serializer.ts: Symbol serialization (lines 441-557 are most relevant)
  - definitions-symbols.ts: Greek letter mappings

GitHub: https://github.com/cortex-js/compute-engine

Key conventions from Cortex-JS (definitions-symbols.ts, parse-symbol.ts):

1. Greek Letters:
   - LaTeX command -> internal name: \\alpha -> alpha, \\Delta -> Delta
   - Consistent across uppercase and lowercase

2. Subscripts/Superscripts:
   - Subscript uses '_': x_1, T_{h,in} -> T_h_in
   - Superscript uses '__': x^2 -> x__2
   - Multiple subscripts: x_{a,b} -> x_a_b (commas become underscores)

3. Modifiers (for future extension):
   - \\dot{x} -> x_dot
   - \\hat{x} -> x_hat
   - \\vec{x} -> x_vec
   - \\bar{x} -> x_bar

4. Multi-letter symbols:
   - Use \\text{} or \\mathrm{} for protection from splitting
   - Internal name preserves structure: speed_of_sound

This allows consistent internal representation while preserving LaTeX display forms.
"""

import re
from typing import Tuple
from .schema import SymbolMapping


# Greek letter mappings (LaTeX command -> internal name)
GREEK_LETTERS = {
    # Lowercase
    '\\alpha': 'alpha',
    '\\beta': 'beta',
    '\\gamma': 'gamma',
    '\\delta': 'delta',
    '\\epsilon': 'epsilon',
    '\\varepsilon': 'varepsilon',
    '\\zeta': 'zeta',
    '\\eta': 'eta',
    '\\theta': 'theta',
    '\\vartheta': 'vartheta',
    '\\iota': 'iota',
    '\\kappa': 'kappa',
    '\\lambda': 'lambda',
    '\\mu': 'mu',
    '\\nu': 'nu',
    '\\xi': 'xi',
    '\\pi': 'pi',
    '\\varpi': 'varpi',
    '\\rho': 'rho',
    '\\varrho': 'varrho',
    '\\sigma': 'sigma',
    '\\varsigma': 'varsigma',
    '\\tau': 'tau',
    '\\upsilon': 'upsilon',
    '\\phi': 'phi',
    '\\varphi': 'varphi',
    '\\chi': 'chi',
    '\\psi': 'psi',
    '\\omega': 'omega',
    # Uppercase
    '\\Alpha': 'Alpha',
    '\\Beta': 'Beta',
    '\\Gamma': 'Gamma',
    '\\Delta': 'Delta',
    '\\Epsilon': 'Epsilon',
    '\\Zeta': 'Zeta',
    '\\Eta': 'Eta',
    '\\Theta': 'Theta',
    '\\Iota': 'Iota',
    '\\Kappa': 'Kappa',
    '\\Lambda': 'Lambda',
    '\\Mu': 'Mu',
    '\\Nu': 'Nu',
    '\\Xi': 'Xi',
    '\\Pi': 'Pi',
    '\\Rho': 'Rho',
    '\\Sigma': 'Sigma',
    '\\Tau': 'Tau',
    '\\Upsilon': 'Upsilon',
    '\\Phi': 'Phi',
    '\\Chi': 'Chi',
    '\\Psi': 'Psi',
    '\\Omega': 'Omega',
}

# Reverse mapping for denormalization
GREEK_LETTERS_REVERSE = {v: k for k, v in GREEK_LETTERS.items()}


def _normalize_subscript(subscript: str) -> str:
    """
    Normalize subscript content.

    Examples:
        "h,in" -> "h_in"
        "1" -> "1"
        "out" -> "out"
    """
    # Replace commas with underscores
    result = subscript.replace(',', '_')
    # Remove any braces
    result = result.replace('{', '').replace('}', '')
    return result


def _extract_subscript(latex: str) -> Tuple[str, str]:
    """
    Extract base and subscript from LaTeX.

    Returns:
        Tuple of (base, subscript) where subscript may be empty string

    Examples:
        "T_{h,in}" -> ("T", "h,in")
        "x_1" -> ("x", "1")
        "alpha" -> ("alpha", "")
    """
    # Pattern for subscript with braces: base_{subscript}
    match = re.match(r'^(.+?)_\{([^}]+)\}$', latex)
    if match:
        return match.group(1), match.group(2)

    # Pattern for simple subscript: base_x
    match = re.match(r'^(.+?)_([a-zA-Z0-9]+)$', latex)
    if match:
        return match.group(1), match.group(2)

    return latex, ""


def normalize_symbol(latex: str) -> SymbolMapping:
    """
    Convert LaTeX symbol to normalized forms.

    This creates a SymbolMapping with:
    - latex_original: Exact input
    - latex_display: KaTeX-safe version
    - internal_name: Python/SymPy-safe identifier

    Examples:
        "\\Delta T_h"  -> internal: "Delta_T_h", display: "\\Delta_{T_h}"
        "T_{h,in}"    -> internal: "T_h_in",    display: "T_{h,in}"
        "\\alpha_1"   -> internal: "alpha_1",   display: "\\alpha_1"
        "c_p"         -> internal: "c_p",       display: "c_p"
    """
    latex_original = latex.strip()

    # Start with the original for both
    internal = latex_original
    display = latex_original

    # Step 1: Handle Greek letter followed by space and identifier
    # Pattern: \Delta T_h -> Delta_T_h (internal), \Delta_{T_h} (display)
    greek_space_pattern = r'^(\\[A-Za-z]+)\s+([A-Za-z](?:_\{?[A-Za-z0-9,]+\}?)?)$'
    match = re.match(greek_space_pattern, latex_original)
    if match:
        greek_cmd = match.group(1)
        following = match.group(2)

        if greek_cmd in GREEK_LETTERS:
            greek_name = GREEK_LETTERS[greek_cmd]
            # Normalize the following part
            following_normalized = following.replace(',', '_').replace('{', '').replace('}', '')
            internal = f"{greek_name}_{following_normalized}"
            # For display, wrap the following in a subscript
            display = f"{greek_cmd}_{{{following}}}"
            return SymbolMapping(latex_original, display, internal)

    # Step 2: Handle standalone Greek letters with subscripts
    # Pattern: \alpha_1 -> alpha_1
    for greek_cmd, greek_name in GREEK_LETTERS.items():
        if latex_original.startswith(greek_cmd):
            rest = latex_original[len(greek_cmd):]

            if not rest:
                # Just the Greek letter
                internal = greek_name
                display = greek_cmd
                return SymbolMapping(latex_original, display, internal)

            if rest.startswith('_'):
                # Greek with subscript
                _, subscript = _extract_subscript(latex_original)
                if subscript:
                    subscript_norm = _normalize_subscript(subscript)
                    internal = f"{greek_name}_{subscript_norm}"
                    # Keep display as-is or normalize braces
                    if '_{' in latex_original:
                        display = latex_original
                    else:
                        display = f"{greek_cmd}_{{{subscript}}}"
                    return SymbolMapping(latex_original, display, internal)

    # Step 3: Handle regular variables with subscripts
    base, subscript = _extract_subscript(latex_original)
    if subscript:
        subscript_norm = _normalize_subscript(subscript)
        internal = f"{base}_{subscript_norm}"
        # Ensure display has proper braces for multi-char subscripts
        if len(subscript) > 1 and '_{' not in latex_original:
            display = f"{base}_{{{subscript}}}"
        else:
            display = latex_original
        return SymbolMapping(latex_original, display, internal)

    # Step 4: Simple variable (no Greek, no subscript)
    # Remove any remaining LaTeX commands
    internal = latex_original
    for cmd in ['\\text{', '\\mathrm{', '\\mathit{']:
        if internal.startswith(cmd) and internal.endswith('}'):
            internal = internal[len(cmd):-1]

    # Replace backslashes and braces for internal name
    internal = internal.replace('\\', '').replace('{', '').replace('}', '')

    return SymbolMapping(latex_original, display, internal)


def denormalize_symbol(internal_name: str) -> str:
    """
    Convert internal name back to LaTeX display form.

    This is a best-effort reverse mapping. For accurate display,
    use the latex_display from the SymbolMapping.

    Examples:
        "Delta_T_h" -> "\\Delta_{T_h}"
        "alpha_1" -> "\\alpha_1"
        "T_h_in" -> "T_{h,in}"
    """
    # Check if starts with a Greek letter name
    for greek_name, greek_cmd in GREEK_LETTERS_REVERSE.items():
        if internal_name == greek_name:
            return greek_cmd
        if internal_name.startswith(greek_name + '_'):
            rest = internal_name[len(greek_name) + 1:]
            # Convert back underscores to subscript
            return f"{greek_cmd}_{{{rest}}}"

    # Regular variable with subscript
    if '_' in internal_name:
        parts = internal_name.split('_', 1)
        base = parts[0]
        subscript = parts[1]
        # If subscript has underscores, convert to commas for display
        if '_' in subscript:
            subscript = subscript.replace('_', ',')
        return f"{base}_{{{subscript}}}"

    return internal_name


def is_greek_letter(name: str) -> bool:
    """Check if a name is a Greek letter (internal or LaTeX form)."""
    return name in GREEK_LETTERS or name in GREEK_LETTERS_REVERSE


def latex_to_internal(latex: str) -> str:
    """
    Quick conversion from LaTeX to internal name.

    For full mapping info, use normalize_symbol() instead.
    """
    return normalize_symbol(latex).internal_name


def internal_to_display(internal_name: str) -> str:
    """
    Quick conversion from internal name to display LaTeX.

    For accurate display, use the latex_display from SymbolMapping.
    """
    return denormalize_symbol(internal_name)
