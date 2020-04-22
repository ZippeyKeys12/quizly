from typing import Any, Dict, List

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.validation import Validator

from ...util import MD
from .base import base_begin, base_end, base_loop

data: List[Dict[str, Any]]


def begin(_) -> None:
    global data
    data = base_begin('Release Dates', 'year of release')


session = PromptSession()


def qa_input(movie: Dict[str, Any]) -> str:
    print('Title: {[title]} dir. '.format(movie), end='')
    for name in movie['directors'][:-1]:
        print(f'{name}, ')
    print(movie['directors'][-1]['name'])

    return session.prompt(
        'Release Year> ',
        validator=Validator.from_callable(
            lambda x: x.isdigit(),
            error_message='Not a valid year',
            move_cursor_to_end=True
        ))


def qa_correct(answer: str, movie: Dict[str, Any]) -> bool:
    return int(answer) == movie['year']


def qa_response(answer_in: str, movie: Dict[str, Any], print_result):
    answer = int(answer_in)
    actual = movie['year']

    if answer == actual:
        print_result('Correct!')
        print()

    else:
        diff = abs(actual - answer)

        if diff <= 5:
            print_result(MD(f'Close, only **{diff}** off!'), end='')

        elif answer // 10 == actual // 10:
            print_result('Right decade!')

        else:
            print_result('Aww, better luck next time!')

        print(HTML(f'Correct Year: <b fg="ansired">{actual}</b>'))
        print()


def loop():
    base_loop(data, qa_input, qa_correct, qa_response)


def end():
    base_end()
