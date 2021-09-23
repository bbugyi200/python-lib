"""Automates Logging Initialization"""

import functools
import inspect
import os
import sys
import types
from typing import List, Mapping, Optional

from loguru import logger as log


def configure(
    name: str, *, debug: Optional[bool], verbose: Optional[int]
) -> None:
    """Configure the Logger."""
    if debug is None:
        debug = False

    if verbose is None:
        verbose = 0

    if debug:
        verbose += 1

    # In case __file__ is used...
    basename = os.path.basename(name).replace(".py", "")

    def sformat(report: Mapping) -> str:
        verbose = bool("SUPERVISOR_ENABLED" in os.environ)
        fmt_list = _formatter(report, verbose=verbose)
        return "".join(fmt_list)

    def fformat(report: Mapping) -> str:
        fmt_list = _formatter(report, verbose=True)
        return "".join(fmt_list)

    stream_h = dict(
        sink=sys.stderr,
        format=sformat,
        filter=lambda record: "quiet" not in record["extra"],
    )
    file_h = dict(
        sink=f"/var/tmp/{basename}.log", format=fformat, rotation="1 day"
    )

    if verbose > 1:
        stream_h["level"] = file_h["level"] = "TRACE"
    elif verbose > 0:
        stream_h["level"] = file_h["level"] = "DEBUG"
    else:
        stream_h["level"] = "INFO"
        file_h["level"] = "DEBUG"

    log.configure(handlers=[stream_h, file_h])


def _formatter(report: Mapping, *, verbose: bool = False) -> List[str]:
    fmt_list: List[str] = []
    add_field = functools.partial(_add_field, fmt_list)

    DATE_STYLE = ["fg #afd787"]
    if verbose:
        add_field("{time:YYYY-MM-DD HH:mm:ss}", DATE_STYLE)
    else:
        _minutes, _seconds = divmod(report["elapsed"].seconds, 60)
        _milliseconds = report["elapsed"].microseconds // 1000
        _my_elapsed = f"{_minutes:02}:{_seconds:02}.{_milliseconds:03}"
        add_field(f"{_my_elapsed}", DATE_STYLE)

    _level = f"[{report['level']}]"
    add_field(f"{_level:^7}", ["level"])

    if _has_threading(inspect.stack()[2].frame):
        add_field("{thread.name:^10}", ["fg #ffffaf"])

    _process = f"PID:{report['process']}"
    add_field(f"{_process:^9}", ["fg #d78700"])

    _loc = f"{report['file']}::{report['function']}::{report['line']}"
    _max_loc_length = max(
        len(_loc),
        getattr(configure, "max_loc_length", 0),
    )
    setattr(configure, "max_loc_length", _max_loc_length)
    _loc_fmt = "{{loc:^{0}}}".format(_max_loc_length)
    loc = _loc_fmt.format(loc=_loc.replace("<", "\\<"))
    add_field(loc, ["black", "bold"])

    add_field("{message}", ["level"], sep="")

    fmt_list.append("\n{exception}")

    return fmt_list


def _add_field(
    fmt_list: List[str], field: str, marks: List[str], sep: str = " | "
) -> None:
    fmt_list.append(
        f"{''.join(['<' + m + '>' for m in marks])}"
        f"{field}"
        f"{''.join(['</>' for _ in marks])}"
        f"{sep}"
    )


def _has_threading(frame: types.FrameType) -> bool:
    """
    Determines whether or not the given frame has the 'threading' module in
    scope.
    """
    try:
        return isinstance(frame.f_globals["threading"], types.ModuleType)
    except KeyError:
        return False
