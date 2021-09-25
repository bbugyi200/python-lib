"""
Functions/classes which make use of Python's dynamic nature to inspect a
program's internals.
"""

from functools import wraps
import inspect
from os.path import abspath, isfile, realpath
from pathlib import Path
import sys
from typing import Any, Callable
from warnings import warn


def cname(obj: object) -> str:
    """Helper function for getting an object's class name as a string."""
    return obj.__class__.__name__


class Inspector:
    """
    Helper class for python introspection (e.g. What line number is this?)
    """

    def __init__(self, *, up: int = 0) -> None:
        frame = inspect.stack()[up + 1]

        self.module_name = _path_to_module(frame[1])
        self.file_name = frame[1]
        self.line_number = frame[2]
        self.function_name = frame[3]
        self.lines = "".join(frame[4] or [])


def _path_to_module(path: str) -> str:
    P = path

    # HACK: Improves the (still broken) output in some weird cases where
    # python gets confused about paths.
    real_abs_P = realpath(abspath(P))
    if isfile(real_abs_P):
        P = real_abs_P

    if P.endswith((".py", ".px")):
        P = P[:-3]

    sorted_pypaths = sorted(sys.path, key=lambda x: -len(x))
    for pypath in sorted_pypaths:
        pypath = realpath(pypath)
        P = P.replace(pypath + "/", "")

    P = P.replace("/", ".")
    return P


def scriptname(*, up: int = 0) -> str:
    """Returns the name of the current script / module.

    Args:
        up: How far should we crawl up the stack?
    """
    frame = inspect.stack()[up + 1]
    return Path(frame.filename).stem


def deprecated(func: Callable, wmsg: str) -> Callable:
    """
    Used to deprecate @func after renaming it or moving it to a
    different module/package.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        warn(wmsg, category=BugyiDepreciationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return wrapper


class BugyiDepreciationWarning(Warning):
    """DepreciationWarning that doesn't get ignored by default."""
