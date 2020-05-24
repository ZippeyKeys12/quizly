from typing import Any, Callable, Dict, List

from Levenshtein import ratio as levenshtein_ratio  # noqa
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import print_formatted_text as print

from ...util import normalize
from .base import base_begin, base_end, base_loop

data: List[Dict[str, Any]]
session: PromptSession
score: int
total: int


def begin(_) -> None:
    global data, session, score, total
    data = base_begin('Directors', 'director of the film')
    session = PromptSession()
    score = 0
    total = 0


def qa_input(movie: Dict[str, Any]) -> str:
    print('Title: {0[title]} ({0[year]})'.format(movie))

    return session.prompt('Director> ')


def qa_correct(answer: str, movie: Dict[str, Any]) -> bool:
    return normalize(answer) in map(lambda x: normalize(x['name']), movie['directors'])


def qa_response(answer: str, movie: Dict[str, Any], print_result: Callable[[str], None]):
    global total
    total += 1

    answer = normalize(answer)
    actual = [x['name'] for x in movie['directors']]
    cleaned = list(map(normalize, actual))

    if answer in cleaned:
        print_result('Correct!')

        global score
        score += 1

    else:
        ratio = max(map(lambda x: levenshtein_ratio(x, answer), cleaned))

        if len(answer) == 0:
            print_result('At least give it a try!')

        elif ratio >= .9:
            print_result('Close!')

        else:
            print_result('Aww, better luck next time!')

        if len(cleaned) == 1:
            print(HTML(f'Correct Director: <b fg="ansired">{actual[0]}</b>'))
        else:
            to_print = 'Correct Directors: <b fg="ansired">'
            for name in actual[:-1]:
                to_print += f'{name}, '
            print(HTML('{}and {}</b>'.format(to_print, actual[-1])))

    print()


def loop():
    base_loop(data, qa_input, qa_correct, qa_response)


def end():
    if total != 0:
        percent = score / total * 100

        if percent == 100:
            color = 'ansiwhite'
        elif percent >= 90:
            color = 'ansigreen'
        elif percent >= 80:
            color = 'gold'
        elif percent >= 70:
            color = 'darkorange'
        else:
            color = 'ansired'

        print(
            HTML(f'You got <b fg="{color}">{percent:.2f}%</b> correct ({score}/{total})'))

    base_end()
