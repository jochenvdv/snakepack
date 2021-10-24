from abc import ABC, abstractmethod

from snakepack.assets import Asset, AssetContent
from snakepack.config import ConfigurableComponent


class Transformer(ConfigurableComponent, ABC):
    @abstractmethod
    def transform(self, content: AssetContent) -> AssetContent:
        raise NotImplementedError
