from __future__ import annotations
from typing import Optional, List, Union

from climaker.tokenizer import FlagToken, WordToken
from climaker.spec import Command, ArgOpt, ArgFlag, ArgPos

from .token_walker import TokenWalker
from .parse_result import ParserResult
from .exceptions import *


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

    def consume(self, walker: TokenWalker) -> ParserResult:
        try:
            while walker.lookup():
                token = walker.next()
                if token.into_flag_stop():
                    continue
                elif token.into_flag():
                    self.consume_flag(token.into_flag(), walker)
                elif token.into_word():
                    word = token.into_word()
                    if self._command.has_subcommands():
                        subcommand = self._get_subcommand(word.get_value())
                        if not subcommand:
                            raise UnknownSubcommandError(word.get_value())

                        subconsumer = TokenParser(subcommand, self)
                        subcommand_parse_result = subconsumer.consume(walker)
                        if subcommand_parse_result.error:
                            return ParserResult(name=self._command.name,
                                                error=ParseSubcommandError(subcommand.name),
                                                child=subcommand_parse_result)
                        else:
                            return ParserResult(name=self._command.name,
                                                args=self._consumed,
                                                child=subcommand_parse_result)
                    else:
                        self.consume_word(word, walker)
        except TokenParserError as err:
            return ParserResult(name=self._command.name,
                                error=err)
        else:
            return ParserResult(name=self._command.name,
                                args=self._consumed)

    def consume_flag(self, flag_token: FlagToken, walker: TokenWalker):
        alias = flag_token.get_name()
        flag_or_opt = self._get_flag_or_opt(alias)

        if not flag_or_opt:
            if not self._parent:
                raise UnexpectedFlagOptError(flag_token)
            else:
                self._parent.consume_flag(flag_token, walker)

        elif isinstance(flag_or_opt, ArgOpt):
            opt = flag_or_opt
            opt_value = flag_token.get_value()
            if opt_value is None:
                while walker.lookup() and walker.lookup().into_flag_stop():
                    walker.next()
                if not walker.lookup() or not walker.lookup().into_word():
                    raise ExpectedOptionValueError(flag_token, walker.lookup())
                word = walker.next().into_word()
                opt_value = word.get_value()

            self._consumed[opt.name] = opt.reducer(
                self._consumed.get(opt.name),
                opt.processor(opt_value),
            )

        elif isinstance(flag_or_opt, ArgFlag):
            flag = flag_or_opt
            if flag_token.get_value():
                raise UnexpectedAssignmentError(flag_token)

            self._consumed[flag.name] = flag.set_value

        else:
            raise RuntimeError('Totally unexpected error')

    def consume_word(self, word: WordToken, walker: TokenWalker):
        positional: ArgPos = self._get_current_positional()
        if not positional:
            raise UnexpectedPositionalError(word)

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
            raise UnexpectedPositionalError(word)

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
