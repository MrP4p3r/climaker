from abc import abstractmethod
from typing import Any


__all__ = [
    'ProcessorFn',
    'ArgReducer',
]


class ProcessorFn:
    """
    Argument processor.
    Each argument for given option/positional is passed to processor function.

    """

    @abstractmethod
    def __call__(self, value: str) -> Any: ...


class ArgReducer:

    @abstractmethod
    def __call__(self, accumulator: Any, value: str) -> Any: ...
