import string
from functools import lru_cache

import mistune
from cytoolz.functoolz import pipe
from prompt_toolkit import HTML
from textacy.preprocessing import (normalize_whitespace, remove_accents,
                                   remove_punctuation)


def MD(text: str) -> HTML:
    return HTML(mistune.html(text))


@lru_cache()
def normalize(text: str) -> str:
    space = len(text) > 0 and text[-1] in string.whitespace

    text = text.lower()

    text = pipe(
        text,
        remove_accents,
        remove_punctuation,
        normalize_whitespace
    )

    if space:
        return f'{text} '

    return text
