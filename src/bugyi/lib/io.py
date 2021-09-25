"""Helper utilities related to IO."""

import errno
import logging
import os
from subprocess import PIPE, Popen
import sys
import termios
from textwrap import wrap
import tty
from typing import Any, Iterator

from . import shell


logger = logging.getLogger(__name__)


def getch(prompt: str = None) -> str:
    """Reads a single character from stdin.

    Args:
        prompt: prompt that is presented to user.

    Returns:
        The single character that was read.
    """
    if prompt:
        sys.stdout.write(prompt)

    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def emsg(msg: str) -> None:
    """ERROR Message"""
    print("[ERROR] {}".format(msg))


def imsg(msg: str) -> None:
    """INFO Message"""
    print(">>> {}".format(msg))


def eprint(*args: Any, **kwargs: Any) -> None:
    """Helper function for printing to STDERR."""
    print(*args, file=sys.stderr, **kwargs)


def ewrap(
    multiline_msg: str, width: int = 80, indent: int = 0
) -> Iterator[str]:
    """A better version of textwrap.wrap()."""
    for msg in multiline_msg.split("\n"):
        if not msg:
            yield ""
            continue

        msg = (" " * indent) + msg

        i = 0
        while i < len(msg) and msg[i] == " ":
            i += 1

        spaces = " " * i
        for m in wrap(
            msg, width, subsequent_indent=spaces, drop_whitespace=True
        ):
            yield m


def efill(multiline_msg: str, width: int = 80, indent: int = 0) -> str:
    """A better version of textwrap.fill()."""
    return "\n".join(ewrap(multiline_msg, width, indent))


def confirm(prompt: str) -> bool:
    """Prompt user for 'y' or 'n' answer.

    Returns:
        True iff the user responds to the @prompt with 'y'.
    """
    prompt += " (y/n): "
    y_or_n = input(prompt)
    return y_or_n == "y"


def box(title: str) -> str:
    """Wraps @title in a pretty ASCII box."""
    middle = f"|          {title}          |"
    top = bottom = "+" + ("-" * (len(middle) - 2)) + "+"
    return f"{top}\n{middle}\n{bottom}"


def create_dir(directory: str) -> None:
    """Create directory if it does not already exist.

    Args:
        directory: The full directory path.
    """
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def mkfifo(fifo_path: str) -> None:
    """Creates named pipe if it does not already exist.

    Args:
        fifo_path: The full file path where the named pipe will be created.
    """
    try:
        os.mkfifo(fifo_path)
    except OSError:
        pass


def copy_to_clipboard(clip: str) -> None:
    """Copys a clip to the system clipboard.

    Args:
        clip: The clip that gets copied into the clipboard.
    """
    if shell.command_exists("xclip"):
        tool = "xclip"
        cmd_list = ["xclip", "-sel", "clip"]
    elif shell.command_exists("pbcopy"):
        tool = "pbcopy"
        cmd_list = ["pbcopy"]
    else:
        logger.warning("Neither xclip nor pbcopy are installed.")
        return

    popen = Popen(cmd_list, stdin=PIPE)
    popen.communicate(input=clip.encode())
    logger.info("Copied %s into clipboard using %s.", clip, tool)
