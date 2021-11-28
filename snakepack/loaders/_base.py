from abc import ABC, abstractmethod
from typing import Mapping, Iterable

from snakepack.assets import AssetGroup
from snakepack.config.options import ConfigurableComponent


class Loader(ConfigurableComponent, ABC):
    @abstractmethod
    def load(self) -> AssetGroup:
        raise NotImplementedError