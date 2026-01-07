"""
IR Schema v2.0 - Simplified Intermediate Representation.

This schema provides a minimal, debuggable JSON structure:
- Symbols with original and SI-converted values
- Custom unit definitions
- Errors array with line numbers

No redundant fields, no blocks array - just what's needed for lookup.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


@dataclass
class ValueWithUnit:
    """
    A numeric value with optional unit.

    Attributes:
        value: The numeric value (None if evaluation failed)
        unit: The unit string (None for dimensionless)
    """
    value: Optional[float] = None
    unit: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "value": self.value,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ValueWithUnit':
        """Create from dict."""
        if data is None:
            return cls()
        return cls(
            value=data.get("value"),
            unit=data.get("unit"),
        )


@dataclass
class SymbolEntry:
    """
    Complete information about a defined symbol.

    Attributes:
        id: Internal ID for latex2sympy (e.g., "v_{0}")
        original: User's input value and unit (for display)
        si: SI-converted value and unit (for calculations)
        valid: Whether the unit conversion was successful
        line: Line number where defined
        error: Error message if conversion failed
    """
    id: str = ""
    original: ValueWithUnit = field(default_factory=ValueWithUnit)
    si: ValueWithUnit = field(default_factory=ValueWithUnit)
    valid: bool = True
    line: int = 0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        result = {
            "id": self.id,
            "original": self.original.to_dict(),
            "si": self.si.to_dict(),
            "valid": self.valid,
            "line": self.line,
        }
        if self.error:
            result["error"] = self.error
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'SymbolEntry':
        """Create from dict."""
        return cls(
            id=data.get("id", ""),
            original=ValueWithUnit.from_dict(data.get("original", {})),
            si=ValueWithUnit.from_dict(data.get("si", {})),
            valid=data.get("valid", True),
            line=data.get("line", 0),
            error=data.get("error"),
        )


@dataclass
class IRError:
    """
    An error that occurred during processing.

    Attributes:
        line: Line number where error occurred
        message: Error description
    """
    line: int
    message: str

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "line": self.line,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'IRError':
        """Create from dict."""
        return cls(
            line=data.get("line", 0),
            message=data.get("message", ""),
        )


@dataclass
class LivemathIR:
    """
    Complete Intermediate Representation for a livemathtex document.

    Version 2.0 - Simplified schema with:
    - symbols: Dict of LaTeX name -> SymbolEntry
    - custom_units: Dict of unit name -> definition
    - errors: List of processing errors
    - stats: Summary statistics

    Can be serialized to JSON for debugging (json=true directive).
    """
    version: str = "2.0"
    source: str = ""
    custom_units: Dict[str, str] = field(default_factory=dict)
    symbols: Dict[str, SymbolEntry] = field(default_factory=dict)
    errors: List[IRError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def get_symbol(self, name: str) -> Optional[SymbolEntry]:
        """Get a symbol by its LaTeX name."""
        return self.symbols.get(name)

    def set_symbol(self, name: str, entry: SymbolEntry) -> None:
        """Add or update a symbol entry."""
        self.symbols[name] = entry

    def add_error(self, line: int, message: str) -> None:
        """Add a processing error."""
        self.errors.append(IRError(line=line, message=message))

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "version": self.version,
            "source": self.source,
            "custom_units": self.custom_units,
            "symbols": {
                name: entry.to_dict()
                for name, entry in self.symbols.items()
            },
            "errors": [err.to_dict() for err in self.errors],
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
            version=data.get("version", "2.0"),
            source=data.get("source", ""),
            custom_units=data.get("custom_units", {}),
            stats=data.get("stats", {}),
        )

        # Load symbols
        for name, entry_data in data.get("symbols", {}).items():
            ir.symbols[name] = SymbolEntry.from_dict(entry_data)

        # Load errors
        for error_data in data.get("errors", []):
            ir.errors.append(IRError.from_dict(error_data))

        return ir

    @classmethod
    def from_json(cls, path: Path) -> 'LivemathIR':
        """Load IR from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
