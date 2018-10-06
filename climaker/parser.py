"""Parser itself"""

from typing import List
from argparse import ArgumentParser

from .action import Action
from .spec import Arguments, Subcommands


__all__ = ['Parser']


class Parser(object):
    """
    Parser object.
    Builds argparse parser by provided specification and performs argument parsing.
    """

    def __init__(self, spec, prog=None):
        self.spec = spec
        self.prog = prog
        self._parser = _make_parser(self.spec, prog)

    def parse_arguments(self, args: List[str]) -> Action:
        """
        Returns Action object with command name and its arguments.
        """

        if len(args) == 0:
            self._parser.error('No arguments specified.')

        parsed = self._parser.parse_args(args)
        action = _make_action(parsed)
        return action


def _make_parser(spec, prog) -> ArgumentParser:
    parser = ArgumentParser(prog=prog)
    parser.set_defaults(_command_parts_=[])
    _dispatch(spec, parser)
    return parser


def _dispatch(spec, parser):
    if isinstance(spec, Subcommands):
        return _create_subcommands_parser(spec, parser)
    elif isinstance(spec, Arguments):
        return _create_arguments_parser(spec, parser)
    else:
        raise ValueError(f'Unknown spec: {spec}')


def _create_subcommands_parser(spec: Subcommands, parent: ArgumentParser):
    subparsers = parent.add_subparsers()
    for cmd_name, sub_spec in spec.subcommands.items():
        parser = subparsers.add_parser(cmd_name)
        command_parts = parent.get_default('_command_parts_')
        parser.set_defaults(_command_parts_=command_parts + [cmd_name])
        _dispatch(sub_spec, parser)


def _create_arguments_parser(spec: Arguments, parent: ArgumentParser):
    for arg_spec in spec.arguments:
        if arg_spec.arg_type == 'value':
            kwargs = dict(
                default=arg_spec.default,
                type=arg_spec.type,
                help=arg_spec.description,
            )
            if arg_spec.required is not None:
                kwargs['required'] = arg_spec.required
        elif arg_spec.arg_type == 'flag':
            kwargs = dict(
                default=arg_spec.default,
                action='store_const',
                const=not arg_spec.default,
            )
        else:
            raise ValueError(f'Unknown arg_type: {arg_spec.arg_type}')

        parent.add_argument(*arg_spec.aliases, **kwargs)


def _make_action(parsed) -> Action:
    kwargs = {}
    command = list(getattr(parsed, '_command_parts_'))
    for key, value in parsed.__dict__.items():
        if not key.startswith('_'):
            kwargs[key] = value

    return Action(command, kwargs)
