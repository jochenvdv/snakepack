from abc import ABC, abstractmethod
from typing import Type, Mapping, Union

from snakepack.analyzers import Analyzer
from snakepack.assets import Asset, AssetContent, AssetGroup
from snakepack.config import ConfigurableComponent


class Transformer(ConfigurableComponent, ABC):
    @abstractmethod
    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[Asset, AssetGroup]
    ) -> Union[Asset, AssetGroup]:
        raise NotImplementedError
