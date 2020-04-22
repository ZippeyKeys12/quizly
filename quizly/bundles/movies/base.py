import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import path
from random import randint, shuffle
from typing import Any, Callable, Dict, List

import tmdbsimple as tmdb
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.shortcuts import ProgressBar

from ...util import MD

session = PromptSession()


def base_begin(title: str, answer: str) -> List[Dict[str, Any]]:
    tmdb.API_KEY = os.getenv('TMDB_API_KEY')

    if not path.isfile('data/movies.json'):
        data = load_data()

    else:
        with open('data/movies.json', 'r') as f:
            data = json.load(f)

    print(MD(f'Welcome to the **{title}** quiz!'), end='')
    print(
        MD(f'When presented with a title, enter the **{answer}**'), end='')
    print('Enter # to exit and have fun!')
    print()

    return data


def load_data() -> List[Dict[str, Any]]:
    discover = tmdb.Discover()

    with ProgressBar(title=MD('**Discovering Movies:**')) as pb:
        resp = discover.movie()

        data: List = []

        def add_discover(page_num: int):
            data.extend(discover.movie(page=page_num)['results'])

        with ThreadPoolExecutor(max_workers=5) as executor:
            future = [executor.submit(add_discover, i) for i in range(
                1, resp['total_pages'] + 1)]

            for _ in pb(as_completed(future), label='Querying TMDB:', total=resp['total_pages']):
                pass

    print()

    with ProgressBar(title=MD('**Compiling Information:**')) as pb:
        def scan_crew(movie: Dict[str, Any]):
            movie['year'] = movie['release_date'][:4]

            crew = tmdb.Movies(movie['id']).credits()['crew']

            start_index = 0
            while crew[start_index]['department'] != 'Direction':
                start_index += 1

            for person in crew[start_index]:
                if person['job'] == 'Director':
                    if 'directors' not in movie:
                        movie['directors'] = [person]

                    else:
                        movie['directors'].append(person)

                elif person['department'] != 'Direction':
                    return

        with ThreadPoolExecutor(max_workers=10) as executor:
            future = [executor.submit(scan_crew, movie) for movie in data]

            for _ in pb(as_completed(future), label='Scanning Cast and Crew:', total=len(data)):
                pass

    data = list(filter(lambda x: 'directors' in x, data))

    print()

    with open('data/movies.json', 'w') as f:
        json.dump(data, f)

    return data


def base_loop(
        data: List[Dict[str, Any]],
        qa_input: Callable[[Dict[str, Any]], str],
        qa_correct: Callable[[str, Dict[str, Any]], bool],
        qa_response: Callable[[str, Dict[str, Any], Callable], None]):
    global mode, prompt, validator
    looping = True
    while looping:
        first = data[0]
        shuffle(data)

        if data[0] == first:
            index = randint(1, len(data) - 1)
            data[0] = data[index]
            data[index] = first

        for movie in data:
            answer = qa_input(movie)

            if answer.strip() == '#':
                print()
                return

            if qa_correct(answer, movie):
                color = 'ansigreen'
            else:
                color = 'ansired'

            def print_result(text: str) -> str:
                return print(HTML(f'<b fg="{color}">{text}</b>'))

            qa_response(answer, movie, print_result)


def base_end():
    print(MD('*Bye!*'))
    print('This product uses the TMDb API but is not endorsed or certified by TMDb.')
