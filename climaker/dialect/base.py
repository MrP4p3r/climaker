from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from climaker.argdef import Command
from climaker.types import ArgTree, CliError
from climaker.util import Result, Ok, Err

from .shared import Token, TokenParser, Finalizer
from .interfaces import IDialect


__all__ = [
    'BaseDialect',
]


class BaseDialect(IDialect, ABC):

    def parse(self, command: Command, args: Iterable[str]) -> Result[ArgTree, CliError]:
        tokens = self._tokenize(command, args)

        parser = TokenParser(command)
        parser_result = parser.parse(tokens)
        if parser_result.is_err():
            return Err(parser_result.unwrap_err())

        raw_arg_tree = parser_result.unwrap()
        finalizer = Finalizer()
        finalizer_result = finalizer.finalize(command, raw_arg_tree)
        if finalizer_result.is_err():
            return Err(finalizer_result.unwrap_err())

        return Ok(finalizer_result.unwrap())

    @abstractmethod
    def format_help(self, command: Command, subcommand: str) -> str: ...

    @abstractmethod
    def format_error(self, cli_error: CliError) -> str: ...

    @abstractmethod
    def _tokenize(self, command: Command, args: Iterable[str]) -> Sequence[Token]: ...
