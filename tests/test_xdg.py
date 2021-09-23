import os
from pathlib import Path

import pytest

from bugyi import xdg


_xdg_params = [
    ("config", "/home/bryan/.config"),
    ("data", "/home/bryan/.local/share"),
    ("runtime", "/run/user/1000"),
    ("cache", "/home/bryan/.cache"),
]
xdg_params = [(x, Path(y)) for x, y in _xdg_params]


@pytest.mark.parametrize("key, expected_part", xdg_params)
def test_xdg_init(key: xdg.XDG_Type, expected_part: Path) -> None:
    expected = expected_part / "test_xdg"
    assert expected == xdg.init_full_dir(key)
    os.rmdir(expected)


@pytest.mark.parametrize("key, expected", xdg_params)
def test_xdg_get(key: xdg.XDG_Type, expected: Path) -> None:
    assert expected == xdg.get_base_dir(key)


def test_init_failure() -> None:
    with pytest.raises(AssertionError):
        xdg.init_full_dir("bad_key")  # type: ignore
