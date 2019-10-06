from io import StringIO
from typing import Iterable, List, Optional

from climaker.interface import IDialect

from climaker.spec import Command
from climaker.tokens import Token
from climaker.util import get_words

from .tokenizer import DefaultLinuxTokenizer


class DefaultLinuxDialect(IDialect[Command, Token]):

    def tokenize(self, args: Iterable[str]) -> List[Token]:
        tokenizer = DefaultLinuxTokenizer()
        return tokenizer.tokenize_args(args)

    def format_help(self, command: Command, subcommand_path: Iterable[str] = (),
                    error: Optional[str] = None, short: bool = False) -> str:

        help_ = StringIO()

        if error:
            help_.write(f'Error: {error}\n\n')

        help_.writelines([
            'Arguments:',
            '# TODO',
        ])

        return help_.getvalue()

    def format_flag(self, identifier_name: str) -> str:
        if len(identifier_name) == 1:
            return '-{}'.format(identifier_name)
        else:
            return '--{}'.format(
                '-'.join(get_words(identifier_name))
            )

    def format_word(self, identifier_name: str) -> str:
        return '_'.join(get_words(identifier_name)).upper()
