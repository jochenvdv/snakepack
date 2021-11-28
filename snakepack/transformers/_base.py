from abc import ABC, abstractmethod
from typing import Type, Mapping, Union

from snakepack.analyzers import Analyzer
from snakepack.assets import Asset, AssetContent, AssetGroup
from snakepack.config.options import ConfigurableComponent


class Transformer(ConfigurableComponent, ABC):
    REQUIRED_ANALYZERS = []

    @abstractmethod
    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[Asset, AssetGroup]
    ) -> Union[Asset, AssetGroup]:
        raise NotImplementedError
