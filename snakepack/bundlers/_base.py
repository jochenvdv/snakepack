from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence, Optional

from snakepack.assets import Asset, AssetGroup
from snakepack.config.options import ConfigurableComponent
from snakepack.loaders import Loader
from snakepack.transformers import Transformer


class Bundle:
    def __init__(self, name: str, bundler: Bundler, loader: Loader, transformers: Sequence[Transformer]):
        self._name = name
        self._bundler = bundler
        self._loader = loader
        self._asset_group: Optional[AssetGroup] = None
        self._transformers = transformers

    @property
    def name(self) -> str:
        return self._name

    @property
    def bundler(self) -> Bundler:
        return self._bundler

    @property
    def loader(self) -> Loader:
        return self._loader

    @property
    def asset_group(self) -> AssetGroup:
        return self._asset_group

    @property
    def transformers(self) -> Sequence[Transformer]:
        return self._transformers

    def load(self):
        self._asset_group = self._loader.load()

    def bundle(self, *args, **kwargs):
        return self._bundler.bundle(self, *args, **kwargs)


class Bundler(ConfigurableComponent, ABC):
    @abstractmethod
    def bundle(self, bundle: Bundle, package):
        raise NotImplementedError
