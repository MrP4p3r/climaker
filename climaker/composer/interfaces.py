from __future__ import annotations

from typing import Protocol, TypeVar
from climaker.types import ArgTree


__all__ = [
    'IComposer',
]


T = TypeVar('T')


class IComposer(Protocol[T]):
    """
    Composes ArgTree into some result suitable for client code.

    """

    def compose(self, arg_tree: ArgTree) -> T: ...
