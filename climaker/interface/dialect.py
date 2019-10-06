from abc import abstractmethod
from typing import Generic, Optional, Iterable, List
from .typevars import TToken, TCommand


__all__ = [
    'IDialect',
]


class IDialect(Generic[TCommand, TToken]):

    @abstractmethod
    def tokenize(self, args: Iterable[str]) -> List[TToken]:
        """
        Convert CLI arguments into tokens.

        """

    @abstractmethod
    def format_help(
            self,
            command: TCommand,
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
