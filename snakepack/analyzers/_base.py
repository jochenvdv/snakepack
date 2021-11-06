from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

from snakepack.assets import Asset, AssetGroup


class Analyzer(ABC):
    @abstractmethod
    def analyse(self, subject: Union[Asset, AssetGroup]) -> Analysis:
        raise NotImplementedError

    class Analysis(ABC):
        pass