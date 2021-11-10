import string
from collections import deque
from itertools import chain, cycle, dropwhile, islice, permutations, repeat, count
from typing import Mapping, Iterable, Dict, Set, Optional, List, Generator, Deque, Tuple

from libcst.metadata import Scope, Assignment


class NameRegistry:
    def __init__(self):
        self._scopes: Dict[Scope, Tuple[Generator[str, None, None], Deque]] = {}

    def generate_name_for_scope(self, scope: Scope, exclude_existing=False) -> str:
        if scope not in self._scopes:
            self._scopes[scope] = (self._generate_identifiers(), deque())

        if len(self._scopes[scope][1]) > 0:
            name = self._scopes[scope][1][-1]
        else:
            name = next(self._scopes[scope][0])
            self._scopes[scope][1].appendleft(name)

        return name

    def register_name_for_scope(self, scope: Scope, name: str):
        assert len(self._scopes[scope][1]) > 0
        registered_name = self._scopes[scope][1].pop()
        assert registered_name == name

    def _generate_identifiers(self):
        first_chars = string.ascii_letters
        chars = first_chars + string.digits

        yield from first_chars
        size = 2

        while True:
            yield from map(lambda x: ''.join(x), permutations(chars, size))
            size += 1

