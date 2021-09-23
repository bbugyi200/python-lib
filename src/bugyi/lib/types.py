from collections import defaultdict
import datetime as dt
from enum import Enum
from pathlib import Path
import sys
from typing import Any, Callable, List, NoReturn, Type, TypeVar, Union


C = TypeVar("C", bound=Callable)
E = TypeVar("E", bound=Exception)
T = TypeVar("T")

DateLike = Union[str, dt.date, dt.datetime]
PathLike = Union[str, Path]

# The below 'typing' module types are imported from this module by other
# modules/scripts.
#
# Used to maintain Python<=3.7 compatibility.
try:
    from typing import (  # pylint: disable=unused-import
        Final,
        Literal,
        Protocol,
    )
except ImportError:
    try:
        from typing_extension import Final, Literal, Protocol  # type: ignore
    except ImportError:

        class _FinalMock:
            def __getitem__(self, key: Type[T]) -> Type[T]:
                return key

        class _ProtocolMock(type):
            def __getitem__(cls, _key: Any) -> "_ProtocolMock":
                return cls

        Final = _FinalMock()  # type: ignore
        Literal = defaultdict(lambda: str)  # type: ignore
        Protocol = _ProtocolMock("Protocol", (object,), {})  # type: ignore


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
        >>> literal_to_list(Literal['a', 'b', 'c'])
        ['a', 'b', 'c']

        >>> literal_to_list(Literal['a', 'b', Literal['c', 'd', Literal['e']]])
        ['a', 'b', 'c', 'd', 'e']

        >>> literal_to_list(Literal['a', 'b', Literal[1, 2, Literal[None]]])
        ['a', 'b', 1, 2, None]
    """
    assert sys.version_info >= (3, 8), (
        "This function cannot be called from code run by Python<3.8"
        f" ({sys.version})."
    )

    from typing import get_args

    result = []

    for arg in get_args(literal):
        if arg is None or isinstance(arg, (bool, bytes, int, str, Enum)):
            result.append(arg)
        else:
            result.extend(literal_to_list(arg))

    return result
