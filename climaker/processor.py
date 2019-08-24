from typing import Any


class ProcessorFn:
    """
    Argument processor.
    Each argument for given option/positional is passed to processor function.

    """

    def __call__(self, value: str) -> Any: ...
