"""
IR Schema - Intermediate Representation for LiveMathTeX.

Version 2.0 (legacy):
- Symbols with original and SI-converted values
- Custom unit definitions as simple strings
- Errors array with line numbers

Version 3.0 (current):
- Clean IDs (v1, f1, x1) as keys
- FormulaInfo for expression tracking
- CustomUnitEntry with full metadata
- Both original and base units for formulas
- Pint-based unit backend
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


# =============================================================================
# IR Schema v3.0 - Full Pint Integration
# =============================================================================


@dataclass
class FormulaInfo:
    """
    Information about a formula expression.

    Attributes:
        expression: The formula using clean IDs (e.g., "v5 * v1 / v2")
        depends_on: List of clean IDs this formula depends on
        parameters: List of clean IDs for function parameters (e.g., ["x1", "x2"])
        parameter_latex: Original LaTeX names for parameters (e.g., ["x", "y"])
    """
    expression: str = ""
    depends_on: List[str] = field(default_factory=list)
    parameters: Optional[List[str]] = None
    parameter_latex: Optional[List[str]] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        result = {
            "expression": self.expression,
            "depends_on": self.depends_on,
        }
        if self.parameters:
            result["parameters"] = self.parameters
        if self.parameter_latex:
            result["parameter_latex"] = self.parameter_latex
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'FormulaInfo':
        """Create from dict."""
        return cls(
            expression=data.get("expression", ""),
            depends_on=data.get("depends_on", []),
            parameters=data.get("parameters"),
            parameter_latex=data.get("parameter_latex"),
        )


@dataclass
class CustomUnitEntry:
    """
    Metadata about a custom unit definition.

    Attributes:
        latex: LaTeX representation (e.g., "€" or "kW")
        type: Unit type: "base", "derived", "compound", or "alias"
        pint_definition: Pint-compatible definition string
        line: Source line number where defined
    """
    latex: str = ""
    type: str = ""  # "base", "derived", "compound", "alias"
    pint_definition: str = ""
    line: int = 0

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "latex": self.latex,
            "type": self.type,
            "pint_definition": self.pint_definition,
            "line": self.line,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CustomUnitEntry':
        """Create from dict."""
        return cls(
            latex=data.get("latex", ""),
            type=data.get("type", ""),
            pint_definition=data.get("pint_definition", ""),
            line=data.get("line", 0),
        )


@dataclass
class SymbolEntryV3:
    """
    Complete information about a defined symbol in v3.0 schema.

    Keys in symbols dict are clean IDs (v1, f1, etc.).
    The latex_name provides the display name.

    Attributes:
        latex_name: Original LaTeX name for display (e.g., "P_{LED,out}")
        original: User's input value and unit
        base: SI-converted (base) value and unit
        conversion_ok: Whether the unit conversion succeeded
        formula: Formula info if this is a computed value
        line: Line number where defined
        conversion_error: Error message if conversion failed
    """
    latex_name: str = ""
    original: ValueWithUnit = field(default_factory=ValueWithUnit)
    base: ValueWithUnit = field(default_factory=ValueWithUnit)
    conversion_ok: bool = True
    formula: Optional[FormulaInfo] = None
    line: int = 0
    conversion_error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        result = {
            "latex_name": self.latex_name,
            "original": self.original.to_dict(),
            "base": self.base.to_dict(),
            "conversion_ok": self.conversion_ok,
            "line": self.line,
        }
        if self.formula:
            result["formula"] = self.formula.to_dict()
        if self.conversion_error:
            result["conversion_error"] = self.conversion_error
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'SymbolEntryV3':
        """Create from dict."""
        formula_data = data.get("formula")
        return cls(
            latex_name=data.get("latex_name", ""),
            original=ValueWithUnit.from_dict(data.get("original", {})),
            base=ValueWithUnit.from_dict(data.get("base", {})),
            conversion_ok=data.get("conversion_ok", True),
            formula=FormulaInfo.from_dict(formula_data) if formula_data else None,
            line=data.get("line", 0),
            conversion_error=data.get("conversion_error"),
        )


@dataclass
class LivemathIRV3:
    """
    Complete Intermediate Representation v3.0.

    This IR serves as central state throughout processing:
    - Lexer populates with calculations and custom units
    - Classifier categorizes (value/formula/function)
    - Evaluator updates with computed values
    - Renderer reads to produce output Markdown
    - Optionally serializes to JSON if requested

    Attributes:
        version: Schema version ("3.0")
        source: Original source file path
        unit_backend: Dict with backend info {"name": "pint", "version": "X.X"}
        custom_units: Dict of unit name -> CustomUnitEntry
        symbols: Dict of clean ID (v1, f1) -> SymbolEntryV3
        errors: List of processing errors
        stats: Summary statistics
    """
    version: str = "3.0"
    source: str = ""
    unit_backend: Dict[str, str] = field(default_factory=lambda: {"name": "pint", "version": ""})
    custom_units: Dict[str, CustomUnitEntry] = field(default_factory=dict)
    symbols: Dict[str, SymbolEntryV3] = field(default_factory=dict)
    errors: List[IRError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    # Internal mapping: latex_name -> clean_id (not serialized to JSON)
    _latex_to_id: Dict[str, str] = field(default_factory=dict, repr=False)

    def get_symbol(self, clean_id: str) -> Optional[SymbolEntryV3]:
        """Get a symbol by its clean ID (v1, f1, etc.)."""
        return self.symbols.get(clean_id)

    def get_symbol_by_latex(self, latex_name: str) -> Optional[SymbolEntryV3]:
        """Get a symbol by its LaTeX name."""
        clean_id = self._latex_to_id.get(latex_name)
        if clean_id:
            return self.symbols.get(clean_id)
        return None

    def get_id_for_latex(self, latex_name: str) -> Optional[str]:
        """Get the clean ID for a LaTeX name."""
        return self._latex_to_id.get(latex_name)

    def set_symbol(self, clean_id: str, entry: SymbolEntryV3) -> None:
        """Add or update a symbol entry."""
        self.symbols[clean_id] = entry
        if entry.latex_name:
            self._latex_to_id[entry.latex_name] = clean_id

    def add_error(self, line: int, message: str) -> None:
        """Add a processing error."""
        self.errors.append(IRError(line=line, message=message))

    def add_custom_unit(self, name: str, entry: CustomUnitEntry) -> None:
        """Add a custom unit definition."""
        self.custom_units[name] = entry

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "version": self.version,
            "source": self.source,
            "unit_backend": self.unit_backend,
            "custom_units": {
                name: entry.to_dict()
                for name, entry in self.custom_units.items()
            },
            "symbols": {
                clean_id: entry.to_dict()
                for clean_id, entry in self.symbols.items()
            },
            "errors": [err.to_dict() for err in self.errors],
            "stats": self.stats,
        }

    def to_json(self, path: Path) -> None:
        """Write IR to JSON file for debugging."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'LivemathIRV3':
        """Create IR from dict."""
        ir = cls(
            version=data.get("version", "3.0"),
            source=data.get("source", ""),
            unit_backend=data.get("unit_backend", {"name": "pint", "version": ""}),
            stats=data.get("stats", {}),
        )

        # Load custom units
        for name, entry_data in data.get("custom_units", {}).items():
            ir.custom_units[name] = CustomUnitEntry.from_dict(entry_data)

        # Load symbols
        for clean_id, entry_data in data.get("symbols", {}).items():
            entry = SymbolEntryV3.from_dict(entry_data)
            ir.symbols[clean_id] = entry
            if entry.latex_name:
                ir._latex_to_id[entry.latex_name] = clean_id

        # Load errors
        for error_data in data.get("errors", []):
            ir.errors.append(IRError.from_dict(error_data))

        return ir

    @classmethod
    def from_json(cls, path: Path) -> 'LivemathIRV3':
        """Load IR from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
