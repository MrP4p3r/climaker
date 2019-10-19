from typing import Generic, TypeVar, Sequence


__all__ = [
    'IArgumentParser',
]


R = TypeVar('R')  # Result type


class IArgumentParser(Generic[R]):

    def parse(self, args: Sequence[str]) -> R:
        ...
