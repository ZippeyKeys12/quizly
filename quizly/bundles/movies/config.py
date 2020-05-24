import re
from os import path
from typing import Optional

import fire
import toml
# from bullet import Bullet, Check, SlidePrompt, VerticalPrompt, YesNo
from clint.textui import indent, puts
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.validation import Validator
from termcolor import colored

from .scrape import scrape_list


def main():
    _session = PromptSession()
    _commands = {
        'status': status,
        'list': {
            'add': add_list
        }
    }

    _completes = {
        'status': None,
        'list': {'add': None}
    }

    print_formatted_text(HTML('<b>Config:</b>'))

    status()

    while True:
        ip = _session.prompt(
            'Config> ',
            completer=NestedCompleter.from_nested_dict(_completes),
            validator=Validator.from_callable(_validate)
        ).strip()

        if ip == '#':
            return

        fire.Fire(_commands, command=ip)


_ws = re.compile(r'\s+')


def _validate(command: str) -> bool:
    x = _ws.split(command.strip())

    if x[0] == '#':
        return True

    elif x[0] == 'status':
        return len(x) == 1

    elif x[0] == 'list':
        if len(x) == 1:
            return False

        if x[1] == 'add':
            return len(x) >= 3
            # return all(_url.match(x) is not None for x in x[1:])

    return False


def _bold(x: str) -> str:
    return colored(x, attrs=['bold'])


def load_config() -> Optional[dict]:
    if path.isfile('config.toml'):
        with open('config.toml', 'r') as f:
            return toml.load(f)['quizly']['movies']

    return None


def status():
    config = load_config()

    if config is None:
        return

    print('Lists:')
    with indent(2):
        for l in config['data']['lists']:
            puts(f"{_bold(l['title'])} by {l['creator']} ({l['url']})")


def add_list(*urls: str):
    for url in urls:
        title, creator, url, _ = scrape_list(url)

        if path.isfile('config.toml'):
            with open('config.toml', 'r') as f:
                data = toml.load(f)
        else:
            data = {}

        data['quizly']['movies']['data']['lists'].append({
            'title': title,
            'creator': creator,
            'url': url
        })

        with open('config.toml', 'w') as f:
            toml.dump(data, f)
