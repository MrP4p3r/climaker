from __future__ import annotations
from typing import Optional, Union, Sequence

from climaker.interface import IParser
from climaker.tokens import Token, FlagToken, WordToken
from climaker.argdef import Command, ArgOpt, ArgFlag, ArgPos
from climaker.util import Walker, into_identifier

from .parse_result import ParserResult
from .exceptions import *


__all__ = [
    'TokenParser',
]


class TokenParser(IParser[Token, ParserResult]):

    def __init__(self, command: Command, parent: Optional[TokenParser] = None):
        self._command = command
        self._parent = parent
        self._consumed = {}
        self._state = CommandParseState(self._command)

    def parse(self, tokens: Sequence[Token]) -> ParserResult:
        return self.consume(Walker(tokens))

    def consume(self, walker: Walker[Token]) -> ParserResult:
        try:
            while walker.lookup():
                token = walker.next()
                if token.into_flag():
                    self.consume_flag(token.into_flag(), walker)
                elif token.into_word():
                    word = token.into_word()
                    if self._command.has_subcommands():
                        subcommand = self._state.get_subcommand(word.get_value())
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

    def consume_flag(self, flag_token: FlagToken, walker: Walker[Token]):
        alias = flag_token.get_name()
        flag_or_opt = self._state.get_flag_or_opt(alias)

        if not flag_or_opt:
            if not self._parent:
                raise UnexpectedFlagOptError(flag_token)
            else:
                self._parent.consume_flag(flag_token, walker)

        elif isinstance(flag_or_opt, ArgOpt):
            opt = flag_or_opt
            opt_value = flag_token.get_value()
            if opt_value is None:
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

    def consume_word(self, word: WordToken, walker: Walker[Token]):
        positional: ArgPos = self._state.get_current_positional()
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

        positional: ArgPos = self._state.get_next_positional()
        if not positional:
            raise UnexpectedPositionalError(word)

        self._consumed[positional.name] = positional.reducer(
            self._consumed.get(positional.name),
            positional.processor(word.get_value())
        )


class CommandParseState:

    def __init__(self, command: Command):
        self._command = command

        positionals = []
        flags_and_opts = {}
        for arg in command.arguments:
            if isinstance(arg, ArgPos):
                positionals.append(arg)
            elif isinstance(arg, (ArgFlag, ArgOpt)):
                flags_and_opts[arg.name] = arg
                for alias in arg.aliases:
                    flags_and_opts[alias] = arg

        self._positionals = Walker(positionals)
        self._flags_and_opts = flags_and_opts

    def get_current_positional(self) -> Optional[ArgPos]:
        return self._positionals.current() or self._positionals.next()

    def get_next_positional(self) -> Optional[ArgPos]:
        return self._positionals.next()

    def get_flag_or_opt(self, alias: str) -> Optional[Union[ArgFlag, ArgOpt]]:
        return self._flags_and_opts.get(into_identifier(alias))

    def has_subcommands(self) -> bool:
        return self._command.has_subcommands()

    def get_subcommand(self, name: str) -> Optional[Command]:
        for subcommand in self._command.subcommands:
            if subcommand.name == name:
                return subcommand
