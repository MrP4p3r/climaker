from typing import Any, Optional, Mapping, Sequence

from climaker.util import Result, Err, Ok
from climaker.types import ArgTree
from climaker.argdef import Command, ArgPos, ArgFlag, ArgOpt, missing

from .errors import *


__all__ = [
    'Finalizer',
]


class Finalizer:

    def finalize(self, command: Command, arg_tree: ArgTree) -> Result[ArgTree, ParsingError]:
        result = self._finalize_args(command, arg_tree.args)
        if result.is_err():
            return Err(result.unwrap_err())

        finalized_args = result.unwrap()

        finalized_child: Optional[ArgTree] = None
        if arg_tree.child:
            subcommand = command.get_subcommand(arg_tree.child.name)
            child_result = self.finalize(subcommand, arg_tree.child)
            if child_result.is_err():
                return Err(SubcommandFinalizationError(child_result.unwrap_err()))

            finalized_child = child_result.unwrap()

        return Ok(ArgTree(
            name=arg_tree.name,
            args=finalized_args,
            child=finalized_child,
        ))

    def _finalize_args(self, command: Command, args: Mapping[str, Any]) -> Result[Mapping[str, Any], ParsingError]:
        finalized_args = {}

        for arg in command.arguments:
            if arg.name in args:
                result = self._finalize_values(arg, args[arg.name])
                if result.is_err():
                    return result

                finalized_args[arg.name] = result.unwrap()
            else:
                result = self._get_default(arg)
                if result.is_err():
                    return result

                finalized_args[arg.name] = result.unwrap()

        # TODO: Add type check?

        return Ok(finalized_args)

    def _finalize_values(self, arg: BaseArg, arg_values: Sequence[str]) -> Result[Any, ParsingError]:
        min_values, max_values = arg.reducer.get_value_number_range()
        if min_values > len(arg_values):
            return Err(InsufficientArgumentValues(arg.name, min_values))

        if max_values is not None and max_values < len(arg_values):
            return Err(TooManyArgumentValues(arg.name, max_values))

        return Ok(arg.reducer.reduce(arg_values))

    def _get_default(self, arg: BaseArg) -> Result[Any, ParsingError]:
        if isinstance(arg, ArgFlag):
            return Ok(arg.default)
        elif isinstance(arg, (ArgPos, ArgOpt)):
            default = arg.default
            if default is missing:
                return Err(MissingArg(arg))

            return Ok(default)
