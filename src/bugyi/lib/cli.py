"""Helper functions for command-line argument parsing."""

import argparse
from dataclasses import dataclass
import inspect
from typing import Any, Iterable

from .types import Protocol


@dataclass(frozen=True)
class Arguments:
    debug: bool
    verbose: int


def ArgumentParser(
    *args: Any, description: Any = None, **kwargs: Any
) -> argparse.ArgumentParser:
    """Wrapper for argparse.ArgumentParser."""
    if description is None:
        try:
            frame = inspect.stack()[1].frame
            description = frame.f_globals["__doc__"]
        except KeyError:
            pass

    if kwargs.get("formatter_class") is None:
        kwargs["formatter_class"] = _HelpFormatter

    parser = argparse.ArgumentParser(  # type: ignore
        *args, description=description, **kwargs
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debugging mode. DEPRECIATED: Use --verbose instead.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help=(
            "How verbose should the output be? This option can be specified"
            " multiple times (e.g. -v, -vv, -vvv, ...)."
        ),
    )

    return parser


class _HelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Custom argparse.HelpFormatter that uses raw descriptions and sorts optional
    arguments alphabetically.
    """

    def add_arguments(self, actions: Iterable[argparse.Action]) -> None:
        actions = sorted(actions, key=_argparse_action_key)
        super().add_arguments(actions)


def _argparse_action_key(action: argparse.Action) -> str:
    opts = action.option_strings
    if opts:
        return opts[-1].lstrip("-")
    else:
        return action.dest


class _NewCommand(Protocol):
    def __call__(
        self,
        name: str,
        *,
        help: str,  # pylint: disable=redefined-builtin
        **kwargs: Any,
    ) -> argparse.ArgumentParser:
        pass


def new_command_factory(
    parser: argparse.ArgumentParser,
    *,
    dest: str = "command",
    required: bool = True,
    description: str = None,
    **kwargs: Any,
) -> _NewCommand:
    subparsers = parser.add_subparsers(
        dest=dest, required=required, description=description, **kwargs
    )

    def new_command(
        name: str,
        *,
        help: str,  # pylint: disable=redefined-builtin
        **inner_kwargs: Any,
    ) -> argparse.ArgumentParser:
        return subparsers.add_parser(
            name,
            formatter_class=parser.formatter_class,
            help=help,
            description=help,
            **inner_kwargs,
        )

    return new_command
