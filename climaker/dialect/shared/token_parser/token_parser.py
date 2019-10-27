from __future__ import annotations

from collections import defaultdict
from typing import Optional, Union, Sequence, List

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
        self._consumed = defaultdict(list)
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
            return self._on_flag_or_opt_not_found(flag_token, walker)

        elif isinstance(flag_or_opt, ArgOpt):
            return self._consume_flag_argopt(flag_token, flag_or_opt, walker)

        elif isinstance(flag_or_opt, ArgFlag):
            return self._consume_flag_argflag(flag_token, flag_or_opt)

        else:
            raise RuntimeError('Totally unexpected error')

    def _consume_word(self, word: WordToken, walker: Walker[Token]) -> Result[None, CliError]:
        if not (positional := self._state.get_current_positional()):
            return Err(UnexpectedPositional(word.get_value()))

        _, max_values = positional.reducer.get_value_number_range()
        if max_values is not None and len(self._consumed[positional.name]) >= max_values:
            if not (positional := self._state.get_next_positional()):
                return Err(UnexpectedPositional(word.get_value()))

        value = positional.processor.parse(word.get_value())
        self._consumed[positional.name].append(value)

        return Ok(None)

    def _on_flag_or_opt_not_found(self, flag_token: FlagToken, walker: Walker[Token]) -> Result[None, CliError]:
        if not self._parent:
            return Err(UnexpectedFlagOpt(flag_token.get_name()))

        result = self._parent._consume_flag(flag_token, walker)
        if result.is_err():
            return Err(ParentCommandParsingError(result.unwrap_err()))

        return Ok(None)

    def _consume_flag_argopt(self, flag_token: FlagToken,
                             opt: ArgOpt, walker: Walker[Token]) -> Result[None, CliError]:

        min_words, max_words = opt.processor.get_word_number_range()

        if max_words > 1:
            if flag_token.get_value():
                return Err(UnexpectedAssignment(flag_token.get_raw()))

            get_words_result = self._get_words(walker, opt.name, min_words, max_words)
            if get_words_result.is_err():
                return Err(get_words_result.unwrap_err())

            self._consumed[opt.name].append(opt.processor.parse(*(
                word.get_value() for word in get_words_result.unwrap()
            )))

        else:
            opt_value = flag_token.get_value()
            if opt_value is None:
                if not walker.lookup() or not walker.lookup().into_word():
                    found = walker.lookup() and walker.lookup().get_raw()
                    return Err(ExpectedOptionValue(flag_token.get_raw(), found))

                opt_value = walker.next().into_word().get_value()

            self._consumed[opt.name].append(opt.processor.parse(
                opt_value
            ))

        return Ok(None)

    def _consume_flag_argflag(self, flag_token: FlagToken,
                              flag: ArgFlag) -> Result[None, CliError]:

        if flag_token.get_value():
            return Err(UnexpectedAssignment(flag_token.get_raw()))

        self._consumed[flag.name].append(flag.set_value)
        return Ok(None)

    def _get_words(self, walker: Walker[Token], argument_name: str,
                   min_words: int, max_words: Optional[int]) -> Result[List[WordToken], CliError]:
        words = []
        while True:
            if not walker.lookup() or not walker.lookup().into_word():
                break

            words.append(walker.next().into_word())
            if max_words is not None and len(words) >= max_words:
                break

        if len(words) < min_words:
            return Err(InsufficientPositionalsNumber(argument_name, min_words))

        return Ok(words)


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
