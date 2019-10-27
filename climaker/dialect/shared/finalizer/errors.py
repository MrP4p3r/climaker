from typing import Generic, TypeVar, Final

from climaker.types import ParsingError
from climaker.argdef import BaseArg


class SubcommandFinalizationError(ParsingError):

    error: Final[ParsingError]

    def __init__(self, error: ParsingError):
        self.error = error


class InsufficientArgumentValues(ParsingError):

    argument_name: Final[str]
    min_required: Final[int]

    def __init__(self, argument_name: str, min_required: int):
        self.argument_name = argument_name
        self.min_required = min_required


class TooManyArgumentValues(ParsingError):

    argument_name: Final[str]
    max_required: Final[int]

    def __init__(self, argument_name: str, max_required: int):
        self.argument_name = argument_name
        self.max_required = max_required


TA = TypeVar('TA', bound=BaseArg, covariant=True)


class MissingArg(ParsingError, Generic[TA]):

    argument: TA

    def __init__(self, argument: TA):
        self.argument = argument
