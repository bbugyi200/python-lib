"""Tests for the bugyi.lib.io module."""

from typing import Iterable, Optional

from pytest import mark

from bugyi.lib.io import get_secret


params = mark.parametrize


@params(
    "key,key_parts,directory,actual",
    [
        ("foo", [], None, "foo"),
        ("db", ["dev", "foo"], "infra", "infra/db.dev.foo"),
    ],
)
def test_get_secret(
    key: str,
    key_parts: Iterable[str],
    directory: Optional[str],
    actual: str,
) -> None:
    """Test the get_secret() function."""
    cmd_list = ["echo"]
    secret = get_secret(
        key, *key_parts, cmd_list=cmd_list, directory=directory
    )
    assert secret == actual
