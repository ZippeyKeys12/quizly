from typing import List, Iterable, Dict, TypeVar, Generic, Callable

T = TypeVar('T')


class TrieNode(Generic[T]):
    def __init__(self, value: T):
        self.value = value
        self.children: Dict[T, TrieNode[T]] = {}
        self.is_complete = False

    def get_paths(self) -> List[List[T]]:
        paths = []
        if self.is_complete:
            paths.append([self.value])

        for child in self.children.values():
            for comp in child.get_paths():
                paths.append([self.value] + comp)

        return paths


class Trie(Generic[T]):
    def __init__(self, default: T, merger: Callable[[Iterable[T]], Iterable[T]] = lambda x: x):
        self.root = TrieNode(default)
        self.merger = merger

    def add(self, new_value: Iterable[T]):
        curr = self.root

        for val in new_value:
            if val not in curr.children:
                curr.children[val] = TrieNode(val)

            curr = curr.children[val]

        curr.is_complete = True

    def get_children(self, item: Iterable[T]) -> Dict[T, TrieNode[T]]:
        curr = self.root

        for val in item:
            if val in curr.children:
                curr = curr.children[val]

            else:
                raise KeyError(f'{item}')

        return curr.children

    def get_completions(self, prefix: Iterable[T]) -> List[Iterable[T]]:
        curr = self.root
        path = []

        for val in prefix:
            path.append(val)

            if val in curr.children:
                curr = curr.children[val]

            else:
                raise KeyError(f'{prefix}')

        return [self.merger(path[:-1] + x) for x in curr.get_paths()]

    def __contains__(self, item: Iterable[T]) -> bool:
        curr = self.root

        for val in item:
            if val in curr.children:
                curr = curr.children[val]

            else:
                return False

        return curr.is_complete
