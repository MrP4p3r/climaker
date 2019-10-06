from typing import Sequence

import pytest

from climaker.spec import Command, ArgFlag, ArgOpt, ArgPos
from climaker.tokens import Token, WordToken, FlagToken
from climaker.parser import (
    TokenParser,
    UnexpectedFlagOptError,
    ExpectedOptionValueError,
    UnexpectedAssignmentError,
    UnexpectedPositionalError,
    UnknownSubcommandError,
    ParseSubcommandError,
)


@pytest.fixture()
def tokens() -> Sequence[Token]:
    return [
        FlagToken('a'),
        FlagToken('b', value='value-b'),
        WordToken('subx'),
        FlagToken('c'), WordToken('value-c'),
        FlagToken('subx_opt1', value='subx-opt1-value'),
        FlagToken('subx_opt2'), WordToken('subx-opt2-value'),
        FlagToken('subx_flag1'),
        WordToken('subx-pos1'),
        WordToken('--subx-pos2'),
    ]


@pytest.fixture()
def command():
    return Command(
        'root',
        arguments=[
            ArgFlag('a', set_value=True, default=False),
            ArgOpt('b', type_=str),
            ArgOpt('c', type_=str),
        ],
        subcommands=[
            Command('subx', arguments=[
                ArgFlag('subx_flag1', set_value=True, default=False),
                ArgOpt('subx_opt1', type_=str, default='no-subx-opt1-value'),
                ArgOpt('subx_opt2', type_=str, default='no-subx-opt2-value'),
                ArgPos('subx_pos1'),
                ArgPos('subx_pos2'),
            ]),
        ],
    )


@pytest.fixture()
def parser(command) -> TokenParser:
    return TokenParser(command)


def test_token_consumer(parser, tokens):
    result = parser.parse(tokens)
    assert result.args
    assert result.error is None


def test_unexpected_flag_opt_unknown_flag(parser):
    # This flag is not in command spec
    result = parser.parse([
        FlagToken('totally_unknown_flag')
    ])
    assert isinstance(result.error, UnexpectedFlagOptError)


def test_unexpected_flag_opt_subcommand_flag_before_subcommand(parser):
    # Flags from any subcommand are unknown
    # until a WordToken with subcommand name is consumed from token stream
    result = parser.parse([
        FlagToken('subx_flag'),
    ])
    assert isinstance(result.error, UnexpectedFlagOptError)


def test_expected_option_value_on_token_stream_end(parser):
    # Expecting option value but token stream ends
    result = parser.parse([
        FlagToken('-b'),
    ])
    assert isinstance(result.error, ExpectedOptionValueError)


def test_expected_option_value_on_another_flag_found(parser):
    # Expecting option value but another flag token is found
    result = parser.parse([
        FlagToken('b'),
        FlagToken('a'),
    ])
    assert isinstance(result.error, ExpectedOptionValueError)


def test_unexpected_assignment(parser):
    # Not expecting to see assignment in flag token for flag argument
    result = parser.parse([
        FlagToken('a', value='this is an unexpected value for flag argument')
    ])
    assert isinstance(result.error, UnexpectedAssignmentError)


def test_unknown_subcommand(parser):
    result = parser.parse([
        WordToken('totally-unknown-subcommand'),
    ])
    assert isinstance(result.error, UnknownSubcommandError)


def test_unexpected_positional_argument(parser, tokens):
    result = parser.parse(list(tokens) + [
        WordToken('extra positional')
    ])
    assert isinstance(result.error, ParseSubcommandError)
    assert isinstance(result.child.error, UnexpectedPositionalError)
