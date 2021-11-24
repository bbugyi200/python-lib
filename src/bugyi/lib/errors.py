"""Custom error handling code lives here."""

import traceback
from typing import Iterator, List, Optional

from result import Err, Result

from .meta import Inspector, cname
from .types import E, T


BResult = Result[T, "BugyiError"]


class BErr(Err[T, "BugyiError"]):
    """Bugyi Err Type."""

    def __init__(
        self, emsg: str, cause: Exception = None, up: int = 0
    ) -> None:
        e = BugyiError(emsg, cause=cause, up=up + 1)
        super().__init__(e)


class BugyiError(Exception):
    """Custom general-purpose exception."""

    def __init__(
        self, emsg: str, cause: Exception = None, up: int = 0
    ) -> None:
        chain_errors(self, cause)
        self.inspector = Inspector(up=up + 1)
        super().__init__(emsg)

    def __str__(self) -> str:
        return str(self.report())

    def __repr__(self) -> str:
        return self._repr()

    def _repr(self, width: int = 80) -> str:
        """
        Format error to width.  If width is None, return string suitable for
        traceback.
        """
        from .io import efill

        super_str = super().__str__()

        emsg = efill(super_str, width, indent=2)
        return "{}::{}::{}::{}{{\n{}\n}}".format(
            cname(self),
            self.inspector.module_name,
            self.inspector.function_name,
            self.inspector.line_number,
            emsg,
        )

    def __iter__(self) -> Iterator[BaseException]:
        yield self

        e = self.__cause__
        while e:
            yield e
            e = e.__cause__

    def report(self, width: int = 80) -> "_ErrorReport":
        """
        Return an _ErrorReport object formatting the current state of this
        BugyiError
        """
        from .io import ewrap

        TITLE = cname(self)
        MIDDLE_MSG = "was the direct cause of"

        H_CH = "-"  # Horizontal Character
        V_CH = "|"  # Vertical Character
        S_CH = "*"  # Special Character

        nleft_spaces, rem = divmod(width - len(TITLE), 2)
        if rem == 0:
            nright_spaces = nleft_spaces
        else:
            nright_spaces = nleft_spaces + 1

        header = "{0}{1}{2}{3}{0}".format(
            V_CH, " " * nleft_spaces, TITLE, " " * nright_spaces
        )

        minibar_length, rem = divmod(width - len(MIDDLE_MSG), 4)
        left_minibar = (H_CH + S_CH) * minibar_length
        right_minibar = (S_CH + H_CH) * minibar_length

        if rem >= 2:
            left_minibar += H_CH
            right_minibar = S_CH + right_minibar

        if rem % 2 != 0:
            right_minibar = H_CH + right_minibar

        middle_header = "{0} {1} {2}".format(
            left_minibar, MIDDLE_MSG, right_minibar
        )

        dashes = "-" * len(header)

        # >>> Put everything together into a _ErrorReport object.
        report = _ErrorReport("\n", border_ch=V_CH)
        report += "{0}\n{1}\n{0}\n".format(dashes, header)
        for i, error in enumerate(reversed(list(self))):
            w = width - 2
            error_string = _tb_or_repr(error, width=w)
            if i != 0:
                report += "{0}\n{1}\n{0}\n".format(dashes, middle_header)

            for line in ewrap(error_string, w):
                right_spaces = " " * (width - len(line) - 2)
                report += "{0} {1}{2} {0}\n".format(V_CH, line, right_spaces)

        report += dashes
        return report


class _ErrorReport:
    def __init__(self, chunk: str = None, border_ch: str = "|") -> None:
        self.report_lines: List[_ErrorReportLine] = []
        self.border_ch = border_ch
        if chunk is not None:
            self._add_chunk(chunk)

    def __str__(self) -> str:
        self._close_borders()
        return "".join(rl.line + rl.newlines for rl in self.report_lines)

    def __iadd__(self, chunk: str) -> "_ErrorReport":
        self._add_chunk(chunk)
        return self

    def _add_chunk(self, chunk: str) -> None:
        if not chunk:
            return

        chunk_split = chunk.split("\n")
        for i, line in enumerate(chunk_split):
            if len(chunk_split) == 1 or i < len(chunk_split) - 1:
                if self.report_lines:
                    self.report_lines[-1].newlines += "\n"
                else:
                    rline = _ErrorReportLine("", "")
                    self.report_lines.append(rline)

            if line:
                rline = _ErrorReportLine(line, "")
                self.report_lines.append(rline)

    def _close_borders(self) -> None:
        for i, rline in enumerate(self.report_lines[:]):
            V_CH = self.border_ch
            if not rline.line:
                continue

            self.report_lines[i].line = V_CH + rline.line[1:-1] + V_CH

        V_CH = "+"  # report box corners
        for i, inc in [(0, 1), (-1, -1)]:
            j = i
            while (
                0 <= j < len(self.report_lines)
                and not self.report_lines[j].line
            ):
                j += inc

            rline = self.report_lines[j]
            self.report_lines[j].line = V_CH + rline.line[1:-1] + V_CH


class _ErrorReportLine:
    def __init__(self, line: str, newlines: str) -> None:
        self.line = line
        self.newlines = newlines

    def __str__(self) -> str:
        return "{}(line={!r}, newlines={!r})".format(
            cname(self), self.line, self.newlines
        )


def _tb_or_repr(e: BaseException, width: int) -> str:
    if isinstance(e, BugyiError):
        return e._repr(width=width)
    else:
        tb = getattr(e, "__traceback__", None)
        if tb is not None:
            estring = "".join(traceback.format_exception(type(e), e, tb))
        else:
            estring = repr(e)
        return estring


def chain_errors(e1: E, e2: Optional[Exception]) -> E:
    """Chain two exceptions together.

    This is the functional equivalent to ``raise e1 from e2``.

    Args:
        e1: An exception.
        e2: The exception we want to chain to ``e2``.

    Returns:
        ``e1`` after chaining ``e2`` to it.
    """
    e: BaseException = e1
    cause = e.__cause__
    while cause:
        e = cause
        cause = e.__cause__
    e.__cause__ = e2
    return e1
