from typing import Final
from climaker.types import CliError, ParsingError


__all__ = [
    'UnknownSubcommand',
    'SubcommandParsingError',
    'FailedWithException',
    'ExpectedOptionValue',
    'UnexpectedFlagOpt',
    'UnexpectedPositional',
    'UnexpectedAssignment',
]


class UnknownSubcommand(ParsingError):

    subcommand_name: Final[str]

    def __init__(self, subcommand_name: str):
        self.subcommand_name = subcommand_name


class SubcommandParsingError(ParsingError):

    subcommand_name: Final[str]
    error: Final[CliError]

    def __init__(self, subcommand_name: str, error: CliError):
        self.subcommand_name = subcommand_name
        self.error = error


class FailedWithException(ParsingError):

    exception: Final[BaseException]

    def __init__(self, exception: BaseException):
        self.exception = exception


class UnexpectedFlagOpt(ParsingError):

    flag: Final[str]

    def __init__(self, flag: str):
        self.flag = flag


class ExpectedOptionValue(ParsingError):

    flag: Final[str]
    found: Final[str]

    def __init__(self, flag: str, found: str):
        self.flag = flag
        self.found = found


class UnexpectedAssignment(ParsingError):

    assignment: Final[str]

    def __init__(self, assignment: str):
        self.assignment = assignment


class UnexpectedPositional(ParsingError):

    positional: Final[str]

    def __init__(self, positional):
        self.positional = positional
