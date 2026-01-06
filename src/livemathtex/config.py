"""
Configuration system for livemathtex.

Implements a hierarchical configuration system with the following priority
(highest to lowest):

1. CLI -o flag (explicit output path - operational override)
2. Expression-level overrides (<!-- digits:6 -->)
3. Document directives (<!-- livemathtex: ... -->)
4. Local config (.livemathtex.toml in document directory)
5. Project config (pyproject.toml [tool.livemathtex])
6. User config (~/.config/livemathtex/config.toml)
7. Defaults (hardcoded in this module)

Design principle: Documents are self-contained. The same input should produce
the same output regardless of who processes it. Therefore, CLI options do NOT
include formatting settings - only operational flags like -o for output path.
"""

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional
import sys

# Python 3.11+ has tomllib built-in, older versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# Type aliases for configuration values
FormatType = Literal["general", "decimal", "scientific", "engineering"]
UnitSystem = Literal["SI", "imperial", "CGS"]


@dataclass(frozen=True)
class LivemathConfig:
    """
    Immutable configuration for livemathtex processing.

    This dataclass holds all configuration options. It is immutable (frozen=True)
    to ensure configuration doesn't change unexpectedly during processing.
    Use with_overrides() to create a new config with modified values.

    Attributes:
        digits: Significant figures for numeric output (1-15, default: 4)
        format: Number format type (default: "general")
        exponential_threshold: Magnitude at which to switch to scientific notation (default: 3)
        trailing_zeros: Whether to show trailing zeros to fill precision (default: False)
        unit_system: Unit system for calculations (default: "SI")
        timeout: Maximum seconds per expression evaluation (default: 5)
        output: Output mode - "timestamped", "inplace", or specific filename (default: "timestamped")
        simplify_units: Combine to derived units like N·m (default: True)
        auto_simplify: Automatically simplify symbolic results (default: True)
        tolerance: Numerical tolerance for comparisons (default: 1e-12)
    """

    # Tier 1: Core settings
    digits: int = 4
    format: FormatType = "general"
    exponential_threshold: int = 3
    trailing_zeros: bool = False
    unit_system: UnitSystem = "SI"
    timeout: int = 5
    output: str = "timestamped"

    # Tier 2: Advanced settings
    simplify_units: bool = True
    auto_simplify: bool = True
    tolerance: float = 1e-12

    def with_overrides(self, overrides: Dict[str, Any]) -> "LivemathConfig":
        """
        Return a new config with the specified overrides applied.

        Args:
            overrides: Dictionary of setting names to new values.
                       Unknown keys are ignored. None values are ignored.

        Returns:
            New LivemathConfig instance with overrides applied.

        Example:
            >>> config = LivemathConfig()
            >>> new_config = config.with_overrides({"digits": 6, "format": "scientific"})
            >>> new_config.digits
            6
        """
        # Filter to only valid attributes that are not None
        valid = {
            k: v
            for k, v in overrides.items()
            if hasattr(self, k) and v is not None
        }
        if not valid:
            return self
        return replace(self, **valid)

    def resolve_output_path(
        self, input_path: Path, cli_output: Optional[str] = None
    ) -> Path:
        """
        Resolve the actual output path based on config and CLI override.

        Priority: CLI -o > config output setting > default (timestamped)

        Args:
            input_path: Path to the input markdown file
            cli_output: Optional CLI -o override (takes precedence)

        Returns:
            Resolved output path as Path object.

        Examples:
            - output="timestamped" -> input_20260106_2045.md
            - output="inplace" -> same as input_path
            - output="output.md" -> output.md in same directory as input
        """
        # CLI override takes precedence
        if cli_output:
            output_path = Path(cli_output)
            if not output_path.is_absolute():
                output_path = input_path.parent / output_path
            return output_path

        # Config-based resolution
        if self.output == "inplace":
            return input_path
        elif self.output == "timestamped":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            stem = input_path.stem
            return input_path.parent / f"{stem}_{timestamp}.md"
        else:
            # Specific filename - resolve relative to input directory
            output_path = Path(self.output)
            if not output_path.is_absolute():
                output_path = input_path.parent / output_path
            return output_path

    @classmethod
    def load(cls, document_path: Optional[Path] = None) -> "LivemathConfig":
        """
        Load config from all file sources (NOT expression/directive level).

        This loads configuration from files only. Document directives and
        expression-level overrides must be applied separately by the caller.

        Hierarchy (lowest to highest priority):
        1. Defaults (this class)
        2. User config (~/.config/livemathtex/config.toml)
        3. Project config (pyproject.toml [tool.livemathtex])
        4. Local config (.livemathtex.toml in document directory)

        Args:
            document_path: Optional path to the document being processed.
                          Used to find local and project config files.

        Returns:
            LivemathConfig with all file-based settings applied.
        """
        config = cls()  # Start with defaults

        # 1. User config (~/.config/livemathtex/config.toml)
        user_config = Path.home() / ".config" / "livemathtex" / "config.toml"
        if user_config.exists():
            config = config.with_overrides(cls._load_toml(user_config))

        # 2. Project config (find pyproject.toml going up from document)
        if document_path:
            pyproject = cls._find_pyproject(document_path)
            if pyproject:
                config = config.with_overrides(cls._load_pyproject(pyproject))

        # 3. Local config (.livemathtex.toml in document directory)
        if document_path:
            local_config = document_path.parent / ".livemathtex.toml"
            if local_config.exists():
                config = config.with_overrides(cls._load_toml(local_config))

        return config

    @staticmethod
    def _load_toml(path: Path) -> Dict[str, Any]:
        """
        Load and flatten a TOML config file.

        Handles nested [units] section by flattening to top-level keys.

        Args:
            path: Path to TOML file

        Returns:
            Flattened dictionary of configuration values
        """
        with open(path, "rb") as f:
            data = tomllib.load(f)

        # Flatten [units] section to top-level keys
        result = {}
        for key, value in data.items():
            if key == "units" and isinstance(value, dict):
                if "system" in value:
                    result["unit_system"] = value["system"]
                if "simplify" in value:
                    result["simplify_units"] = value["simplify"]
            else:
                result[key] = value
        return result

    @staticmethod
    def _load_pyproject(path: Path) -> Dict[str, Any]:
        """
        Load [tool.livemathtex] section from pyproject.toml.

        Args:
            path: Path to pyproject.toml

        Returns:
            Dictionary of livemathtex settings, or empty dict if section missing
        """
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return LivemathConfig._load_toml_dict(
            data.get("tool", {}).get("livemathtex", {})
        )

    @staticmethod
    def _load_toml_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a TOML dictionary, flattening nested sections.

        Args:
            data: Raw TOML dictionary

        Returns:
            Flattened dictionary suitable for with_overrides()
        """
        result = {}
        for key, value in data.items():
            if key == "units" and isinstance(value, dict):
                if "system" in value:
                    result["unit_system"] = value["system"]
                if "simplify" in value:
                    result["simplify_units"] = value["simplify"]
            else:
                result[key] = value
        return result

    @staticmethod
    def _find_pyproject(start: Path) -> Optional[Path]:
        """
        Find pyproject.toml by walking up from start directory.

        Args:
            start: Starting path (file or directory)

        Returns:
            Path to pyproject.toml if found, None otherwise
        """
        current = start.parent if start.is_file() else start
        for parent in [current] + list(current.parents):
            pyproject = parent / "pyproject.toml"
            if pyproject.exists():
                return pyproject
        return None
