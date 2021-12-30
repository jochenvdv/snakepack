from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

from snakepack.assets import Asset, AssetGroup


class Analyzer(ABC):
    class Analysis(ABC):
        pass


class PostLoadingAnalyzer(Analyzer, ABC):
    @abstractmethod
    def analyse_assets(self, asset_group: AssetGroup) -> Analysis:
        raise NotImplementedError

    class Analysis(ABC):
        pass


class SubjectAnalyzer(Analyzer, ABC):
    @abstractmethod
    def analyse_subject(self, subject: Asset) -> Analysis:
        raise NotImplementedError

    class Analysis(ABC):
        pass