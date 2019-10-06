from __future__ import annotations
from typing import Optional


__all__ = [
    'Token',
    'WordToken',
    'FlagToken',
    # 'FlagStopToken',
]


class Token:

    def into_flag(self) -> Optional[FlagToken]:
        return None

    def into_word(self) -> Optional[WordToken]:
        return None

    # def into_flag_stop(self) -> Optional[FlagStopToken]:
    #     return None


class FlagToken(Token):

    def __init__(self, name: str, value: Optional[str] = None):
        self._name = name
        self._value = value

    def get_name(self) -> str:
        return self._name

    def get_value(self) -> Optional[str]:
        return self._value

    def into_flag(self) -> Optional[FlagToken]:
        return self

    def __repr__(self):
        repr_str = f'FlagToken({self._name}'

        if self._value is not None:
            repr_str += f'={self._value!r})'
        else:
            repr_str += ')'

        return repr_str


# class FlagStopToken(Token):
#
#     def into_flag_stop(self) -> Optional[FlagStopToken]:
#         return self


class WordToken(Token):

    def __init__(self, value: str):
        self._value = value

    def get_value(self) -> str:
        return self._value

    def into_word(self) -> Optional[WordToken]:
        return self

    def __repr__(self):
        return f'WordToken({self._value!r})'
