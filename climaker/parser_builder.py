import argparse
from functools import singledispatch
from typing import Optional, List

from .spec import *


__all__ = [
    'make_command_parser',
    'COMMAND_PARTS_KEY',
]


_SubParsersAction = argparse._SubParsersAction  # noqa


COMMAND_PARTS_KEY = '_command_parts_'


def make_command_parser(command: Command,
                        _subparsers: Optional[_SubParsersAction] = None,
                        _command_parts: Optional[List[str]] = None
                        ) -> argparse.ArgumentParser:

    if _subparsers is not None:
        parser = _subparsers.add_parser(name=command.name, description=command.description)
        parser.set_defaults(**{COMMAND_PARTS_KEY: _command_parts + [command.name]})
    else:
        parser = argparse.ArgumentParser(prog=command.name, description=command.name)
        parser.set_defaults(**{COMMAND_PARTS_KEY: []})

    if command.is_subcommands_group():
        subparsers = parser.add_subparsers()
        for subcommand in command.subcommands:
            make_command_parser(subcommand,
                                _subparsers=subparsers,
                                _command_parts=parser.get_default(COMMAND_PARTS_KEY))
    else:
        for argument in command.arguments:
            _add_argument(argument, parser)

    return parser


@singledispatch
def _add_argument(_argument: BaseArg, _parser: argparse.ArgumentParser): ...


@_add_argument.register(ArgPos)
def _(argument: ArgPos, parser: argparse.ArgumentParser):
    # TODO: handle type, choices, processor and reducer
    # TODO: required is not valid argument for positionals
    parser.add_argument(
        argument.name, metavar=argument.help_name,
        default=argument.default,
        help=argument.description,
        type=argument.type,
    )


@_add_argument.register(ArgOpt)
def _(argument: ArgOpt, parser: argparse.ArgumentParser):
    # TODO: handle type, choices, processor and reducer
    parser.add_argument(
        *argument.aliases, dest=argument.name,
        default=argument.default, required=(argument.default is None),
        type=argument.type,
        help=argument.description,
    )


@_add_argument.register(ArgFlag)
def _(argument: ArgFlag, parser: argparse.ArgumentParser):
    parser.add_argument(
        *argument.aliases, dest=argument.name,
        default=argument.default, required=(argument.default is None),
        action='store_const', const=argument.set_value,
        type=argument.type,
        help=argument.description,
    )
