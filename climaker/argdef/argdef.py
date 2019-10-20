from __future__ import annotations

from typing import (
    TypeVar, Type,
    Any, Union, Optional,
    Iterable, Sequence, List,
)

from .interfaces import ProcessorFn, ArgReducer
from .reducer import singleargument


__all__ = [
    'Command',
    'BaseArg', 'ReducerMixin',
    'ArgPos', 'ArgOpt', 'ArgFlag',
    'get_name_from_aliases',
    'MISSING',
]


TypingType = TypeVar('TypingType')
MISSING = object()
ArgDefaultType = Union[str, TypingType, 'Literal[MISSING]']


class Command:

    _name: str
    _subcommands: Optional[List[Command]]
    _arguments: Optional[List[BaseArg]]
    _description: Optional[str]

    def __init__(self,
                 name: str,
                 *,
                 arguments: Optional[List[BaseArg]] = None,
                 subcommands: Optional[List[Command]] = None,
                 description: Optional[str] = None
                 ):

        self._name = name
        self._subcommands = subcommands or []
        self._arguments = arguments or []
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def subcommands(self) -> Sequence[Command]:
        if self._subcommands is None:
            raise TypeError('Command is not a subcommands group')
        return self._subcommands

    @property
    def arguments(self) -> Sequence[BaseArg]:
        if self._arguments is None:
            raise TypeError('Command is not an arguments group')
        return self._arguments

    @property
    def description(self) -> Optional[str]:
        return self._description

    def has_subcommands(self) -> bool:
        return bool(self._subcommands)


class BaseArg:

    _name: str
    _type: TypingType
    _processor: ProcessorFn
    _description: Optional[str]

    def __init__(self,
                 name: str,
                 type_: TypingType,
                 processor: ProcessorFn,
                 description: Optional[str],
                 ):
        self._name = name
        self._type = type_
        self._processor = processor or str
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> TypingType:
        return self._processor

    @property
    def processor(self) -> ProcessorFn:
        return self._processor

    @property
    def description(self) -> Optional[str]:
        return self._description


class ReducerMixin:

    __reducer: Optional[ArgReducer]

    def __init__(self):
        self.__reducer = None

    def _set_reducer(self, reducer: Optional[ArgReducer] = None):
        self.__reducer = reducer or singleargument()

    def reducer(self, acc: Any, value: str) -> Any:
        assert self.__reducer is not None, f'Reducer is not set for {type(self).__name__}'
        return self.__reducer(acc, value)


class ArgPos(BaseArg, ReducerMixin):

    _default: Any
    _help_name: str
    _choices: Iterable[str]

    def __init__(self,
                 name: str, *,
                 type_: Type[TypingType] = str,
                 processor: Optional[ProcessorFn] = None,
                 default: ArgDefaultType = MISSING,
                 help_name: Optional[str] = None,
                 description: Optional[str] = None,
                 choices: Optional[Iterable[str]] = None,
                 reducer: Optional[ArgReducer] = None,
                 ):

        super().__init__(name, type_, processor, description)
        self._set_reducer(reducer)

        self._default = default
        self._help_name = help_name or name
        self._choices = list(choices) if choices else None

    @property
    def default(self) -> Any:
        return self._default

    @property
    def help_name(self) -> str:
        return self._help_name

    @property
    def choices(self) -> Optional[Iterable[str]]:
        return self._choices


class ArgOpt(BaseArg, ReducerMixin):

    _default: Any
    _aliases: Iterable[str]
    _choices: Optional[Iterable[str]]

    def __init__(self,
                 name: str,
                 *aliases: str,
                 type_: TypingType = str,
                 processor: Optional[ProcessorFn] = None,
                 default: ArgDefaultType = MISSING,
                 description: Optional[str] = None,
                 choices: Optional[Iterable] = None,
                 reducer: Optional[ArgReducer] = None,
                 ):

        super().__init__(name, type_, processor, description)
        self._set_reducer(reducer)

        self._aliases = aliases
        self._default = default
        self._choices = list(choices) if choices else None

    @property
    def default(self) -> Any:
        return self._default

    @property
    def aliases(self) -> Iterable[str]:
        return self._aliases

    @property
    def choices(self) -> Optional[Iterable[str]]:
        return self._choices


class ArgFlag(BaseArg):

    _aliases: Iterable[str]
    _default: Any
    _set_value: Any

    def __init__(self,
                 name: str,
                 *aliases: str,
                 set_value: Any,
                 default: Any,
                 type_: TypingType = bool,
                 processor: Optional[ProcessorFn] = None,
                 description: Optional[str] = None,
                 ):

        super().__init__(name, type_, processor, description)
        self._aliases = aliases
        self._default = default
        self._set_value = set_value

    @property
    def aliases(self) -> Iterable[str]:
        return self._aliases

    @property
    def default(self) -> Any:
        return self._default

    @property
    def set_value(self) -> Any:
        return self._set_value


def get_name_from_aliases(aliases: Iterable[str]) -> str:
    longest_alias = max(aliases, key=len)
    name = longest_alias.lstrip('-').replace('-', '_').lower()
    return name
