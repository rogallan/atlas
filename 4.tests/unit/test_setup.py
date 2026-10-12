"""Smoke tests to verify project toolchain, imports, and basic environment setup."""

import sys


def test_python_version() -> None:
    """Ensure Python version is 3.11 or newer."""
    assert sys.version_info >= (3, 11), f"Python version must be >= 3.11, got {sys.version_info}"


def test_core_package_imports() -> None:
    """Ensure all core architectural packages are importable."""
    import agent
    import api
    import data
    import mcp
    import providers
    import rag

    assert agent is not None
    assert api is not None
    assert data is not None
    assert mcp is not None
    assert providers is not None
    assert rag is not None
