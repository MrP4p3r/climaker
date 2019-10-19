from dataclasses import dataclass
from typing import Any, Optional, Dict

from climaker.interface import IFinalizer, IDialect
from climaker.parser import TokenParsingResult
from climaker.util import into_identifier


__all__ = [
    'MergedArgs',
    'MergingFinalizer',
]


@dataclass
class MergedArgs:
    failure: bool = False
    command_name: Optional[str] = None
    arguments: Optional[dict] = None


class MergingFinalizer(IFinalizer[TokenParsingResult, MergedArgs]):
    """
    Finalizer that merges all arguments into single dictionary.

    """

    def finalize(self, parsing_result: TokenParsingResult, dialect: IDialect) -> MergedArgs:
        arguments: Dict[str, Any] = {}

        command_name = into_identifier(parsing_result.name)
        if parsing_result.args:
            arguments.update(parsing_result.args)

        while parsing_result.child:
            parsing_result = parsing_result.child
            command_name += '.' + into_identifier(parsing_result.name)
            if parsing_result.args:
                arguments.update(parsing_result.args)

        return MergedArgs(command_name=command_name, arguments=arguments)
