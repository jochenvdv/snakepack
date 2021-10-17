from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from snakepack.assets import Asset
from snakepack.config import ConfigurableComponent
from snakepack.transformers import Transformer


class Bundle:
    def __init__(self, name: str, bundler: Bundler, assets: Iterable[Asset], transformers: Sequence[Transformer]):
        self._name = name
        self._bundler = bundler
        self._assets = assets
        self._transformers = transformers

    @property
    def name(self) -> str:
        return self._name

    @property
    def bundler(self) -> Bundler:
        return self._bundler

    @property
    def assets(self) -> Iterable[Asset]:
        return self._assets

    @property
    def transformers(self) -> Sequence[Transformer]:
        return self._transformers

    def bundle(self):
        return self._bundler.bundle(self)


class Bundler(ConfigurableComponent, ABC):
    @abstractmethod
    def bundle(self, bundle: Bundle):
        raise NotImplementedError
