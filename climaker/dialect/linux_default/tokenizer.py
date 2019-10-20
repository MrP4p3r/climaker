import re
from typing import Optional, Iterable, List

from climaker.dialect.shared import *


__all__ = [
    'DefaultLinuxTokenizer',
]


class DefaultLinuxTokenizer:
    """
    This tokenizer is available to process the most commonly used
    CLI grammar by programs for Linux-based operating systems::

        prog -a -bc=OptionValueForC --e-flag --f-option=value \
            subcommand --subcommand-flag --subcommand-option=42 \
            postional_a positional_b

    Output for the example above will be::

        [
            WordToken('prog'),
            FlagToken('a'), FlagToken('b'),
            FlagToken('c', value='OptionValueForC'),
            FlagToken('e_flag'), FlagToken('f_option', value='value'),
            WordToken('subcommand'),
            FlagToken('subcommand_flag'),
            FlagToken('subcommand_option', value='42'),
            WordToken('positional_a'),
            WordToken('positional_b'),
        ]

    """

    _stop_options_pattern = re.compile('^--$')
    _single_long_option_pattern = re.compile(r'^--([a-z-]+)(?:(=)(.*))?$')
    _short_options_pattern = re.compile(r'^-([a-z]+)(?:(=)(.*))?$')

    def __init__(self):
        self._had_flag_stop = False

    def tokenize_args(self, args: Iterable[str]) -> List[Token]:
        result = []
        for index, arg in enumerate(args):
            arg_tokens = self.tokenize_single_arg(arg)
            result.extend(arg_tokens)

        return result

    def tokenize_single_arg(self, arg: str) -> List[Token]:
        result = None
        if not self._had_flag_stop:
            if self._is_flag_stop(arg):
                self._had_flag_stop = True
                return []

            result = (
                self._try_single_long_flag_pattern(arg)
                or self._try_short_flag_pattern(arg)
            )

        if result is not None:
            return result

        return [WordToken(arg)]

    @classmethod
    def _is_flag_stop(cls, arg: str) -> bool:
        return bool(cls._stop_options_pattern.match(arg))

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
