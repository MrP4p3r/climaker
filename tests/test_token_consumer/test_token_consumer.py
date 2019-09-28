from typing import Sequence

import pytest

from climaker.spec import Command, ArgFlag, ArgOpt, ArgPos
from climaker.tokenizer import Token, WordToken, FlagToken, FlagStopToken
from climaker.parser import (
    TokenParser,
    TokenWalker,
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
        FlagStopToken(),
        WordToken('--subx-pos2'),
    ]


@pytest.fixture()
def command_spec():
    return Command(
        'root',
        arguments=[
            ArgFlag('-a', set_value=True, default=False),
            ArgOpt('-b', type_=str),
            ArgOpt('-c', type_=str),
        ],
        subcommands=[
            Command('subx', arguments=[
                ArgFlag('--subx-flag1', set_value=True, default=False),
                ArgOpt('--subx-opt1', type_=str, default='no-subx-opt1-value'),
                ArgOpt('--subx-opt2', type_=str, default='no-subx-opt2-value'),
                ArgPos('subx_pos1'),
                ArgPos('subx_pos2'),
            ]),
        ],
    )


def test_token_consumer(command_spec, tokens):
    consumer = TokenParser(command_spec)
    result = consumer.consume(TokenWalker(tokens))
    assert result.args
    assert result.error is None


def test_unexpected_flag_opt(command_spec):
    consumer = TokenParser(command_spec)

    # This flag is not in command spec
    result = consumer.consume(TokenWalker([
        FlagToken('totally_unknown_flag')
    ]))
    assert isinstance(result.error, UnexpectedFlagOptError)

    consumer = TokenParser(command_spec)

    # Flags from any subcommand are unknown
    # until a WordToken with subcommand name is consumed from token stream
    result = consumer.consume(TokenWalker([
        FlagToken('subx_flag'),
    ]))
    assert isinstance(result.error, UnexpectedFlagOptError)


def test_expected_option_value(command_spec):
    consumer = TokenParser(command_spec)

    # Expecting option value but token stream ends
    result = consumer.consume(TokenWalker([
        FlagToken('-b'),
    ]))
    assert isinstance(result.error, ExpectedOptionValueError)

    consumer = TokenParser(command_spec)

    # Expecting option value but another flag token is found
    result = consumer.consume(TokenWalker([
        FlagToken('b'),
        FlagToken('a'),
    ]))
    assert isinstance(result.error, ExpectedOptionValueError)


def test_unexpected_assignment(command_spec):
    consumer = TokenParser(command_spec)

    # Not expecting to see assignment in flag token for flag argument
    result = consumer.consume(TokenWalker([
        FlagToken('a', value='this is an unexpected value for flag argument')
    ]))
    assert isinstance(result.error, UnexpectedAssignmentError)


def test_unknown_subcommand(command_spec):
    consumer = TokenParser(command_spec)

    result = consumer.consume(TokenWalker([
        WordToken('totally-unknown-subcommand'),
    ]))
    assert isinstance(result.error, UnknownSubcommandError)


def test_unexpected_positional_argument(command_spec, tokens):
    consumer = TokenParser(command_spec)

    result = consumer.consume(TokenWalker(list(tokens) + [
        WordToken('extra positional')
    ]))
    assert isinstance(result.error, ParseSubcommandError)
    assert isinstance(result.child.error, UnexpectedPositionalError)
