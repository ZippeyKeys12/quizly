import re
from typing import List, Tuple

from cytoolz import compose

_ws = re.compile(r'\s+')


def fuzzy_match(pattern: str, text: str) -> Tuple[List[str], str]:
    pattern = _ws.sub(' ', pattern)
    pattern = ''.join(map(compose('({})'.format, re.escape), pattern))

    matches = []

    for sep in ['.*', '.*?']:
        regex = re.compile('(?=({}))'.format(sep.join(pattern)), re.IGNORECASE)

        r = list(regex.finditer(text))

        if r:
            for x in r:
                start = None
                num = 0
                parts: List[str] = []
                for i in range(2, regex.groups + 1):
                    if start is None:
                        start = x.start(i)
                        num = 1

                    elif x.start(i) > start + num:
                        parts.append(x.string[start:start + num])

                        start = x.start(i)
                        num = 1

                    elif i == regex.groups:
                        parts.append(x.string[start:x.end(i)])

                    else:
                        num += 1

                caught = x.string[x.start(1):x.end(1)]

                matches.append((len(parts), len(caught), parts, caught))

    return min(matches)[2:]
