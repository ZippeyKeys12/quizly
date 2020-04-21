import json
import types
from os import path
from typing import Any, Dict

import click
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator


@click.group()
def cli():
    pass


@cli.command()
def install():
    print('install')


def ask_mode(modes: Dict[str, str]) -> str:
    if len(modes.keys()) == 1:
        # faster than next(iter(modes.keys()))
        return modes[min(modes.keys())]

    mode = prompt(
        f'Choose a mode from {set(modes.keys())}: ',
        completer=WordCompleter(modes.keys(), WORD=True),
        validator=Validator.from_callable(
            lambda x: x in modes,
            error_message='Invalid mode',
            move_cursor_to_end=True
        ),
        validate_while_typing=False)

    return modes[mode]


@cli.command()
@click.argument('bundle')
def run(bundle: str):
    with open(path.join(path.dirname(__file__), 'bundles.json'), 'r') as f:
        data = json.load(f)[bundle]
        mode = ask_mode(data['entry'])
        module: Any = types.ModuleType(data['name'])

    with open(path.join(path.dirname(__file__), mode), 'r') as f:
        exec(f.read(), module.__dict__)

    try:
        module.begin(mode)

        module.loop()

    except KeyboardInterrupt:
        module.end()


cli()
