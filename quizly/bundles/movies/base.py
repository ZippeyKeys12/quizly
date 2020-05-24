import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import path
from random import randint, shuffle
from typing import Any, Callable, Dict, List

import tmdbsimple as tmdb
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import print_formatted_text
from prompt_toolkit.shortcuts import ProgressBar

from ...util import MD
from .config import load_config
from .scrape import scrape_list, scrape_movie

session = PromptSession()


def base_begin(title: str, answer: str) -> List[Dict[str, Any]]:
    tmdb.API_KEY = os.getenv('TMDB_API_KEY')

    config = load_config() or {}

    # Load Movies
    ids = set()

    # if config['data'].get('load_default_movies'):
    #     data, changed = load_discovery(ids)

    # else:
    data = []
    changed = False

    with ProgressBar(title=MD('**Loading Custom Lists:**')) as pb:
        if path.isfile('data/movies.json'):
            with open('data/movies.json', 'r') as f:
                list_data = json.load(f)
        else:
            list_data = {'lists': {}, 'movies': {}}

        for l in pb(config['data']['lists'], label='Adding Lists'):
            url = l['url']
            if url not in list_data['lists']:
                changed = True
                title, creator, url, movie_urls = scrape_list(url)
                list_data['lists'][url] = [scrape_movie(m) for m in movie_urls]

            ids.update(list_data['lists'][url])

    with ProgressBar() as pb:
        for i in pb(ids, label='Loading Movies'):
            if i not in list_data['movies'].keys():
                changed = True
                list_data['movies'][i] = load_movie(i)

            data.append(list_data['movies'][i])

    if changed:
        with open('data/movies.json', 'w') as f:
            json.dump(list_data, f)

    print_formatted_text(MD(f'Welcome to the **{title}** quiz!'), end='')
    print_formatted_text(
        MD(f'When presented with a title, enter the **{answer}**'), end='')
    print('Enter # to exit and have fun!')
    print()

    return data


tags = ['popularity', 'id', 'video', 'vote_count', 'vote_average',
        'title', 'release_date', 'original_language',  'original_title',
        'backdrop_path', 'adult', 'overview', 'poster_path']


def load_movie(id: int) -> dict:
    res = {}

    details = tmdb.Movies(id).info()

    # Handle Shared Tags
    for tag in tags:
        res[tag] = details[tag]

    # Handle Genres
    res['genre_ides'] = list(map(lambda x: x['id'], details['genres']))

    # Handle Year
    res['year'] = details['release_date'][:4]

    # Free up space
    del details

    # Handle Credits
    crew = tmdb.Movies(id).credits()['crew']

    for person in crew:
        if person['job'] == 'Director':
            if 'directors' not in res:
                res['directors'] = [person]

            else:
                res['directors'].append(person)

    return res


TOTAL_PAGES = 10


def load_data() -> List[Dict[str, Any]]:
    discover = tmdb.Discover()

    data: List = []

    with ProgressBar(title=MD('**Discovering Movies:**')) as pb:
        def add_discover(page_num: int):
            data.extend(discover.movie(page=page_num)['results'])

        with ThreadPoolExecutor(max_workers=5) as executor:
            future = [executor.submit(add_discover, i) for i in range(
                1, TOTAL_PAGES + 1)]

            for _ in pb(as_completed(future), label='Querying TMDB:', total=TOTAL_PAGES):
                pass

    print()

    with ProgressBar(title=MD('**Compiling Information:**')) as pb:
        def scan_crew(movie: Dict[str, Any]):
            movie['year'] = movie['release_date'][:4]

            crew = tmdb.Movies(movie['id']).credits()['crew']

            for person in crew:
                if person['job'] == 'Director':
                    if 'directors' not in movie:
                        movie['directors'] = [person]

                    else:
                        movie['directors'].append(person)

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
            return print_formatted_text(HTML(f'<b fg="{color}">{text}</b>'))

        qa_response(answer, movie, print_result)


def base_end():
    print_formatted_text(MD('*Bye!*'))
    print('This product uses the TMDb API but is not endorsed or certified by TMDb.')
