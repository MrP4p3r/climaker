"""Parser tests"""

from unittest import TestCase
from climaker import Parser, Arg, Arguments, Subcommands


class ParserTest(TestCase):

    def test_no_args_parser(self):
        parser = Parser(Arguments([]))
        action = parser.parse_arguments([])
        self.assertEqual(len(action.params), 0)

    def test_parser_flat(self):
        parser = Parser(fixture_flat_spec, prog='climaker_test')
        action = parser.parse_arguments(fixture_flat_args)
        self.assertEqual(action.command, fixture_flat_command)
        self.assertEqual(action.params, fixture_flat_params)

    def test_parser_complex(self):
        parser = Parser(fixture_complex_spec, prog='climaker_test')
        for check_key, check_config in fixture_complex_checks.items():
            with self.subTest(f'Parser complex check {check_key!r}'):
                action = parser.parse_arguments(check_config['args'])
                self.assertEqual(action.command, check_config['command'])
                self.assertEqual(action.params, check_config['params'])


fixture_flat_spec = Arguments([
    Arg('name'),
    Arg('-f', '--foo'),
    Arg('--bar', type_=int, default=42),
    Arg('--no-check', arg_type='flag', default=False),
])

fixture_flat_args = ['Some Name', '-f', 'string value', '--bar', '19', '--no-check']

fixture_flat_command = []
fixture_flat_params = {
    'name': 'Some Name',
    'foo': 'string value',
    'bar': 19,
    'no_check': True,
}


fixture_complex_spec = Subcommands({
    'cmd1': Subcommands({
        'sub1': Arguments([Arg('name')]),
        'sub2': Arguments([Arg('value')]),
    }),
    'cmd2': Arguments([
        Arg('-f', '--foo', type_=int),
    ])
})

fixture_complex_checks = {
    'check_1': {
        'args': ['cmd1', 'sub1', 'Name'],
        'command': ['cmd1', 'sub1'],
        'params': {'name': 'Name'},
    },
    'check_2': {
        'args': ['cmd1', 'sub2', 'Value'],
        'command': ['cmd1', 'sub2'],
        'params': {'value': 'Value'},
    },
    'check_3': {
        'args': ['cmd2', '-f', '42'],
        'command': ['cmd2'],
        'params': {'foo': 42},
    }
}
