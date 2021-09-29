"""Tests for the bugyi.lib.secrets module."""

from typing import Iterable, Optional

from pytest import mark

from bugyi.lib.secrets import get_secret


params = mark.parametrize


@params(
    "key,key_parts,folder,expected",
    [
        ("foo", [], None, "foo"),
        ("db", ["dev", "foo"], "infra", "infra/db.dev.foo"),
    ],
)
def test_get_secret(
    key: str,
    key_parts: Iterable[str],
    folder: Optional[str],
    expected: str,
) -> None:
    """Test the get_secret() function."""
    cmd_list = ["echo"]
    secret = get_secret(key, *key_parts, cmd_list=cmd_list, folder=folder)
    assert secret == expected
