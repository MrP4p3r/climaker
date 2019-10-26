from typing import TypeVar, Optional, Any, Callable, Tuple, Sequence
from .interfaces import IValueReducer


__all__ = [
    'BaseReducer',
    'FnReducer', 'TransformReducer',
    'single_arg', 'multiple_args', 'count_args',
]


A = TypeVar('A')
V = TypeVar('V')


class BaseReducer:

    def __init__(self, min_count: int = 1, max_count: Optional[int] = 1):
        assert 0 <= min_count
        assert max_count is None or min_count <= max_count
        self._min_count = min_count
        self._max_count = max_count

    def get_value_number_range(self) -> Tuple[int, Optional[int]]:
        return self._min_count, self._max_count


class FnReducer(BaseReducer, IValueReducer[V, A]):

    def __init__(self, function: Callable[[A, V], A],
                 initial_factory: Optional[Callable[..., A]] = None,
                 min_count: int = 1, max_count: Optional[int] = 1):
        super().__init__(min_count, max_count)
        self._function = function
        self._initial_factory = initial_factory

    def reduce(self, values: Sequence[V]) -> A:
        values_ = values
        if self._initial_factory:
            result = self._initial_factory()
        else:
            result, values_ = values[0], values_[1:]

        for value in values_:
            result = self._function(result, value)

        return result


class TransformReducer(BaseReducer, IValueReducer[V, A]):

    def __init__(self, function: Callable[[Sequence[V]], A],
                 min_count: int = 1, max_count: Optional[int] = 1):
        super().__init__(min_count, max_count)
        self._function = function

    def reduce(self, values: Sequence[V]) -> A:
        return self._function(values)


def single_arg() -> IValueReducer[A, V]:
    return FnReducer(
        lambda acc, v: v,
        initial_factory=lambda: None,
        min_count=1,
        max_count=1,
    )


def multiple_args(max_count: int = None,
                  transform_fn: Callable[[Sequence[V]], A] = list) -> IValueReducer[V, A]:
    return TransformReducer(transform_fn, max_count=max_count)


def count_args(max_count: int = None) -> IValueReducer[int, Any]:
    return FnReducer(
        lambda acc, v: acc + 1,
        initial_factory=int,
        min_count=0,
        max_count=max_count,
    )
