from typing import Generic, TypeVar, Sequence
from abc import abstractmethod


__all__ = [
    'IParser',
]


T = TypeVar('T')  # Token type
P = TypeVar('P')  # Parsing result


class IParser(Generic[T, P]):

    @abstractmethod
    def parse(self, tokens: Sequence[T]) -> P:
        ...
