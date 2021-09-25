"""Helper functions/classes related to dates/datetimes."""

import datetime as dt
import re
from typing import List

from dateutil.parser import parse as dateutil_parse

from .types import DateLike, assert_never


def parse_date(date: DateLike) -> dt.date:
    """Parses a date string.

    Args:
        date: The date string to parse.

    This function defaults to using dateutil.parser.parse(), but also accepts
    the following special formats for ``date``:

        @t | @today
            Today's date.

        Nd
            N days ago.

        Nw
            N weeks ago.
    """
    if isinstance(date, str):
        date = date.lower()

        match = re.match("^(?P<num>[0-9]+)(?P<ch>d|w)$", date)
        if match:
            num = int(match.group("num"))
            ch = match.group("ch")

            if ch == "d":
                days = num
            else:
                assert ch == "w"
                days = 7 * num

            return dt.date.today() - dt.timedelta(days=days)

    if date in ["@today", "@t"]:
        return dt.date.today()
    elif isinstance(date, str):
        datetime = dateutil_parse(date)
        return datetime.date()
    elif isinstance(date, dt.datetime):
        return date.date()
    elif isinstance(date, dt.date):
        return date
    else:
        assert_never(date)


def parse_daterange(daterange: str) -> List[dt.date]:
    """Transforms a date range specifier into a list of sequential dates.

    Args:
        daterange: A string of the form START_DATE:END_DATE where both
          START_DATE and END_DATE are any value that the parse_date() function
          can parse.
    """
    if ":" not in daterange:
        return [parse_date(daterange)]
    else:
        first_date, last_date = [parse_date(D) for D in daterange.split(":")]

        result = []
        next_date = first_date
        while next_date <= last_date:
            result.append(next_date)
            next_date = next_date + dt.timedelta(days=1)

        return result
