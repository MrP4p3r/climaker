from typing import Optional, Sequence
from climaker.tokenizer import Token


__all__ = [
    'TokenWalker',
]


class TokenWalker:

    def __init__(self, tokens: Sequence[Token]):
        self._tokens = tokens
        self._current_index = -1

    def lookup(self) -> Optional[Token]:
        if self._has_next():
            return self._tokens[self._current_index + 1]

    def next(self) -> Optional[Token]:
        if self._has_next():
            self._current_index += 1
            return self._tokens[self._current_index]

    def _has_next(self) -> bool:
        return self._current_index + 1 < len(self._tokens)
