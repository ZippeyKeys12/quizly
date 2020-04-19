from typing import Sequence, TypeVar

import numpy as np

T = TypeVar('T')


def levenshtein_distance(one: Sequence[T], two: Sequence[T]) -> int:
    l1 = len(one) + 1
    l2 = len(two) + 1

    distances = np.zeros((l1, l2))

    for i in range(l1):
        distances[i][0] = i

    for i in range(l2):
        distances[0][i] = i

    for i in range(1, l1):
        for j in range(1, l2):
            if (one[i - 1] == two[j - 1]):
                distances[i][j] = distances[i - 1][j - 1]

            else:
                distances[i][j] = 1 + min(
                    distances[i][j - 1],
                    distances[i - 1][j],
                    distances[i - 1][j - 1]
                )

    return distances[l1 - 1][l2 - 1]


def levenshtein_ratio(one: Sequence[T], two: Sequence[T]) -> float:
    return 2 * levenshtein_distance(one, two) / (len(one) + len(two))
