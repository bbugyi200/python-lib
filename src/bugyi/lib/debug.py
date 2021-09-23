"""Debugging Utilities"""

import functools
import logging
import signal
import traceback
from types import FrameType
from typing import Any, Callable


def sigint_dump() -> None:
    """Sets up a signal handler for SIGINT that prints the stack trace."""

    def int_handler(_signum: int, frame: FrameType) -> None:
        import ipdb  # type: ignore

        ipdb.set_trace()
        traceback.print_stack(frame)

    signal.signal(signal.SIGINT, int_handler)


def trace(log: logging.Logger) -> Callable:
    """Decorator that prints signature of function calls.

    Useful when debugging recursive functions.

    Args:
        log: logging.Logger object.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            pretty_args = ""
            for arg in args:
                if pretty_args:
                    pretty_args = "{0}, {1!r}".format(pretty_args, arg)
                else:
                    pretty_args = repr(arg)

            pretty_kwargs = ""
            for key, value in kwargs.items():
                if pretty_kwargs or pretty_args:
                    pretty_kwargs = "{0}, {1}={2!r}".format(
                        pretty_kwargs, key, value
                    )
                else:
                    pretty_kwargs = "{0}={1!r}".format(key, value)

            log.debug(
                "{0}({1}{2}) -> {3}".format(
                    func.__name__, pretty_args, pretty_kwargs, result
                )
            )
            return result

        return wrapper

    return decorator
