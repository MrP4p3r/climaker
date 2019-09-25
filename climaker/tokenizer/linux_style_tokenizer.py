import re
from typing import Optional, Iterable, List
from .tokens import *


__all__ = [
    'LinuxStyleTokenizer',
]


class LinuxStyleTokenizer:

    _stop_options_pattern = re.compile('^--$')
    _single_long_option_pattern = re.compile(r'^--([a-z-]+)(?:(=)(.*))?$')
    _short_options_pattern = re.compile(r'^-([a-z]+)(?:(=)(.*))?$')

    @classmethod
    def tokenize_args(cls, args: Iterable[str]) -> List[Token]:
        had_flag_stop = False

        result = []
        for index, arg in enumerate(args):
            arg_tokens = cls.tokenize_single_arg(arg, had_flag_stop)
            for token in arg_tokens:
                if token.into_flag_stop():
                    had_flag_stop = True

            result.extend(arg_tokens)

        return result

    @classmethod
    def tokenize_single_arg(cls, arg: str, had_flag_stop: bool = False) -> List[Token]:
        result = None
        if not had_flag_stop:
            result = (
                cls._try_stop_options_pattern(arg)
                or cls._try_single_long_flag_pattern(arg)
                or cls._try_short_flag_pattern(arg)
            )

        if result is not None:
            return result

        return [WordToken(arg)]

    @classmethod
    def _try_stop_options_pattern(cls, arg: str) -> Optional[List[Token]]:
        match = cls._stop_options_pattern.match(arg)
        if match:
            return [FlagStopToken()]

    @classmethod
    def _try_single_long_flag_pattern(cls, arg: str) -> Optional[List[Token]]:
        match = cls._single_long_option_pattern.match(arg)
        if match:
            flag_name = match.group(1).replace('-', '_')
            flag_value = None
            if match.group(2):
                flag_value = match.group(3)

            return [FlagToken(name=normalize_identifier(flag_name), value=flag_value)]

    @classmethod
    def _try_short_flag_pattern(cls, arg: str) -> Optional[List[Token]]:
        match = cls._short_options_pattern.match(arg)
        if match:
            result = []
            flags = match.group(1)
            for flag_name in flags[:-1]:
                result.append(FlagToken(name=normalize_identifier(flag_name)))

            last_flag_name = flags[-1]
            last_flag_value = None
            if match.group(2):
                last_flag_value = match.group(3)

            result.append(FlagToken(name=normalize_identifier(last_flag_name), value=last_flag_value))
            return result


def normalize_identifier(identifier: str) -> str:
    return identifier.strip('-').replace('-', '_')
