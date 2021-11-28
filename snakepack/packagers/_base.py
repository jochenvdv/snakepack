from __future__ import annotations

from abc import abstractmethod, ABC
from pathlib import Path
from typing import Iterable, Dict, Optional

from snakepack.bundlers import Bundle
from snakepack.config.options import Options, ConfigurableComponent


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

    @property
    def target_path(self) -> Path:
        return self._packager.get_target_path(self)

    def package(self):
        return self._packager.package(self)


class Packager(ConfigurableComponent, ABC):
    @abstractmethod
    def package(self, package: Package):
        raise NotImplementedError

    @abstractmethod
    def get_target_path(self, package: Package) -> Path:
        raise NotImplementedError
