from abc import abstractmethod
from typing import Generic, TypeVar

from .dialect import IDialect


__all__ = [
    'IFinalizer',
]


P = TypeVar('P')
R = TypeVar('R')


class IFinalizer(Generic[P, R]):
    """
    Parsing result finalizer.

    """

    @abstractmethod
    def finalize(self, parsing_result: P, dialect: IDialect) -> R: ...
