from typing import Sequence

import pytest

from climaker.spec import Command, ArgFlag, ArgOpt, ArgPos
from climaker.tokenizer import Token, WordToken, FlagToken, FlagStopToken
from climaker.parser import TokenParser, TokenWalker


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
def walker(tokens: Sequence[Token]) -> TokenWalker:
    return TokenWalker(tokens)


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


def test_token_consumer(command_spec, walker):
    consumer = TokenParser(command_spec)
    consumer.consume(walker)
