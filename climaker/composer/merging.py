from dataclasses import dataclass
from typing import Any, Optional, Dict

from climaker.types import ArgTree
from climaker.composer import IComposer
from climaker.util import into_identifier


__all__ = [
    'MergedArgs',
    'MergingComposer',
]


@dataclass
class MergedArgs:
    """
    :ivar command_name:
        Command name "path" in `dot_separated.snake_case` string.
        E. g. `git stash pop` will be `git.stash.pop`.

    :ivar arguments:
        Dictionary with all parsed arguments.

    """

    command_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None


class MergingComposer(IComposer[MergedArgs]):
    """
    Finalizer that merges all arguments into single dictionary.

    """

    def compose(self, arg_tree: ArgTree) -> MergedArgs:
        arguments: Dict[str, Any] = {}

        command_name = into_identifier(arg_tree.name)
        if arg_tree.args:
            arguments.update(arg_tree.args)

        while arg_tree.child:
            arg_tree = arg_tree.child
            command_name += '.' + into_identifier(arg_tree.name)
            if arg_tree.args:
                arguments.update(arg_tree.args)

        return MergedArgs(command_name=command_name, arguments=arguments)
