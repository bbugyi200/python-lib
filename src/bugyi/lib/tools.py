"""
Miscellaneous tools, where a "tool" is a function that emulates a script/shell
command.
"""

import subprocess as sp

from . import shell
from .meta import scriptname


def get_secret(key: str) -> str:
    """Returns a secret (i.e. a password).

    Args:
        key: The key that the secret is associated with.
    """
    secret, _err = shell.safe_popen(["pass", "show", key]).unwrap()
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
