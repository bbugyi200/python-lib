"""Helper utilities related to the subprocess module and the shell."""

import os
import subprocess as sp
from typing import Any, Iterable, List, Tuple

from . import xdg
from .errors import BErr, BResult, BugyiError
from .result import Err, Ok


_DEFAULT_TIMEOUT = 15


def safe_popen(
    cmd_parts: Iterable[str],
    *,
    up: int = 0,
    timeout: int = _DEFAULT_TIMEOUT,
    **kwargs: Any
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

    proc = sp.Popen(cmd_list, **kwargs)

    done_proc = _DoneProcess(proc, cmd_list, timeout=timeout)
    if proc.returncode != 0:
        return done_proc.to_error(up=up + 1)

    return Ok((done_proc.out, done_proc.err))


def unsafe_popen(
    cmd_parts: Iterable[str], timeout: int = _DEFAULT_TIMEOUT, **kwargs: Any
) -> Tuple[str, str]:
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

    proc = sp.Popen(cmd_list, **kwargs)
    done_proc = _DoneProcess(proc, cmd_list, timeout=timeout)

    return (done_proc.out, done_proc.err)


class _DoneProcess:
    def __init__(
        self,
        proc: sp.Popen,
        cmd_list: List[str],
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        self.proc = proc
        self.cmd_list = cmd_list

        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except sp.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

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
                self.proc.returncode, self.cmd_list, maybe_out, maybe_err
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
    proc = sp.Popen(
        "hash {}".format(cmd), shell=True, stdout=sp.PIPE, stderr=sp.PIPE
    )
    return proc.wait() == 0
