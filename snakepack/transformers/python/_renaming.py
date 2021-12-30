import string
from collections import deque
from itertools import chain, cycle, dropwhile, islice, permutations, repeat, count
from keyword import iskeyword
from typing import Mapping, Iterable, Dict, Set, Optional, List, Generator, Deque, Tuple

from libcst.metadata import Scope, Assignment


class NameRegistry:
    def __init__(self):
        self._scopes: Dict[Scope, Tuple[Generator[str, None, None], Deque]] = {}
        self._registered_names: Dict[Scope, Set[str]] = {}

    def generate_name_for_scope(self, scope: Scope) -> str:
        if scope not in self._scopes:
            self._scopes[scope] = self._generate_identifiers()

        if scope not in self._registered_names:
            self._registered_names[scope] = set()

        name = None

        while name is None or name in self._registered_names[scope] or iskeyword(name):
            name = next(self._scopes[scope])

        return name

    def register_name_for_scope(self, scope: Scope, name: str):
        if scope not in self._registered_names:
            self._registered_names[scope] = set()

        self._registered_names[scope].add(name)
        self._scopes[scope] = self._generate_identifiers()

    def reset(self, scope: Scope):
        self._scopes[scope] = self._generate_identifiers()

    def _generate_identifiers(self):
        first_chars = string.ascii_letters
        chars = first_chars + string.digits

        yield from first_chars
        size = 2

        while True:
            yield from map(lambda x: ''.join(x), permutations(chars, size))
            size += 1

