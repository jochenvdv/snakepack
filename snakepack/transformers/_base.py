from abc import ABC, abstractmethod

from snakepack.assets import Asset
from snakepack.config import ConfigurableComponent


class Transformer(ConfigurableComponent, ABC):
    @abstractmethod
    def transform(self, asset: Asset):
        raise NotImplementedError
