"""
Pytest configuration and fixtures for LiveMathTeX tests.

This module provides shared fixtures for testing the LiveMathTeX pipeline.
"""

import pytest
from pathlib import Path


# Project paths
@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def examples_dir(project_root: Path) -> Path:
    """Return the examples directory."""
    return project_root / "examples"


@pytest.fixture
def example_dirs(examples_dir: Path) -> list[Path]:
    """Return all example directories that contain input.md files."""
    dirs = []
    for subdir in sorted(examples_dir.iterdir()):
        if subdir.is_dir() and (subdir / "input.md").exists():
            dirs.append(subdir)
    return dirs


# Example data
def get_example_ids() -> list[str]:
    """Get list of example directory names for parametrization."""
    examples_path = Path(__file__).parent.parent / "examples"
    return [
        d.name
        for d in sorted(examples_path.iterdir())
        if d.is_dir() and (d / "input.md").exists()
    ]


EXAMPLE_IDS = get_example_ids()
