from typing import Iterable, TypeVar

T = TypeVar('T')


def jaccard_index(one: Iterable[T], two: Iterable[T]) -> float:
    a = set(one)
    b = set(two)

    return len(a & b) / len(a | b)


def jaccard_distance(one: Iterable[T], two: Iterable[T]) -> float:
    return 1 - jaccard_index(one, two)
