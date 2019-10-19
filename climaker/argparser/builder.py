from __future__ import annotations

from typing import Generic, TypeVar, Optional, Callable

from climaker.interface import IDialect, IParser, IFinalizer
from .argparser import ArgumentParser


C = TypeVar('C')
T = TypeVar('T')
P = TypeVar('P')
R = TypeVar('R')

X = TypeVar('X')
Y = TypeVar('Y')


class ArgumentParserBuilder(Generic[C, T, P, R]):

    _dialect: Optional[IDialect[C, T]]
    _parser_factory: Optional[Callable[[], IParser[T, P]]]
    _finalizer: Optional[IFinalizer[P, R]]

    def __init__(self):
        self._dialect = None
        self._parser = None
        self._finalizer = None

    def with_finalizer(self,
                       finalizer: IFinalizer[X, Y]) -> ArgumentParserBuilder[C, T, X, Y]:
        self._finalizer = finalizer
        return self

    def with_parser(self, parser_factory: Callable[[], IParser[X, P]]) -> ArgumentParserBuilder[C, X, P, R]:
        self._parser_factory = parser_factory
        return self

    def with_dialect(self, dialect: IDialect[X, T]) -> ArgumentParserBuilder[X, T, P, R]:
        self._dialect = dialect
        return self

    def build(self, command: C) -> ArgumentParser[R]:
        assert self._dialect is not None
        assert self._parser_factory is not None
        assert self._finalizer is not None
        return ArgumentParser(
            command,
            self._dialect,
            self._parser_factory,
            self._finalizer
        )


from climaker.argdef import Command

