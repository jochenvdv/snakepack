from abc import ABC, abstractmethod

from snakepack.assets import Asset


class Transformer(ABC):
    @abstractmethod
    def transform(self, asset: Asset):
        raise NotImplementedError
