import json
from os import path
from types import ModuleType
from typing import Any, Dict, KeysView

import click
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator

from dotenv import load_dotenv

from .bundles.movies import directors, release_dates

load_dotenv()


@click.group()
def cli():
    pass


@cli.command()
def install():
    print('install')


def ask_mode(modes: KeysView[str]) -> str:
    if len(modes) == 1:
        # faster than next(iter(modes))
        return min(modes)

    mode = prompt(
        f'Choose a mode from {sorted(modes)}: ',
        completer=WordCompleter(modes, WORD=True),
        validator=Validator.from_callable(
            lambda x: x in modes,
            error_message='Invalid mode',
            move_cursor_to_end=True
        ),
        validate_while_typing=False)

    print()

    return mode


BUILTIN_BUNDLES = {
    'movies': {
        'entry': {
            'Directors': directors,
            'Release Dates': release_dates
        }
    }
}


@cli.command()
@click.argument('bundle')
def run(bundle: str):
    module: Any
    data: Dict[str, Any]

    if bundle in BUILTIN_BUNDLES:
        data = BUILTIN_BUNDLES[bundle]['entry']
        mode = ask_mode(data.keys())
        module = data[mode]

    else:
        with open(path.join(path.dirname(__file__), 'bundles.json'), 'r') as f:
            data = json.load(f)[bundle]
            mode = ask_mode(data['entry'].keys())
            module = ModuleType(data['name'])

        with open(path.join(path.dirname(__file__), data['entry'][mode]), 'r') as f:
            exec(f.read(), module.__dict__)

    # Main loop
    module.begin(mode)
    try:
        module.loop()
    except KeyboardInterrupt:
        pass
    finally:
        module.end()


cli()
