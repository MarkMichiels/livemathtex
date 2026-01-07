"""
IR Builder - Converts parsed Document AST to LivemathIR.

v2.0 (legacy):
- Creates minimal IR structure
- Extracts custom unit definitions as strings

v3.0:
- Full custom unit metadata (type, pint_definition, line)
- Direct IR v3.0 integration
"""

import re
from typing import Optional, Tuple
from pathlib import Path

from ..parser.models import Document, MathBlock, Calculation
from ..parser.lexer import Lexer
from .schema import LivemathIR, SymbolEntry, LivemathIRV3, CustomUnitEntry


class IRBuilder:
    """
    Builds a LivemathIR from a parsed Document.

    The v2.0 builder is minimal:
    - Creates empty IR structure
    - Extracts custom unit definitions (===)
    - Symbols are populated by the Evaluator
    """

    def __init__(self):
        self.lexer = Lexer()

    def build(self, document: Document, source: str = "") -> LivemathIR:
        """
        Build IR from a parsed Document.

        Args:
            document: Parsed Document AST
            source: Source file path (for metadata)

        Returns:
            LivemathIR ready for evaluation
        """
        ir = LivemathIR(source=source)

        # Extract custom unit definitions
        for block in document.children:
            if isinstance(block, MathBlock):
                calculations = self.lexer.extract_calculations(block)
                for calc in calculations:
                    if calc.operation == "===":
                        # Unit definition: unit === expr
                        unit_name = calc.target.strip() if calc.target else ""
                        definition = calc.original_result.strip() if calc.original_result else ""
                        if unit_name:
                            ir.custom_units[unit_name] = definition

        return ir

    def build_from_text(self, text: str, source: str = "") -> LivemathIR:
        """
        Build IR directly from markdown text.

        Args:
            text: Markdown source text
            source: Source file path (for metadata)

        Returns:
            LivemathIR ready for evaluation
        """
        document = self.lexer.parse(text)
        return self.build(document, source)

    def load_library(self, ir: LivemathIR, library_path: Path) -> None:
        """
        Load symbols from a library JSON file into the IR.

        Library format (v2.0):
        {
            "name": "Library Name",
            "symbols": {
                "symbol_name": {
                    "id": "v_{0}",
                    "original": {"value": 42, "unit": "kg"},
                    "si": {"value": 42, "unit": "kilogram"},
                    "valid": true,
                    "line": 0
                }
            }
        }
        """
        import json

        with open(library_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for name, entry_data in data.get("symbols", {}).items():
            entry = SymbolEntry.from_dict(entry_data)
            ir.set_symbol(name, entry)

    # =========================================================================
    # IR v3.0 Methods
    # =========================================================================

    def build_v3(self, document: Document, source: str = "") -> LivemathIRV3:
        """
        Build IR v3.0 from a parsed Document.

        Args:
            document: Parsed Document AST
            source: Source file path (for metadata)

        Returns:
            LivemathIRV3 ready for evaluation
        """
        import pint
        ir = LivemathIRV3(source=source)

        # Set Pint version in backend info
        ir.unit_backend = {"name": "pint", "version": pint.__version__}

        # Extract custom unit definitions with full metadata
        for block in document.children:
            if isinstance(block, MathBlock):
                calculations = self.lexer.extract_calculations(block)
                for calc in calculations:
                    if calc.operation == "===":
                        entry = self._parse_unit_definition(calc)
                        if entry:
                            ir.add_custom_unit(calc.target.strip(), entry)
                            # Register in Pint
                            self._register_pint_unit(entry)

        return ir

    def build_from_text_v3(self, text: str, source: str = "") -> LivemathIRV3:
        """
        Build IR v3.0 directly from markdown text.

        Args:
            text: Markdown source text
            source: Source file path (for metadata)

        Returns:
            LivemathIRV3 ready for evaluation
        """
        document = self.lexer.parse(text)
        return self.build_v3(document, source)

    def _parse_unit_definition(self, calc: Calculation) -> Optional[CustomUnitEntry]:
        """
        Parse a unit definition (===) into a CustomUnitEntry.

        Determines the unit type:
        - base: Self-referential (e.g., "EUR === EUR") or new dimension
        - derived: Prefix/multiplier (e.g., "kW === 1000 W")
        - compound: Product of units (e.g., "kWh === kW * h")
        - alias: Simple equivalence (e.g., "dag === day")

        Args:
            calc: The Calculation with operation "==="

        Returns:
            CustomUnitEntry with full metadata, or None if invalid
        """
        unit_name = calc.target.strip() if calc.target else ""
        definition = calc.original_result.strip() if calc.original_result else ""
        line = getattr(calc, 'line', 0)

        if not unit_name:
            return None

        # Determine type and Pint definition
        unit_type, pint_def = self._classify_unit_definition(unit_name, definition)

        return CustomUnitEntry(
            latex=unit_name,
            type=unit_type,
            pint_definition=pint_def,
            line=line
        )

    def _classify_unit_definition(self, name: str, definition: str) -> Tuple[str, str]:
        """
        Classify a unit definition and generate Pint syntax.

        Args:
            name: The unit name being defined
            definition: The definition expression

        Returns:
            Tuple of (unit_type, pint_definition)
        """
        # Normalize definition
        def_clean = definition.strip()

        # Self-referential: EUR === EUR (base unit with new dimension)
        if def_clean == name:
            return ("base", f"{name} = [{name.lower()}]")

        # Check for numeric prefix (derived)
        # Pattern: "1000 W", "0.001 bar", etc.
        prefix_match = re.match(
            r'^([0-9.]+(?:e[+-]?\d+)?)\s*\*?\s*([a-zA-Z_][a-zA-Z0-9_]*)$',
            def_clean,
            re.IGNORECASE
        )
        if prefix_match:
            multiplier = prefix_match.group(1)
            base_unit = prefix_match.group(2)
            return ("derived", f"{name} = {multiplier} * {base_unit}")

        # Check for compound (multiplication/division)
        # Pattern: "kW * h", "kg / m³", etc.
        if '*' in def_clean or '·' in def_clean or '/' in def_clean:
            # Convert LaTeX-style multiplication to Pint
            pint_expr = def_clean.replace('·', '*').replace('\\cdot', '*')
            return ("compound", f"{name} = {pint_expr}")

        # Simple alias: dag === day
        return ("alias", f"{name} = {def_clean}")

    def _register_pint_unit(self, entry: CustomUnitEntry) -> bool:
        """
        Register a custom unit in the Pint registry.

        Args:
            entry: The CustomUnitEntry to register

        Returns:
            True if successful, False otherwise
        """
        from ..engine.pint_backend import get_unit_registry
        import pint

        ureg = get_unit_registry()

        try:
            ureg.define(entry.pint_definition)
            return True
        except (pint.errors.RedefinitionError, pint.errors.DefinitionSyntaxError):
            # Unit already defined or invalid syntax
            return False
        except Exception:
            return False
