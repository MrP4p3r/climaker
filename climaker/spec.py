"""Parser specification objects"""

from typing import Union, Dict, List


__all__ = ['Arg', 'Arguments', 'Subcommands']


class Arg(object):

    def __init__(self, *aliases, type_=str, default=None, required=None, arg_type='value', description=None):
        self.aliases = aliases
        self.type = type_
        self.default = default
        self.required = required
        self.arg_type = arg_type
        self.description = description


class Arguments(object):

    def __init__(self, arguments: List[Arg]):
        self.arguments = arguments


class Subcommands(object):

    def __init__(self, subcommands: Dict[str, Union[Arguments, 'Subcommands']]):
        self.subcommands = subcommands
