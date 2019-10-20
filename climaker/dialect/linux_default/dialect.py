from typing import Iterable

from climaker.types import CliError, ArgTree
from climaker.argdef import Command
from climaker.dialect import IDialect
from climaker.dialect.shared import TokenParser
from climaker.util import Result, Ok, get_words

from .tokenizer import DefaultLinuxTokenizer


class DefaultLinuxDialect(IDialect):

    def parse(self, command: Command, args: Iterable[str]) -> Result[ArgTree, CliError]:
        tokenizer = DefaultLinuxTokenizer()
        tokens = tokenizer.tokenize_args(args)

        parser = TokenParser(command)
        return Ok(parser.parse(tokens))

    def format_help(self, command: Command, subcommand: str) -> str:
        # TODO
        return f'Usage: {command.name} ...'

    def format_error(self, cli_error: CliError) -> str:
        # TODO
        return f'Error: {cli_error!r}'

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
