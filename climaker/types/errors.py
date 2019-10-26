from typing import get_type_hints


__all__ = [
    'CliError',
    'ParsingError',
]


class CliError:

    def __repr__(self) -> str:
        return '{}({})'.format(type(self).__name__, ', '.join((
            f'{attr_name}={getattr(self, attr_name)!r}'
            for attr_name in get_type_hints(type(self)).keys()
        )))


class ParsingError(CliError):
    pass
