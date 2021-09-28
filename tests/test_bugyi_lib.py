"""Tests for the bugyi.lib package."""

from bugyi.lib import dummy


def test_dummy() -> None:
    """Test the dummy() function."""
    assert dummy(1, 2) == 3
