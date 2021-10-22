from abc import ABC, abstractmethod
from typing import Mapping, Iterable

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource
from snakepack.config import ConfigurableComponent


class Loader(ConfigurableComponent, ABC):
    @abstractmethod
    def load(self) -> Iterable[Asset]:
        raise NotImplementedError