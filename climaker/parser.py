import argparse
from typing import Sequence

from .action import Action
from .spec import *
from .parser_builder import make_command_parser


__all__ = [
    'ArgumentParser',
]


class ArgumentParser:
    """Argument parser."""

    _command: Command
    _parser: argparse.ArgumentParser

    def __init__(self, command: Command):
        self._command = command
        self._parser = make_command_parser(self._command)

    def parse_arguments(self, args: Sequence[str]) -> Action:
        """
        Returns Action object with command name and its arguments.
        """

        parsed = self._parser.parse_args(args)
        action = _make_action(parsed)
        return action


def _make_action(parsed) -> Action:
    kwargs = {}
    command = list(getattr(parsed, '_command_parts_'))
    for key, value in parsed.__dict__.items():
        if not key.startswith('_'):
            kwargs[key] = value

    return Action(command, kwargs)
