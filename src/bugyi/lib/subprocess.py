"""Helper utilities related to the subprocess module and the shell."""

import os
import subprocess as sp
from typing import Any, Iterable, List, Tuple

from . import xdg
from .errors import BErr, BResult, BugyiError
from .result import Err, Ok


def safe_popen(
    cmd_parts: Iterable[str], *, up: int = 0, **kwargs: Any
) -> BResult[Tuple[str, str]]:
    """Wrapper for subprocess.Popen(...).

    Returns:
        Ok((out, err)) if the command is successful.
            OR
        Err(BugyiError) otherwise.
    """
    cmd_list = list(cmd_parts)

    kwargs.setdefault("stdout", sp.PIPE)
    kwargs.setdefault("stderr", sp.PIPE)

    ps = sp.Popen(cmd_list, **kwargs)

    proc = _DoneProcess(ps, cmd_list)
    if ps.returncode != 0:
        return proc.to_error(up=up + 1)

    return Ok((proc.out, proc.err))


def unsafe_popen(cmd_parts: Iterable[str], **kwargs: Any) -> Tuple[str, str]:
    """Wrapper for subprocess.Popen(...)

    You can use unsafe_popen() instead of safe_popen() when you don't care
    whether or not the command succeeds.

    Returns: (out, err)
    """
    cmd_list = list(cmd_parts)

    if "stdout" not in kwargs:
        kwargs["stdout"] = sp.PIPE

    if "stderr" not in kwargs:
        kwargs["stderr"] = sp.PIPE

    ps = sp.Popen(cmd_list, **kwargs)
    proc = _DoneProcess(ps, cmd_list)

    return (proc.out, proc.err)


class _DoneProcess:
    def __init__(self, ps: sp.Popen, cmd_list: List[str]) -> None:
        self.ps = ps
        self.cmd_list = cmd_list

        stdout, stderr = ps.communicate()
        self.out = "" if stdout is None else str(stdout.decode().strip())
        self.err = "" if stderr is None else str(stderr.decode().strip())

    def to_error(self, *, up: int = 0) -> Err[Tuple[str, str], BugyiError]:
        maybe_out = ""
        if self.out:
            maybe_out = "\n\n----- STDOUT\n{}".format(self.out)

        maybe_err = ""
        if self.err:
            maybe_err = "\n\n----- STDERR\n{}".format(self.err)

        return BErr(
            "Command Failed (ec={}): {!r}{}{}".format(
                self.ps.returncode, self.cmd_list, maybe_out, maybe_err
            ),
            up=up + 1,
        )


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
    ps = sp.Popen(
        "hash {}".format(cmd), shell=True, stdout=sp.PIPE, stderr=sp.PIPE
    )
    return ps.wait() == 0
