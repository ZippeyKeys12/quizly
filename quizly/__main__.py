import json
from os import path
from types import ModuleType
from typing import Any, Dict, KeysView

import click
from clint.textui import indent, puts
from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
from pyfiglet import figlet_format
from termcolor import colored

from .bundles.movies import config as movie_config
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
        },
        'config': movie_config
    }
}


@cli.command()
@click.argument('bundle')
def run(bundle: str):
    with indent(2):
        puts(colored(figlet_format('Welcome To').rstrip(), attrs=['bold']))

    print()

    with indent(12):
        puts(colored(figlet_format(
            'Quizly', font='slant'), attrs=['bold']))

    module: Any
    data: Dict[str, Any]

    if bundle in BUILTIN_BUNDLES:
        data = BUILTIN_BUNDLES[bundle]['entry']  # type: ignore
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
        print()
    finally:
        module.end()


@cli.command()
@click.argument('bundle')
def config(bundle: str):
    module: Any
    data: Dict[str, Any]

    if bundle in BUILTIN_BUNDLES:
        module = BUILTIN_BUNDLES[bundle]['config']

    else:
        with open(path.join(path.dirname(__file__), 'bundles.json'), 'r') as f:
            data = json.load(f)[bundle]
            module = ModuleType(data['name'])

        with open(path.join(path.dirname(__file__), data['config']), 'r') as f:
            exec(f.read(), module.__dict__)

    module.main()


cli()
