"""
IR Schema - Dataclasses for the Intermediate Representation.

Inspired by Cortex-JS MathJSON patterns, this provides a clean
separation between LaTeX notation and internal computation names.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


@dataclass
class SymbolMapping:
    """
    Maps between different representations of a symbol.

    Attributes:
        latex_original: The exact LaTeX as written by user (e.g., "\\Delta T_h")
        latex_display: KaTeX-safe LaTeX for rendering (e.g., "\\Delta_{T_h}")
        internal_name: Python/SymPy-safe name (e.g., "Delta_T_h")
    """
    latex_original: str
    latex_display: str
    internal_name: str


@dataclass
class SymbolEntry:
    """
    Complete information about a defined symbol.

    Attributes:
        mapping: The symbol name mappings
        value: Computed numeric value (if evaluated)
        unit: Unit string (e.g., "kilogram", "meter/second")
        unit_latex: Original LaTeX unit string (e.g., "kg", "m/s")
        expression_latex: The RHS expression in LaTeX
        line: Line number where defined
    """
    mapping: SymbolMapping
    value: Optional[float] = None
    unit: Optional[str] = None
    unit_latex: Optional[str] = None
    expression_latex: Optional[str] = None
    line: int = 0

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "mapping": asdict(self.mapping),
            "value": self.value,
            "unit": self.unit,
            "unit_latex": self.unit_latex,
            "expression_latex": self.expression_latex,
            "line": self.line,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SymbolEntry':
        """Create from dict."""
        return cls(
            mapping=SymbolMapping(**data["mapping"]),
            value=data.get("value"),
            unit=data.get("unit"),
            unit_latex=data.get("unit_latex"),
            expression_latex=data.get("expression_latex"),
            line=data.get("line", 0),
        )


@dataclass
class BlockResult:
    """
    Result of processing a single math block.

    Attributes:
        line: Line number in source
        latex_input: Original LaTeX input
        latex_output: Processed LaTeX output (with results)
        operation: The operation type (":=", "==", "=>", ":= ==")
        target: The target symbol's internal_name (if assignment)
        error: Error message if evaluation failed
    """
    line: int
    latex_input: str
    latex_output: str
    operation: str
    target: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "line": self.line,
            "latex_input": self.latex_input,
            "latex_output": self.latex_output,
            "operation": self.operation,
            "target": self.target,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BlockResult':
        """Create from dict."""
        return cls(**data)


@dataclass
class LivemathIR:
    """
    Complete Intermediate Representation for a livemathtex document.

    This is the central data structure that flows through the pipeline:
    Parser -> IR Builder -> Evaluator -> Renderer

    Can be serialized to JSON for debugging (--verbose flag).
    """
    version: str = "1.0"
    source: str = ""
    symbols: Dict[str, SymbolEntry] = field(default_factory=dict)
    blocks: List[BlockResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def get_symbol(self, internal_name: str) -> Optional[SymbolEntry]:
        """Get a symbol by its internal name."""
        return self.symbols.get(internal_name)

    def set_symbol(self, entry: SymbolEntry) -> None:
        """Add or update a symbol entry."""
        self.symbols[entry.mapping.internal_name] = entry

    def get_value(self, internal_name: str) -> Optional[float]:
        """Get the numeric value of a symbol."""
        entry = self.symbols.get(internal_name)
        return entry.value if entry else None

    def add_block(self, result: BlockResult) -> None:
        """Add a processed block result."""
        self.blocks.append(result)
        if result.error:
            self.errors.append(f"Line {result.line}: {result.error}")

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "version": self.version,
            "source": self.source,
            "symbols": {
                name: entry.to_dict()
                for name, entry in self.symbols.items()
            },
            "blocks": [block.to_dict() for block in self.blocks],
            "errors": self.errors,
            "stats": self.stats,
        }

    def to_json(self, path: Path) -> None:
        """Write IR to JSON file for debugging."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'LivemathIR':
        """Create IR from dict."""
        ir = cls(
            version=data.get("version", "1.0"),
            source=data.get("source", ""),
            errors=data.get("errors", []),
            stats=data.get("stats", {}),
        )

        # Load symbols
        for name, entry_data in data.get("symbols", {}).items():
            ir.symbols[name] = SymbolEntry.from_dict(entry_data)

        # Load blocks
        for block_data in data.get("blocks", []):
            ir.blocks.append(BlockResult.from_dict(block_data))

        return ir

    @classmethod
    def from_json(cls, path: Path) -> 'LivemathIR':
        """Load IR from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
