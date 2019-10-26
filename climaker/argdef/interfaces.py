from typing import Optional, Protocol, TypeVar, Tuple, Sequence


__all__ = [
    'IValueParser',
    'IValueReducer',
]


V = TypeVar('V')  # Value
A = TypeVar('A')  # Accumulator


class IValueParser(Protocol[V]):
    """
    Argument value parser.

    Used during parsing step to parse words into argument values.

    A single argument value may require more than one word.

    Consider a ``--range 1 100 2`` for instance.
    What a value parser might do for this argument is to tell
    that the ``parse(...)`` method requires three words
    and then ``parse(*('1', '100', '2'))`` into range object of ``range(1, 100, 2)``.


    """

    def get_word_number_range(self) -> Tuple[int, Optional[int]]:
        """
        Get a range for the number of words required for single argument value.

        :return: Tuple of ``min_words`` and ``max_words``.
            Theese values must be ``0 < min_words <= max_words``,
            The ``max_words`` may be None, which means "variable number of words"

        """

    def parse(self, *args: str) -> V:
        """
        Parse provided words into an argument value.

        May raise a TypeError or ValueError.

        """


class IValueReducer(Protocol[V, A]):
    """
    Argument value reducer.

    Used during finalization step to process all collected argument values.

    """

    def get_value_number_range(self) -> Tuple[int, Optional[int]]:
        """
        Get a range for the number of values which reducer can accept.

        """

    def reduce(self, values: Sequence[V]) -> A:
        """
        Reduce a sequence of provided values.

        Particular reducer may use their own approach to reduce values.

        """
