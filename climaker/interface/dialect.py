from abc import abstractmethod
from typing import Generic, TypeVar, Optional, Iterable, Sequence


__all__ = [
    'IDialect',
]


C = TypeVar('C')  # Command type
T = TypeVar('T')  # Token type


class IDialect(Generic[C, T]):

    @abstractmethod
    def tokenize(self, args: Iterable[str]) -> Sequence[T]:
        """
        Convert CLI arguments into tokens.

        """

    @abstractmethod
    def format_help(
            self,
            command: C,
            subcommand_path: Iterable[str] = (),
            error: Optional[str] = None,
            short: bool = False,
    ) -> str:
        """
        Format help for specified command.

        """

    @abstractmethod
    def format_flag(self, identifier_name: str) -> str:
        """
        Format ``identifier_friendly`` name to dialect-specific ``--flag-format``.

        """

    @abstractmethod
    def format_word(self, identifier_name: str) -> str:
        """
        Format ``identifier_friendly`` name to dialect-specific ``WORD_FORMAT``.

        """
