import json
import re

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from completer import TitleCompleter

with open('data/movies.json', 'r') as f:
    options = json.load(f)

    for d in options:
        if 'pattern' not in d.keys():
            d['pattern'] = re.escape(d['title'])

        try:
            for t in d['alt_titles']:
                if 'pattern' not in t.keys():
                    t['pattern'] = re.escape(t['title'])
        except KeyError:
            pass

session = PromptSession(completer=TitleCompleter(
    options), auto_suggest=AutoSuggestFromHistory())

try:
    while True:
        text = session.prompt('String: ')

except KeyboardInterrupt:
    exit(0)
