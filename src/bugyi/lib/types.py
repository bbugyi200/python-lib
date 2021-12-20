"""Helper utilities related to Python types."""

import datetime as dt
from enum import Enum
from pathlib import Path
from typing import Any, Callable, List, NoReturn, TypeVar, Union, get_args


C = TypeVar("C", bound=Callable)
E = TypeVar("E", bound=Exception)
T = TypeVar("T")

DateLike = Union[str, dt.date, dt.datetime]
PathLike = Union[str, Path]


def assert_never(value: NoReturn) -> NoReturn:
    """
    Raises an AssertionError. This function can be used to achieve
    exhaustiveness checking with mypy.

    REFERENCE: https://hakibenita.com/python-mypy-exhaustive-checking
    """
    raise AssertionError(f"Unhandled value: {value} ({type(value).__name__})")


def literal_to_list(
    literal: Any,
) -> List[Union[None, bool, bytes, int, str, Enum]]:
    """
    Convert a typing.Literal into a list.

    Examples:
        >>> from typing import Literal
        >>> literal_to_list(Literal['a', 'b', 'c'])
        ['a', 'b', 'c']

        >>> literal_to_list(Literal['a', 'b', Literal['c', 'd', Literal['e']]])
        ['a', 'b', 'c', 'd', 'e']

        >>> literal_to_list(Literal['a', 'b', Literal[1, 2, Literal[None]]])
        ['a', 'b', 1, 2, None]
    """
    result = []

    for arg in get_args(literal):
        if arg is None or isinstance(arg, (bool, bytes, int, str, Enum)):
            result.append(arg)
        else:
            result.extend(literal_to_list(arg))

    return result
