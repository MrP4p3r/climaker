import pytest
from climaker.tokenizer import LinuxStyleTokenizer


@pytest.fixture()
def tokenizer():
    return LinuxStyleTokenizer


def test_flag(tokenizer):
    tokens = tokenizer.tokenize_single_arg('-x')
    assert len(tokens) == 1

    token = tokens[0].into_flag()
    assert token
    assert token.get_name() == 'x'
    assert token.get_value() is None


def test_long_flag(tokenizer):
    tokens = tokenizer.tokenize_single_arg('--long-flag')
    assert len(tokens) == 1

    token = tokens[0].into_flag()
    assert token
    assert token.get_name() == 'long_flag'
    assert token.get_value() is None


def test_many_flags(tokenizer):
    tokens = tokenizer.tokenize_single_arg('-abc')
    assert len(tokens) == 3

    for name, token in zip(('a', 'b', 'c'), tokens):
        flag = token.into_flag()
        assert flag
        assert flag.get_name() == name
        assert flag.get_value() is None


def test_flag_assignment(tokenizer):
    tokens = tokenizer.tokenize_single_arg('-x=argvalue')
    assert len(tokens) == 1

    flag = tokens[0].into_flag()
    assert flag
    assert flag.get_name() == 'x'
    assert flag.get_value() == 'argvalue'


def test_empty_flag_assignment(tokenizer):
    tokens = tokenizer.tokenize_single_arg('-x=')
    assert len(tokens) == 1

    flag = tokens[0].into_flag()
    assert flag
    assert flag.get_name() == 'x'
    assert flag.get_value() == ''


def test_long_flag_assignment(tokenizer):
    tokens = tokenizer.tokenize_single_arg('--long-flag=-42')
    assert len(tokens) == 1

    flag = tokens[0].into_flag()
    assert flag
    assert flag.get_name() == 'long_flag'
    assert flag.get_value() == '-42'


def test_flag_stop(tokenizer):
    tokens = tokenizer.tokenize_single_arg('--')
    assert len(tokens) == 1

    flag_stop = tokens[0].into_flag_stop()
    assert flag_stop


def test_word(tokenizer):
    tokens = tokenizer.tokenize_single_arg('some--word')
    assert len(tokens) == 1

    word = tokens[0].into_word()
    assert word
    assert word.get_value() == 'some--word'


def test_flag_ish_word_after_flag_stop(tokenizer):
    tokens = tokenizer.tokenize_single_arg('--not-a-flag', had_flag_stop=True)
    assert len(tokens) == 1

    word = tokens[0].into_word()
    assert word
    assert word.get_value() == '--not-a-flag'


def test_args_full(tokenizer):
    tokens = tokenizer.tokenize_args(['--flag-a', 'word-a', '--flag-b=value-b', '-xyz=-42', '--', '-x'])
    assert len(tokens) == 8

    # --flag-a
    assert tokens[0].into_flag().get_name() == 'flag_a'

    # word-a
    assert tokens[1].into_word().get_value() == 'word-a'

    # --flag-b=value-b
    assert tokens[2].into_flag().get_name() == 'flag_b'
    assert tokens[2].into_flag().get_value() == 'value-b'

    # -x
    assert tokens[3].into_flag().get_name() == 'x'

    # -y
    assert tokens[4].into_flag().get_name() == 'y'

    # -z=-42
    assert tokens[5].into_flag().get_name() == 'z'
    assert tokens[5].into_flag().get_value() == '-42'

    # --
    assert tokens[6].into_flag_stop()

    # -x
    assert tokens[7].into_word().get_value() == '-x'
