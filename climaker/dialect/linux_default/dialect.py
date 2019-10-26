from typing import Iterable, Sequence

from climaker.types import CliError
from climaker.argdef import Command
from climaker.util import get_words

from ..base import BaseDialect
from ..shared import Token
from .tokenizer import DefaultLinuxTokenizer


class DefaultLinuxDialect(BaseDialect):

    def format_help(self, command: Command, subcommand: str) -> str:
        # TODO
        return f'Usage: {command.name} ...'

    def format_error(self, cli_error: CliError) -> str:
        # TODO
        return f'Error: {cli_error!r}'

    def _tokenize(self, command: Command, args: Iterable[str]) -> Sequence[Token]:
        return DefaultLinuxTokenizer().tokenize_args(args)

    @staticmethod
    def _format_flag(identifier_name: str) -> str:
        if len(identifier_name) == 1:
            return '-{}'.format(identifier_name)
        else:
            return '--{}'.format(
                '-'.join(get_words(identifier_name))
            )

    @staticmethod
    def _format_word(identifier_name: str) -> str:
        return '_'.join(get_words(identifier_name)).upper()
