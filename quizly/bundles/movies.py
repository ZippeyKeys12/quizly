import json
from random import randint, shuffle

import mistune
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.validation import Validator

session = PromptSession()
data: dict


def markdown(text: str) -> HTML:
    return HTML(mistune.html(text))


def begin(mode) -> None:
    print(markdown(f'Welcome to the **{mode}** quiz!'))
    print('When presented with a title, enter the **year release**')
    print('Enter # to exit and have fun!')
    print()

    global data
    with open('data/movies.json', 'r') as f:
        data = json.load(f)


def loop():
    looping = True
    while looping:
        first = data[0]
        shuffle(data)

        if data[0] == first:
            index = randint(1, len(data) - 1)
            data[0] = data[index]
            data[index] = first

        for movie in data:
            print('Title: {[title]}'.format(movie))
            answer = int(session.prompt(
                'Release Year> ',
                validator=Validator.from_callable(
                    lambda x: x.isdigit(),
                    error_message='Not a valid year',
                    move_cursor_to_end=True
                )))

            if answer == '#':
                looping = False
                break

            actual = movie['year']
            if answer == actual:
                print('Correct!')
                print()

            else:
                diff = abs(actual - answer)
                if diff <= 5:
                    print(markdown(f'Close, only **{diff}** off!'))

                elif answer // 10 == actual // 10:
                    print('Right decade!')

                else:
                    print('Aww, better luck next time!')

                print(markdown(f'Correct Year: **{actual}**'))


def end() -> None:
    print(markdown('*Bye!*'))
    print('This product uses the TMDb API but is not endorsed or certified by TMDb.')
