import re
from difflib import SequenceMatcher
from itertools import groupby
from typing import Any, Dict, Iterable, List, Tuple

# import pycorpora
import sre_yield
from fuzzyfinder import fuzzyfinder
from prompt_toolkit.completion import Completer, Completion
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')


def _levenshtein():
    pass


def _fuzzy():
    pass


def _word2vec():
    pass


# STOPWORDS = pycorpora.words.stopwords.en['stopWords']
STOPWORDS = stopwords.words('english')


def _strip_stopwords(s: str) -> str:
    arr = s.split(' ')

    if arr[-1] == '':
        index = -2
    else:
        index = -1

    arr = [x for x in arr[:index] if x.lower() not in STOPWORDS] + arr[index:]

    return ' '.join(arr)


print(_strip_stopwords('The Nightmare on Elm Street').replace(' ', 'x'))
print(_strip_stopwords('The ').replace(' ', 'x'))


class TitleCompleter(Completer):
    dup_space = re.compile(' +')

    def __init__(self, options: List[Dict[str, Any]]):
        self.options: List[Tuple[str, str]] = []
        self.titles: Dict[str, str] = {}

        for option in options:
            opts: List[Tuple[str, str]] = []

            true_title = '{title} ({year})'.format_map(option)
            self.titles[true_title] = true_title

            for title in sre_yield.AllStrings(option['pattern'], max_count=1):
                # title = '{} ({})'.format(title, option['year'])
                opts.append((true_title, _strip_stopwords(title).strip()))

            if 'alt_titles' not in option.keys():
                self.options.extend(opts)
                continue

            for alt in option['alt_titles']:
                true_alt_title = '{} ({})'.format(alt['title'], option['year'])

                for title in sre_yield.AllStrings(alt['pattern'], max_count=1):
                    # title = '{} ({})'.format(title, option['year'])
                    opts.append(
                        (true_alt_title, _strip_stopwords(title).strip()))
                    self.titles[true_alt_title] = true_title

            self.options.extend(opts)

    def get_completions(self, document, complete_event):
        line = document.current_line_before_cursor
        length = len(line)
        word = _strip_stopwords(self.dup_space.sub(' ', line.lstrip()).lower())

        match_set = set()
        matches = []

        for i in self._sequence_match(word, length):
            match_set.add(self.titles[i[:-7]])
            matches.append(i)

        for i in fuzzyfinder(word, self.options,
                             accessor=lambda x: x[1].lower()):
            title = self.titles[i[0]]
            if title not in match_set:
                match_set.add(title)
                matches.append('{} [FUZZ]'.format(i[0]))

        for m in matches:
            yield Completion(self.titles[m[:-7]], -length, m)

    def _sequence_match(self, word, length) -> List[str]:
        matches: Iterable[Tuple[float, str, str]] = (
            (SequenceMatcher(None, word,
                             w[1].lower()).ratio(), *w)
            for w in self.options)

        matches = sorted(matches, key=lambda x: x[0], reverse=True)

        matches = filter(lambda x: x[0] >= .75, matches)

        new_matches = []

        # def comp(x):
        #     return SequenceMatcher(None, word, x[2].lower()).ratio()

        for _, g in groupby(matches, key=lambda x: x[0]):
            new_matches.extend(sorted(g, key=lambda x: x[2]))

        return ['{1} [{0:.2f}]'.format(*m) for m in new_matches]
