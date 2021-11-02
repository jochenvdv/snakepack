import string
from itertools import chain, cycle, dropwhile, islice, permutations, repeat, count
from typing import Mapping, Iterable, Dict, Set, Optional, List, Generator

from libcst.metadata import Scope, Assignment



class NameRegistry:
    def __init__(self):
        self._scopes: Dict[Scope, Generator[str, None, None]] = {}

    def register_name_for_scope(self, scope: Scope) -> str:
        if scope not in self._scopes:
            self._scopes[scope] = self._generate_identifiers()

        return next(self._scopes[scope])

    def _generate_identifiers(self):
        first_chars = string.ascii_letters
        chars = first_chars + string.digits

        yield from first_chars
        size = 2

        while True:
            yield from map(lambda x: ''.join(x), permutations(chars, size))
            size += 1

