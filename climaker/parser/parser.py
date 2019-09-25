from __future__ import annotations
from typing import Optional, List, Union

from climaker.tokenizer import FlagToken, WordToken
from climaker.spec import Command, ArgOpt, ArgFlag, ArgPos

from .token_walker import TokenWalker


__all__ = [
    'TokenParser',
]


class TokenParser:

    def __init__(self, command: Command, parent: Optional[TokenParser] = None):
        self._command = command
        self._parent = parent

        self._positionals_stack = SpecOps.list_positionals(self._command)
        self._current_positional = None

        self._consumed = {}

    def consume(self, walker: TokenWalker):
        while walker.lookup():
            token = walker.next()
            if token.into_flag_stop():
                continue
            elif token.into_flag():
                self.consume_flag(token.into_flag(), walker)
            elif token.into_word():
                self.consume_word(token.into_word(), walker)

    def consume_flag(self, flag_token: FlagToken, walker: TokenWalker):
        alias = flag_token.get_name()
        flag_or_opt = self._get_flag_or_opt(alias)

        if not flag_or_opt:
            if not self._parent:
                raise ValueError(f'Unknown flag/option {alias!r}')
            else:
                self._parent.consume_flag(flag_token, walker)

        elif isinstance(flag_or_opt, ArgOpt):
            opt = flag_or_opt
            opt_value = flag_token.get_value()
            if opt_value is None:
                while walker.lookup() and walker.lookup().into_flag_stop():
                    walker.next()
                if not walker.lookup() or not walker.lookup().into_word():
                    raise ValueError(f'Expected a value for option {alias!r} ({opt.name!r})')
                word = walker.next().into_word()
                opt_value = word.get_value()

            self._consumed[opt.name] = opt.reducer(
                self._consumed.get(opt.name),
                opt.processor(opt_value),
            )

        elif isinstance(flag_or_opt, ArgFlag):
            flag = flag_or_opt
            if flag_token.get_value():
                raise ValueError(f'Unexpected value for flag {alias!r} ({flag.name!r})')

            self._consumed[flag.name] = flag.set_value

        else:
            raise TypeError('Totally unexpected error')

    def consume_word(self, word: WordToken, walker: TokenWalker):
        if self._command.has_subcommands():
            subcommand = self._get_subcommand(word.get_value())
            subconsumer = TokenParser(subcommand, self)
            subconsumer.consume(walker)
        else:
            positional: ArgPos = self._get_current_positional()
            if not positional:
                raise ValueError(f'Unexpected positional argument: {word.get_value()!r}')

            # if can accept args
            try:
                self._consumed[positional.name] = positional.reducer(
                    self._consumed.get(positional.name),
                    positional.processor(word.get_value())
                )
                return
            except TypeError:
                pass

            positional: ArgPos = self._get_next_positional()
            if not positional:
                raise ValueError(f'Unexpected positional argument: {word.get_value()!r}')

            self._consumed[positional.name] = positional.reducer(
                self._consumed.get(positional.name),
                positional.processor(word.get_value())
            )

    def _get_subcommand(self, name: str) -> Command:
        for subcommand in self._command.subcommands:
            if subcommand.name == name:
                return subcommand

    def _get_flag_or_opt(self, alias: str) -> Optional[Union[ArgFlag, ArgOpt]]:
        for arg in self._command.arguments:
            if isinstance(arg, (ArgFlag, ArgOpt)) and (arg.name == alias or alias in arg.aliases):
                return arg

    def _get_current_positional(self) -> Optional[ArgPos]:
        if not self._current_positional:
            self._current_positional = self._get_next_positional()
        return self._current_positional

    def _get_next_positional(self) -> Optional[ArgPos]:
        if len(self._positionals_stack):
            return self._positionals_stack.pop(0)


class SpecOps:

    @staticmethod
    def list_positionals(command: Command) -> List[ArgPos]:
        positionals = []
        for arg in command.arguments:
            if isinstance(arg, ArgPos):
                positionals.append(arg)

        return positionals
