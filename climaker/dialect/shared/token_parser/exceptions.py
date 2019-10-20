from .tokens import Token, FlagToken, WordToken


__all__ = [
    'TokenParsingError',
    'UnexpectedFlagOptError',
    'ExpectedOptionValueError',
    'UnexpectedAssignmentError',
    'UnexpectedPositionalError',
    'UnknownSubcommandError',
    'SubcommandParsingError',
]


class TokenParsingError(BaseException):

    @property
    def message(self) -> str:
        return self.args[0]


class UnexpectedFlagOptError(TokenParsingError):

    def __init__(self, flag_token: FlagToken):
        super().__init__(f'Unexpected flag/option {flag_token!r}')
        self.flag_token = flag_token


class ExpectedOptionValueError(TokenParsingError):

    def __init__(self, flag_token: FlagToken, token_found: Token):
        super().__init__(f'Expected a value for option {flag_token!r}, found {token_found!r}')
        self.flag_token = flag_token
        self.token_found = token_found


class UnexpectedAssignmentError(TokenParsingError):

    def __init__(self, flag_token: FlagToken):
        super().__init__(f'Unexpected assignment in {flag_token!r}')
        self.flag_token = flag_token


class UnexpectedPositionalError(TokenParsingError):

    def __init__(self, word_token: WordToken):
        super().__init__(f'Unexpected positional argument {word_token!r}')
        self.word_token = word_token


class UnknownSubcommandError(TokenParsingError):

    def __init__(self, subcommand_name: str):
        super().__init__(f'Unknown subcommand {subcommand_name!r}')
        self.subcommand_name = subcommand_name


class SubcommandParsingError(TokenParsingError):

    def __init__(self, subcommand_name: str):
        super().__init__(f'Error while parsing subcommand {subcommand_name!r}')
        self.subcommand_name = subcommand_name
