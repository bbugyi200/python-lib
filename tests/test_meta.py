"""Tests for the meta.py module."""

from pathlib import Path
import sys

from _pytest.monkeypatch import MonkeyPatch
from pytest import mark

from bugyi.lib.meta import Inspector


params = mark.parametrize


def test_inspector__SYS_PATH_BUG(monkeypatch: MonkeyPatch) -> None:
    """Regression test for bug in Inspector.

    This bug occurs when sys.path contains Path objects instead of strings.
    """
    monkeypatch.setattr("sys.path", [Path(p) for p in sys.path])
    inspector = Inspector()
    assert hasattr(inspector, "module_name")
