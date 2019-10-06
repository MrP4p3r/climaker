from typing import Generic, Iterable
from abc import abstractmethod
from .typevars import TToken, TParseResult


__all__ = [
    'IParser',
]


class IParser(Generic[TToken, TParseResult]):

    @abstractmethod
    def parse(self, tokens: Iterable[TToken]) -> TParseResult:
        ...
