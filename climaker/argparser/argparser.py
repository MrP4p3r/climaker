from __future__ import annotations

from typing import Generic, TypeVar, Sequence

from climaker.interface import IArgumentParser, IDialect, IParser, IFinalizer
from climaker.argdef import Command
from climaker.tokens import Token
from climaker.dialect import DefaultLinuxDialect
from climaker.parser import TokenParser, TokenParsingResult
from climaker.finalizer import MergedArgs, MergingFinalizer


__all__ = [
    'ArgumentParser',
    'ParserFactoryFn',
    'make_default_argument_parser',
]


C = TypeVar('C')
T = TypeVar('T')
P = TypeVar('P')
R = TypeVar('R')


class ParserFactoryFn(Generic[T, P]):
    def __call__(self) -> IParser[T, P]: ...


class ArgumentParser(IArgumentParser[R], Generic[C, T, P, R]):
    """
    This is a frontend to climaker argument parsing implementation.

    """

    _command: C
    _dialect: IDialect[C, T]
    _parser_factory: ParserFactoryFn[T, P]
    _finalizer: IFinalizer[P, R]

    def __init__(self, command: C,
                 dialect: IDialect[C, T],
                 parser_factory: ParserFactoryFn[T, P],
                 finalizer: IFinalizer[P, R]):
        self._command = command
        self._dialect = dialect
        self._parser_factory = parser_factory
        self._finalizer = finalizer

    def parse(self, args: Sequence[str]) -> R:
        tokens = self._dialect.tokenize(args)
        token_parser = self._parser_factory()
        parsing_result = token_parser.parse(tokens)
        return self._finalizer.finalize(parsing_result, self._dialect)


def make_default_argument_parser(command: Command) -> IArgumentParser[MergedArgs]:
    dialect: IDialect[Command, Token] = DefaultLinuxDialect()
    parser_factory: ParserFactoryFn[Token, TokenParsingResult] = lambda: TokenParser(command)
    finalizer: IFinalizer[TokenParsingResult, MergedArgs] = MergingFinalizer()
    return ArgumentParser(command, dialect, parser_factory, finalizer)
