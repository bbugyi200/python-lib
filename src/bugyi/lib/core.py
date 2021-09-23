"""
Functions/classes that we were unable to match to a category are placed in this
module. Thus, you should only add code to this module when you are unable to
find ANY other module to add it to.

WARNING: This module probably shouldn't be imported from other modules in this
package.
"""

import atexit
import errno
import os
import random
import signal as sig
import string
import subprocess as sp
import sys
from typing import Callable, Sequence, TypeVar

from loguru import logger as log

from .io import efill, ewrap
from .meta import deprecated
from .types import Protocol


_C = TypeVar("_C", bound=Callable)
_T = TypeVar("_T")


def catch(func: Callable) -> Callable:
    """Wrapper for loguru.logger.catch

    DEPRECATED: Use the main_factory() function instead.
    """
    catcher = log.bind(quiet=True)
    return catcher.catch(
        message="{record[exception].type.__name__}", reraise=True
    )(func)


def create_dir(directory: str) -> None:
    """Create directory if it does not already exist.

    Args:
        directory: full directory path.
    """
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def mkfifo(FIFO_PATH: str) -> None:
    """Creates named pipe if it does not already exist.

    Args:
        FIFO_PATH (str): the full file path where the named pipe will be
        created.
    """
    try:
        os.mkfifo(FIFO_PATH)
    except OSError:
        pass


def secret() -> str:
    """Get Secret String for Use with secret.sh Script"""
    from .meta import scriptname

    secret_key = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(16)
    )
    fp = "/tmp/{}.secret".format(scriptname(up=1))

    @atexit.register
    def remove_secret_file() -> None:  # pylint: disable=unused-variable
        """Exit Handler that Removes Secret File"""
        try:
            os.remove(fp)
        except OSError:
            pass

    with open(fp, "w") as f:
        f.write(secret_key)

    return secret_key


def shell(*cmds: str) -> str:
    """Run Shell Command(s)

    DEPRECATED: Use the bugyi.subprocess module's functions instead.
    """
    out = sp.check_output("; ".join(cmds), shell=True)
    return out.decode().strip()


def signal(*signums: int) -> Callable:
    """A decorator for registering signal handlers."""

    def _signal(handler: Callable) -> Callable:
        for signum in signums:
            sig.signal(signum, handler)

        return handler

    return _signal


class _MainType(Protocol):
    def __call__(self, argv: Sequence[str] = None) -> int:
        pass


def main_factory(
    parse_cli_args: Callable[[Sequence[str]], _T], run: Callable[[_T], int]
) -> _MainType:
    """
    Returns a generic main() function to be used as a script's entry point.
    """
    from .logging import configure as configure_logging
    from .meta import scriptname

    def main(argv: Sequence[str] = None) -> int:
        if argv is None:
            argv = sys.argv

        args = parse_cli_args(argv)

        debug: bool = getattr(args, "debug", False)
        verbose: int = getattr(args, "verbose", 0)
        name = scriptname(up=1)

        configure_logging(name, debug=debug, verbose=verbose)

        log.trace("Trace mode has been enabled.")
        log.debug("args = {!r}", args)

        try:
            status = run(args)
        except KeyboardInterrupt:
            print("Received SIGINT signal. Terminating {}...".format(name))
            return 0
        except Exception:
            log.exception(
                "An unrecoverable error has been raised. Terminating {}...",
                name,
            )
            return 1
        else:
            return status

    return main


def _deprecated_io(io_func: _C) -> _C:
    name = io_func.__name__
    wmsg = (
        f"The '{name}' function should not be imported from the 'core' module."
        f" Use 'from {__package__}.io import {name}' instead."
    )
    return deprecated(io_func, wmsg)


efill = _deprecated_io(efill)
ewrap = _deprecated_io(ewrap)
