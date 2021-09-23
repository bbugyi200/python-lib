import sys
import termios
from textwrap import wrap
import tty
from typing import Any, Callable, Iterator


def getch(prompt: str = None) -> str:
    """Reads a single character from stdin.

    Args:
        prompt (optional): prompt that is presented to user.

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


def _color_factory(N: int) -> Callable[[str], str]:
    def color(msg: str) -> str:
        return "%s%s%s" % ("\033[{}m".format(N), msg, "\033[0m")

    return color


class colors:
    black = _color_factory(30)
    blue = _color_factory(34)
    cyan = _color_factory(36)
    green = _color_factory(32)
    magenta = _color_factory(35)
    red = _color_factory(31)
    white = _color_factory(37)
    yellow = _color_factory(33)


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
