"""Helper utilities related to IO."""

import errno
import logging
import os
import subprocess as sp
from subprocess import PIPE, Popen
import sys
import termios
from textwrap import wrap
import tty
from typing import Iterable, Iterator

from . import shell
from .meta import scriptname


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


def get_secret(
    key: str,
    *key_parts: str,
    cmd_list: Iterable[str] = None,
    directory: str = None,
    user: str = None,
) -> str:
    """Returns a secret (i.e. a password).

    Args:
        key: The key that the secret is associated with.
        key_parts: If provided, these are treated as part of the secret key and
          are joined with the ``key`` argument by separating each distinct key
          part with a period.
        cmd_list: Optional command list to use for fetching the secret (e.g.
          ["pass", "show"], which is the default). Note: we will append the
          ``key`` argument to this list before running.
        directory: If provided, this directory is prepended to the beginning of
          the ``key`` argument.
        user: Should we use `sudo -u <user>` to run our secret retriever
          command as that user?
    """
    if key_parts:
        key = ".".join([key] + list(key_parts))

    if cmd_list is None:
        cmd_list = ["pass", "show"]

    if directory is not None:
        directory = directory.rstrip("/")
        key = f"{directory}/{key}"

    full_cmd_list = []
    if user is not None:
        full_cmd_list.extend(["sudo", "-u", user])

    full_cmd_list.extend(cmd_list)
    full_cmd_list.append(key)

    secret, _err = shell.safe_popen(full_cmd_list).unwrap()
    return secret


def notify(
    *args: str, title: str = None, urgency: str = None, up: int = 0
) -> None:
    """
    Sends desktop notification with calling script's name as the notification
    title.

    Args:
        *args: Arguments to be passed to the notify-send command.
        title: Notification title.
        urgency: Notification urgency.
        up: How far should we crawl up the stack to get the script's name?
    """
    try:
        assert args, "No notification message specified."
        assert urgency in (
            None,
            "low",
            "normal",
            "critical",
        ), "Invalid Urgency: {}".format(urgency)
    except AssertionError as e:
        raise ValueError(str(e)) from e

    if title is None:
        title = scriptname(up=up + 1)

    cmd_list = ["notify-send"]
    cmd_list.extend([title])

    if urgency is not None:
        cmd_list.extend(["-u", urgency])

    cmd_list.extend(args)

    sp.check_call(cmd_list)


def xkey(key: str) -> None:
    """Wrapper for `xdotool key`"""
    sp.check_call(["xdotool", "key", key])


def xtype(keys: str, *, delay: int = None) -> None:
    """Wrapper for `xdotool type`

    Args:
        keys (str): Keys to type.
        delay (optional): Typing delay.
    """
    if delay is None:
        delay = 150

    keys = keys.strip("\n")

    sp.check_call(["xdotool", "type", "--delay", str(delay), keys])
