from __future__ import annotations

from typing import Protocol, Iterable

from climaker.util import Result
from climaker.argdef import Command
from climaker.types import CliError, ArgTree


__all__ = [
    'IDialect',
]


class IDialect(Protocol):
    """
    CLI dialect.

    Purpose:
        - Parse dialect specific set of arguments into :class:`ArgTree`.
        - Format help message in a dialect specific format.
        - Format error message in a dialect specific format.

    """

    def parse(self, command: Command, args: Iterable[str]) -> Result[ArgTree, CliError]: ...

    def format_help(self, command: Command, subcommand: str) -> str: ...

    def format_error(self, cli_error: CliError) -> str: ...
