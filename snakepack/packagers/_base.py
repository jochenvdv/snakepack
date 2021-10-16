from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Iterable, Dict

from snakepack.bundlers import Bundle


class Package:
    def __init__(self, name: str, packager: Packager, bundles: Iterable[Bundle]):
        self._name = name
        self._packager = packager
        self._bundles = {bundle.name: bundle for bundle in bundles}

    @property
    def name(self):
        return self._name

    @property
    def bundles(self) -> Dict[str, Bundle]:
        return self._bundles

    @property
    def packager(self) -> Packager:
        return self._packager

    def package(self):
        return self._packager.package(self)


class Packager(ABC):
    @abstractmethod
    def package(self, package: Package):
        raise NotImplementedError
