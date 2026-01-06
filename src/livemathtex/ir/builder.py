"""
IR Builder - Converts parsed Document AST to LivemathIR.

This is the bridge between parsing and evaluation, creating a clean
intermediate representation.

Symbol normalization uses the v_{n}/f_{n} architecture from symbols.py.
"""

import re
from typing import List, Optional
from pathlib import Path

from ..parser.models import Document, MathBlock, TextBlock, Calculation
from ..parser.lexer import Lexer
from .schema import LivemathIR, SymbolEntry, SymbolMapping, BlockResult


class IRBuilder:
    """
    Builds a LivemathIR from a parsed Document.

    The IR builder:
    1. Extracts calculations from math blocks
    2. Normalizes symbol names (LaTeX -> internal)
    3. Creates symbol mappings for later evaluation
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

        for block in document.children:
            if isinstance(block, MathBlock):
                self._process_math_block(block, ir)

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

    def _process_math_block(self, block: MathBlock, ir: LivemathIR) -> None:
        """
        Process a single math block and add to IR.

        This extracts calculations and registers symbols.
        """
        calculations = self.lexer.extract_calculations(block)

        # If no calculations, this is a display-only block
        if not calculations:
            return

        line = block.location.start_line if block.location else 0

        for calc in calculations:
            self._process_calculation(calc, ir, line)

    def _process_calculation(self, calc: Calculation, ir: LivemathIR, line: int) -> None:
        """
        Process a single calculation and add to IR.

        This:
        1. Records the target symbol (LaTeX form)
        2. Creates/updates symbol entry
        3. Records the block result (to be filled by evaluator)

        Note: The v_{n} internal IDs are assigned by the Evaluator's NameGenerator,
        not here. The IR stores the original LaTeX names.
        """
        # Handle errors
        if calc.operation == "ERROR":
            ir.add_block(BlockResult(
                line=line,
                latex_input=calc.latex,
                latex_output=calc.latex,  # Will be updated with error
                operation="ERROR",
                target=None,
                error=calc.error_message,
            ))
            return

        # Use the LaTeX target name directly
        target_latex = calc.target

        if target_latex:
            # Create simple mapping (LaTeX name stored as-is)
            # The v_{n} ID will be assigned by the Evaluator
            target_mapping = SymbolMapping(
                latex_original=target_latex,
                latex_display=target_latex,
                internal_name=target_latex,  # Will be replaced by v_{n} at eval time
            )

            # Create or update symbol entry
            existing = ir.get_symbol(target_latex)
            if existing:
                # Update existing entry
                existing_dict = existing.to_dict()
                existing_dict["line"] = line
                ir.symbols[target_latex] = SymbolEntry.from_dict(existing_dict)
            else:
                # Create new entry
                ir.set_symbol(SymbolEntry(
                    mapping=target_mapping,
                    line=line,
                    expression_latex=self._extract_rhs(calc),
                ))

        # Record the block (latex_output will be filled by evaluator)
        ir.add_block(BlockResult(
            line=line,
            latex_input=calc.latex,
            latex_output=calc.latex,  # Placeholder, updated by evaluator
            operation=calc.operation,
            target=target_latex,
        ))

    def _extract_rhs(self, calc: Calculation) -> Optional[str]:
        """
        Extract the right-hand side expression from a calculation.

        For "x := expr ==", returns "expr"
        For "x := expr", returns "expr"
        """
        if not calc.target:
            return None

        # Remove target and := from the latex
        latex = calc.latex

        # Find := position
        assign_pos = latex.find(':=')
        if assign_pos == -1:
            return None

        rhs = latex[assign_pos + 2:].strip()

        # Remove == and anything after
        eval_pos = rhs.find('==')
        if eval_pos != -1:
            rhs = rhs[:eval_pos].strip()

        return rhs if rhs else None

    def load_library(self, ir: LivemathIR, library_path: Path) -> None:
        """
        Load symbols from a library JSON file into the IR.

        Library format:
        {
            "name": "Library Name",
            "symbols": {
                "symbol_name": {
                    "mapping": {...},
                    "value": 42,
                    "unit": "kg"
                }
            }
        }
        """
        import json

        with open(library_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for name, entry_data in data.get("symbols", {}).items():
            # Ensure mapping has all required fields
            if "mapping" not in entry_data:
                entry_data["mapping"] = {
                    "latex_original": name,
                    "latex_display": name,
                    "internal_name": name,
                }

            entry = SymbolEntry.from_dict(entry_data)
            ir.set_symbol(entry)
