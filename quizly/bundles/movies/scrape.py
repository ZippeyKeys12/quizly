import re
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup


def _is_movie_poster(tag) -> bool:
    return tag.name == 'div' and tag.has_attr('class') and 'film-poster'in tag['class']


def scrape_list(url: str) -> Tuple[str, str, str, List[str]]:
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'lxml')
    movies = soup.find_all(_is_movie_poster)
    title = soup.find(lambda x: x.name == 'h1' and x.has_attr(
        'itemprop') and x['itemprop'] == 'title').text.strip()
    creator = soup.find(lambda x: x.name == 'span' and x.has_attr(
        'itemprop') and x['itemprop'] == 'name').text.strip()

    return title, creator, r.url, list(map(lambda x: x['data-target-link'], movies))


LINK_PTN = re.compile(r'https://www.themoviedb\.org/movie/(\d+)/')


def _is_tmdb_link(tag) -> bool:
    return tag.has_attr('data-track-action') and tag['data-track-action'] == 'TMDb'


def scrape_movie(url: str) -> str:
    r = requests.get(f'https://letterboxd.com{url}')

    link = LINK_PTN.match(BeautifulSoup(
        r.text, 'lxml').find(_is_tmdb_link)['href'])

    if link is None:
        return ''
    else:
        return link.group(1)


if __name__ == "__main__":
    title, creator, url, films = scrape_list('https://boxd.it/42ipE')
    print([scrape_movie(m) for m in films])
