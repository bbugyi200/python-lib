"""Helper utilities related to the subprocess module and the shell."""

import os
import subprocess as sp
from typing import Any, Iterable, Iterator

from . import xdg
from .errors import BugyiError
from .result import Err, Ok, Result


_DEFAULT_TIMEOUT = 15


class Process:
    """A wrapper around a subprocess.Popen(...) object.

    Examples:
        >>> import subprocess as sp

        >>> echo_factory = lambda x: sp.Popen(["echo", x], stdout=sp.PIPE)

        >>> echo_popen = echo_factory("foo")
        >>> echo_proc = Process(echo_popen)
        >>> echo_proc.out
        'foo'

        >>> echo_popen = echo_factory("bar")
        >>> out, _err = Process(echo_popen)
        >>> out
        'bar'
    """

    def __init__(
        self,
        popen: sp.Popen,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        self.popen = popen

        try:
            stdout, stderr = popen.communicate(timeout=timeout)
        except sp.TimeoutExpired:
            popen.kill()
            stdout, stderr = popen.communicate()

        self.out = "" if stdout is None else str(stdout.decode().strip())
        self.err = "" if stderr is None else str(stderr.decode().strip())

    def __iter__(self) -> Iterator[str]:
        yield from [self.out, self.err]

    def to_error(self, *, up: int = 0) -> Err["Process", BugyiError]:
        """Converts a Process object into an Err(...) object.."""
        maybe_out = ""
        if self.out:
            maybe_out = "\n\n----- STDOUT\n{}".format(self.out)

        maybe_err = ""
        if self.err:
            maybe_err = "\n\n----- STDERR\n{}".format(self.err)

        return Err(
            BugyiError(
                "Command Failed (ec={}): {!r}{}{}".format(
                    self.popen.returncode,
                    self.popen.args,
                    maybe_out,
                    maybe_err,
                ),
                up=up + 1,
            )
        )


def safe_popen(
    cmd_parts: Iterable[str],
    *,
    up: int = 0,
    timeout: int = _DEFAULT_TIMEOUT,
    **kwargs: Any
) -> Result[Process, BugyiError]:
    """Wrapper for subprocess.Popen(...).

    Returns:
        Ok(Process) if the command is successful.
            OR
        Err(BugyiError) otherwise.
    """
    process = unsafe_popen(cmd_parts, timeout=timeout, **kwargs)
    if process.popen.returncode != 0:
        return process.to_error(up=up + 1)

    return Ok(process)


def unsafe_popen(
    cmd_parts: Iterable[str], timeout: int = _DEFAULT_TIMEOUT, **kwargs: Any
) -> Process:
    """Wrapper for subprocess.Popen(...)

    You can use unsafe_popen() instead of safe_popen() when you don't care
    whether or not the command succeeds.

    Returns: (out, err)
    """
    cmd_list = list(cmd_parts)

    kwargs.setdefault("stdout", sp.PIPE)
    kwargs.setdefault("stderr", sp.PIPE)

    popen = sp.Popen(cmd_list, **kwargs)
    process = Process(popen, timeout=timeout)

    return process


def create_pidfile(*, up: int = 0) -> None:
    """Writes PID to file, which is created if necessary.

    Raises:
        StillAliveException: if old instance of script is still alive.
    """
    PIDFILE = "{}/pid".format(xdg.init_full_dir("runtime", up=up + 1))
    if os.path.isfile(PIDFILE):
        old_pid = int(open(PIDFILE, "r").read())
        try:
            os.kill(old_pid, 0)
        except OSError:
            pass
        except ValueError:
            if old_pid != "":
                raise
        else:
            raise StillAliveException(old_pid)

    pid = os.getpid()
    open(PIDFILE, "w").write(str(pid))


class StillAliveException(Exception):
    """Raised when Old Instance of Script is Still Running"""

    def __init__(self, pid: int):
        self.pid = pid


def command_exists(cmd: str) -> bool:
    """Returns True iff the shell command ``cmd`` exists."""
    popen = sp.Popen(
        "hash {}".format(cmd), shell=True, stdout=sp.PIPE, stderr=sp.PIPE
    )
    return popen.wait() == 0
