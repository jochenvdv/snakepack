from abc import ABC, abstractmethod
from typing import Mapping

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource


class Loader(ABC):
    @abstractmethod
    def load(self) -> Mapping[Asset, AssetContentSource]:
        raise NotImplementedError