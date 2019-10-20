from __future__ import annotations

from typing import Generic, TypeVar, Iterable

from climaker.types import CliError
from climaker.argdef import Command
from climaker.dialect import IDialect
from climaker.composer import IComposer
from climaker.util import Result, Err, Ok


__all__ = [
    'ArgumentParser',
]


T = TypeVar('T')


class ArgumentParser(Generic[T]):
    """
    This is a frontend to climaker argument parsing implementation.

    """

    _command: Command
    _dialect: IDialect
    _composer: IComposer[T]

    def __init__(self,
                 command: Command,
                 dialect: IDialect,
                 composer: IComposer[T]):
        self._command = command
        self._dialect = dialect
        self._composer = composer

    def parse(self, args: Iterable[str]) -> Result[T, CliError]:
        raw_parse_result = self._dialect.parse(self._command, args)
        if raw_parse_result.is_err():
            return Err(raw_parse_result.unwrap_err())

        arg_tree = raw_parse_result.unwrap()
        composed_args = self._composer.compose(arg_tree)

        return Ok(composed_args)
