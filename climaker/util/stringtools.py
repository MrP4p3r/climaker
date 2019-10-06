import re
from typing import List


__all__ = [
    'get_words',
    'into_identifier',
]


_identifier_friendly_word_pattern = re.compile(r'[a-zA-Z][a-zA-Z0-9]*')


def get_words(s: str) -> List[str]:
    """
    Extracts all identifier friendly words from the given string.

    :param s:
    :return: List of identifier-friendly words.

    """

    return _identifier_friendly_word_pattern.findall(s)


def into_identifier(s: str) -> str:
    """
    Makes an identifier name from identifier-friendly words in the given string.
    E. g. 'foO - bAr' -> 'foo_bar'

    :param s:
    :return: Identifier-friendly string

    """

    return '_'.join(get_words(s)).lower()


