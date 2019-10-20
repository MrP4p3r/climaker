from abc import abstractmethod
from typing import Protocol


from climaker.argdef import Command
from climaker.types import CliError, ArgTree
from climaker.util import Result

__all__ = [
    'IFinalizer',
]


class IFinalizer(Protocol):
    """
    Parsing result finalizer.

    Purpose:
        Ensure completeness of arg tree (i. e. check
        for missing args, set defaults and so on).

    """

    @abstractmethod
    def finalize(self, command: Command, arg_tree: ArgTree) -> Result[ArgTree, CliError]: ...
