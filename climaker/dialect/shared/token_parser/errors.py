from typing import Final
from climaker.types import CliError, ParsingError


__all__ = [
    'UnknownSubcommand',
    'SubcommandParsingError',
    'ParentCommandParsingError',
    'FailedWithException',
    'ExpectedOptionValue',
    'UnexpectedFlagOpt',
    'UnexpectedPositional',
    'UnexpectedAssignment',
    'InsufficientPositionalsNumber',
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


class ParentCommandParsingError(ParsingError):

    error: Final[CliError]

    def __init__(self, error: CliError):
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

    def __init__(self, positional: str):
        self.positional = positional


class InsufficientPositionalsNumber(ParsingError):

    argument_name: Final[str]
    min_required: Final[int]

    def __init__(self, argument_name: str, min_required: int):
        self.argument_name = argument_name
        self.min_required = min_required
