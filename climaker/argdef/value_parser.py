from typing import TypeVar, Protocol, Tuple, Optional
from .interfaces import IValueParser


__all__ = [
    'FnParser',
]


V = TypeVar('V')


class _VarArgFn(Protocol[V]):

    def __call__(self, *args: str) -> V: ...


class FnParser(IValueParser[V]):

    def __init__(self, function: _VarArgFn[V], min_words: int = 1, max_words: Optional[int] = 1):
        assert 0 <= min_words
        assert max_words is None or min_words <= max_words
        self._function = function
        self._min_words = min_words
        self._max_words = max_words

    def get_word_number_range(self) -> Tuple[int, Optional[int]]:
        return self._min_words, self._max_words

    def parse(self, *args: str) -> V:
        return self._function(*args)
