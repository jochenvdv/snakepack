from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from snakepack.assets import Asset


class Bundle:
    def __init__(self, name: str, bundler: Bundler, assets: Iterable[Asset]):
        self._name = name
        self._bundler = bundler
        self._assets = assets

    @property
    def name(self) -> str:
        return self._name

    @property
    def bundler(self) -> Bundler:
        return self._bundler

    @property
    def assets(self) -> Iterable[Asset]:
        return self._assets

    def bundle(self):
        return self._bundler.bundle(self)


class Bundler(ABC):
    @abstractmethod
    def bundle(self, bundle: Bundle):
        raise NotImplementedError
