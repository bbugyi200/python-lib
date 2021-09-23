"""Tests the bugyi.lib.cli module."""

from bugyi.lib.cli import main


def test_main() -> None:
    """Tests main() function."""
    assert main([""]) == 0
