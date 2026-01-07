"""
IR Builder v2.0 - Converts parsed Document AST to LivemathIR.

This is a simplified builder that:
1. Creates a minimal IR structure
2. Extracts custom unit definitions
3. Leaves symbol population to the evaluator

Symbol values are populated during evaluation, not here.
"""

import re
from typing import Optional
from pathlib import Path

from ..parser.models import Document, MathBlock, Calculation
from ..parser.lexer import Lexer
from .schema import LivemathIR, SymbolEntry


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
