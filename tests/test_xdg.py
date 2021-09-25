"""Tests for the bugyi.lib.xdg module."""

import os
from pathlib import Path
from typing import Iterator

from pytest import fixture, mark

from bugyi.lib import xdg


params = mark.parametrize

_HOME = os.getenv("HOME")
_XDG_PARAMS = [
    ("config", f"{_HOME}/.config"),
    ("data", f"{_HOME}/.local/share"),
    ("runtime", "/tmp"),
    ("cache", f"{_HOME}/.cache"),
]
XDG_PARAMS = [(x, Path(y)) for x, y in _XDG_PARAMS]


@fixture(autouse=True)
def setup_envvars() -> Iterator[None]:
    """Configure environment variables before running XDG tests."""
    old_envvar_map = {}
    for key in [
        "XDG_DATA_HOME",
        "XDG_RUNTIME_DIR",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
    ]:
        if key in os.environ:
            old_envvar_map[key] = os.environ[key]
            del os.environ[key]

    yield

    for key, value in old_envvar_map.items():
        os.environ[key] = value


@params("key,expected", XDG_PARAMS)
def test_xdg_init(key: xdg.XDG_Type, expected: Path) -> None:
    """Test the xdg.init_full_dir() function."""
    full_dir = xdg.init_full_dir(key)
    actual = full_dir.parent

    assert expected == actual
    assert Path(full_dir).exists()

    os.rmdir(full_dir)


@params("key,expected", XDG_PARAMS)
def test_xdg_get_base_dir(key: xdg.XDG_Type, expected: Path) -> None:
    """Test the xdg.get_base_dir() function."""
    assert expected == xdg.get_base_dir(key)
