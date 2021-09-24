"""Helper functions for command-line argument parsing."""

import argparse
from dataclasses import dataclass
import inspect
import sys
from typing import Any, Callable, Iterable, Sequence, TypeVar

from loguru import logger as log

from .types import Protocol


_T = TypeVar("_T")


class MainType(Protocol):
    """Type of the `main()` function returned by `main_factory()`."""

    def __call__(self, argv: Sequence[str] = None) -> int:
        """This method captures the `main()` function's signature."""


def main_factory(
    parse_cli_args: Callable[[Sequence[str]], _T], run: Callable[[_T], int]
) -> MainType:
    """
    Returns a generic main() function to be used as a script's entry point.
    """
    from .logging import configure as configure_logging
    from .meta import scriptname

    def main(argv: Sequence[str] = None) -> int:
        if argv is None:
            argv = sys.argv

        args = parse_cli_args(argv)

        debug: bool = getattr(args, "debug", False)
        verbose: int = getattr(args, "verbose", 0)
        name = scriptname(up=1)

        configure_logging(name, debug=debug, verbose=verbose)

        log.trace("Trace mode has been enabled.")
        log.debug("args = {!r}", args)

        try:
            status = run(args)
        except KeyboardInterrupt:
            print("Received SIGINT signal. Terminating {}...".format(name))
            return 0
        except Exception:
            log.exception(
                "An unrecoverable error has been raised. Terminating {}...",
                name,
            )
            return 1
        else:
            return status

    return main


@dataclass(frozen=True)
class Arguments:
    """Default CLI arguments corresponding to ``ArgumentParser``."""

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


class NewCommand(Protocol):
    """Type of the function returned by `new_command_factory()`."""

    def __call__(
        self,
        name: str,
        *,
        help: str,  # pylint: disable=redefined-builtin
        **kwargs: Any,
    ) -> argparse.ArgumentParser:
        """This method captures the `new_command()` function's signature."""


def new_command_factory(
    parser: argparse.ArgumentParser,
    *,
    dest: str = "command",
    required: bool = True,
    description: str = None,
    **kwargs: Any,
) -> NewCommand:
    """Returns a `new_command()` function that can be used to add subcommands.

    Args:
        parser: The argparse parser that we want to add subcommands to.
        dest: The attribute name that the subcommand name will be stored under
          inside the Namespace object.
        required: Will this subcommand be required or optional?
        description: This argument describes what the subcommand is used for.
        kwargs: These keyword arguments are relayed to the
          ``parser.add_subparsers()`` function call.
    """
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
