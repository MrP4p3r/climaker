from typing import Any, Optional, Mapping

from climaker.util import Result, Err, Ok
from climaker.types import ArgTree, CliError
from climaker.argdef import Command


__all__ = [
    'Finalizer',
]


class Finalizer:

    def finalize(self, command: Command, arg_tree: ArgTree) -> Result[ArgTree, CliError]:
        result = self._finalize_args(command, arg_tree.args)
        if result.is_err():
            return Err(result.unwrap_err())

        finalized_args = result.unwrap()

        finalized_child: Optional[ArgTree] = None
        if arg_tree.child:
            subcommand = command.get_subcommand(arg_tree.child.name)
            child_result = self.finalize(subcommand, arg_tree.child)
            if child_result.is_err():
                return Err(SubcommandError(child_result.unwrap_err()))

            finalized_child = child_result.unwrap()

        return Ok(ArgTree(
            name=arg_tree.name,
            args=finalized_args,
            child=finalized_child,
        ))

    def _finalize_args(self, command: Command, args: Mapping[str, Any]) -> Result[Mapping[str, Any], CliError]:
        # TODO
        return Ok(args)
