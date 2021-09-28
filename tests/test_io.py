"""Tests for the bugyi.lib.io module."""

from _pytest.monkeypatch import MonkeyPatch

from bugyi.lib import io


def test_confirm(monkeypatch: MonkeyPatch) -> None:
    """Test the io.confirm() function."""
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert io.confirm("test prompt")
