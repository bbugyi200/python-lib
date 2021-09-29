"""Tests for the bugyi.lib.dates module."""

import datetime as dt
from typing import Iterator

from freezegun import freeze_time
from pytest import fixture, mark

from bugyi.lib import dates


params = mark.parametrize
TODAY_SPEC = "2021-09-28"
today = dt.datetime.strptime(TODAY_SPEC, "%Y-%m-%d").date()


@fixture(autouse=True, scope="module")
def frozen_time() -> Iterator[None]:
    """Freeze time until our tests are done running."""
    with freeze_time(f"{TODAY_SPEC}T15:45:03.585481Z"):
        yield


@params(
    "date_spec,expected",
    [
        ("2021-09-30", dt.datetime.strptime("2021-09-30", "%Y-%m-%d").date()),
        ("@today", today),
        ("@t", today),
        ("5d", today - dt.timedelta(days=5)),
        ("1w", today - dt.timedelta(days=7)),
        ("3w", today - dt.timedelta(days=21)),
    ],
)
def test_parse_date(date_spec: str, expected: dt.date) -> None:
    """Test the parse_date() function."""
    actual = dates.parse_date(date_spec)
    assert actual == expected
