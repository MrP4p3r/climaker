from __future__ import annotations
from typing import Optional, Union, Sequence

from climaker.types import ArgTree, CliError
from climaker.argdef import Command, ArgOpt, ArgFlag, ArgPos
from climaker.util import Walker, Result, Ok, Err, into_identifier

from .tokens import *
from .errors import *


__all__ = [
    'TokenParser',
]


class TokenParser:

    def __init__(self, command: Command, parent: Optional[TokenParser] = None):
        self._command = command
        self._parent = parent
        self._consumed = {}
        self._state = _CommandParseState(self._command)

    def parse(self, tokens: Sequence[Token]) -> Result[ArgTree, CliError]:
        try:
            return self._consume(Walker(tokens))
        except Exception as exc:
            return Err(FailedWithException(exc))

    def _consume(self, walker: Walker[Token]) -> Result[ArgTree, CliError]:
        while token := walker.next():

            if flag_token := token.into_flag():
                consume_result = self._consume_flag(flag_token, walker)
                if consume_result.is_err():
                    return Err(consume_result.unwrap_err())

            elif word_token := token.into_word():
                if self._command.has_subcommands():
                    if not (subcommand := self._state.get_subcommand(word_token.get_value())):
                        return Err(UnknownSubcommand(word_token.get_value()))

                    subparser = TokenParser(subcommand, parent=self)
                    subcommand_parse_result = subparser._consume(walker)
                    if subcommand_parse_result.is_err():
                        return Err(SubcommandParsingError(
                            subcommand.name,
                            subcommand_parse_result.unwrap_err(),
                        ))
                    else:
                        return Ok(ArgTree(
                            name=self._command.name,
                            args=self._consumed,
                            child=subcommand_parse_result.unwrap(),
                        ))

                consume_result = self._consume_word(word_token, walker)
                if consume_result.is_err():
                    return Err(consume_result.unwrap_err())

        return Ok(ArgTree(
            name=self._command.name,
            args=self._consumed,
        ))

    def _consume_flag(self, flag_token: FlagToken, walker: Walker[Token]) -> Result[None, CliError]:
        alias = flag_token.get_name()
        flag_or_opt = self._state.get_flag_or_opt(alias)

        if not flag_or_opt:
            if not self._parent:
                return Err(UnexpectedFlagOpt(flag_token))

            self._parent._consume_flag(flag_token, walker)

        elif isinstance(flag_or_opt, ArgOpt):
            opt = flag_or_opt
            opt_value = flag_token.get_value()
            if opt_value is None:
                if not walker.lookup() or not walker.lookup().into_word():
                    return Err(ExpectedOptionValue(flag_token, walker.lookup()))

                word = walker.next().into_word()
                opt_value = word.get_value()

            self._consumed[opt.name] = opt.reducer(
                self._consumed.get(opt.name),
                opt.processor(opt_value),
            )

        elif isinstance(flag_or_opt, ArgFlag):
            flag = flag_or_opt
            if flag_token.get_value():
                return Err(UnexpectedAssignment(flag_token))

            self._consumed[flag.name] = flag.set_value

        else:
            raise RuntimeError('Totally unexpected error')

        return Ok(None)

    def _consume_word(self, word: WordToken, walker: Walker[Token]) -> Result[None, CliError]:
        if not (positional := self._state.get_current_positional()):
            return Err(UnexpectedPositional(word))

        # if can accept args
        try:
            self._consumed[positional.name] = positional.reducer(
                self._consumed.get(positional.name),
                positional.processor(word.get_value())
            )
            return Ok(None)
        except TypeError:
            pass

        if not (positional := self._state.get_next_positional()):
            return Err(UnexpectedPositional(word))

        try:
            self._consumed[positional.name] = positional.reducer(
                self._consumed.get(positional.name),
                positional.processor(word.get_value())
            )
            return Ok(None)
        except TypeError:
            return Err(UnexpectedPositional(word))


class _CommandParseState:

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
