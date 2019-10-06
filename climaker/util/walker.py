from typing import Generic, TypeVar, Optional, Sequence


__all__ = [
    'Walker',
]


X = TypeVar('X')


class Walker(Generic[X]):

    def __init__(self, items: Sequence[X]):
        self._items = items
        self._current_index = -1

    def lookup(self) -> Optional[X]:
        if self._has_next():
            return self._items[self._current_index + 1]

    def next(self) -> Optional[X]:
        if self._has_next():
            self._current_index += 1
            return self._items[self._current_index]

    def current(self) -> Optional[X]:
        if self._current_index != -1:
            return self._items[self._current_index]

    def _has_next(self) -> bool:
        return self._current_index + 1 < len(self._items)
