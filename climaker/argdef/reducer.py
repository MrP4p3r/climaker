from typing import Any
from .interfaces import ArgReducer


__all__ = [
    'singleargument',
    'multipleargument',
    'countargument',
]


def singleargument() -> ArgReducer:

    def reducer(accumulator: Any, value: str) -> Any:
        if accumulator is not None:
            raise TypeError('Multiple arguments are not allowed')
        return value

    return reducer


def multipleargument(max_args: int = -1) -> ArgReducer:

    def reducer(accumulator: Any, value: str) -> Any:
        if accumulator is None:
            return [value]
        if 0 < max_args < len(accumulator):
            raise TypeError(f'More than {max_args} not allowed')
        return accumulator + [value]

    return reducer


def countargument(max_count: int = -1) -> ArgReducer:

    def reducer(accumulator: Any, _value: str) -> Any:
        if accumulator is None:
            return 1
        if 0 < max_count < accumulator:
            raise TypeError(f'More than {max_count} not allowed')
        return accumulator + 1

    return reducer
