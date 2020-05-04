import re
from typing import List

import requests
from bs4 import BeautifulSoup


def _is_movie_poster(tag) -> bool:
    return tag.name == 'div' and tag.has_attr('class') and 'film-poster'in tag['class']


def scrape_list(url: str) -> List[str]:
    r = requests.get(url)
    movies = BeautifulSoup(r.text, 'lxml').find_all(_is_movie_poster)

    return list(map(lambda x: x['data-target-link'], movies))


LINK_PTN = re.compile(r'https://www.themoviedb\.org/movie/(\d+)/')


def _is_tmdb_link(tag) -> bool:
    return tag.has_attr('data-track-action') and tag['data-track-action'] == 'TMDb'


def scrape_movie(url: str) -> int:
    r = requests.get(f'https://letterboxd.com{url}')

    link = LINK_PTN.match(BeautifulSoup(
        r.text, 'lxml').find(_is_tmdb_link)['href'])

    if link is None:
        return -1
    else:
        return int(link.group(1))


if __name__ == "__main__":
    print(scrape_list('https://boxd.it/42ipE'))

    print(scrape_movie('/film/black-panther-2018/'))
