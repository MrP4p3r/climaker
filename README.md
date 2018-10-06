# CliMaker

Python package which allows to define a CLI argument parser (with subcommands) with a schema.
The only dependency is the `argparse` library.
Tested (a bit) with Python 3.6+

Please, [create an issue](https://github.com/MrP4p3r/climaker/issues/new) if you have a bug-report or find this package needs an improvement. (It definitely needs an improvement.)

# Installation

```pip install climaker```

# Example

```python
import sys
from climaker import Parser, Subcommands, Arguments, Arg

# Define commands structure
spec = Subcommands({
    'bake': Subcommands({
        'cake': Arguments([
            Arg('-s', '--size', type_=int, default=10),
            Arg('--color', default='pink'),
        ]),
        'cookie': Arguments([
            Arg('--kind', default='biscuit'),
        ]),
    }),
    'eat': Arguments([
        Arg('edible', default='cookie'),
    ])
})

# Create a parser
parser = Parser(spec)

# Parse arguments
action = parser.parse_arguments(sys.argv[1:])

print(action.command)
# ['bake', 'cake']

print(action.params)
# {'size': 10, 'color': 'pink'}
```
