from __future__  import annotations

from abc import ABC, abstractmethod
from typing import Union, Mapping, Iterable, Optional

from boltons.iterutils import flatten
from libcst import MetadataWrapper

from snakepack.analyzers import Analyzer
from snakepack.analyzers._base import SubjectAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule


class PythonModuleCstAnalyzer(SubjectAnalyzer, ABC):
    @abstractmethod
    def analyse_subject(self, subject: Union[Asset, AssetGroup]) -> Analysis:
        raise NotImplementedError

    CST_PROVIDERS = set()

    def create_analysis(
            self,
            metadata: Mapping[PythonModule, MetadataWrapper]
    ) -> PythonModuleCstAnalyzer.Analysis:
        return self.Analysis(metadata=metadata)

    class Analysis(Analyzer.Analysis):
        def __init__(self, metadata: MetadataWrapper):
            self._metadata = metadata

        def __getitem__(self, item):
            return self._metadata[item]

    __config_name__ = NotImplemented


class BatchPythonModuleCstAnalyzer(SubjectAnalyzer):
    def __init__(self, analyzers: Iterable[PythonModuleCstAnalyzer]):
        self._analyzers = analyzers

    def analyse_subject(self, subject) -> Mapping[PythonModuleCstAnalyzer, PythonModuleCstAnalyzer.Analysis]:
        providers = set(flatten(map(lambda x: x.CST_PROVIDERS, self._analyzers)))
        modules_metadata = subject.content.metadata_wrapper.resolve_many(providers)
        analyses = {}

        for analyzer in self._analyzers:
            analysis = analyzer.create_analysis(modules_metadata)
            analyses[analyzer.__class__] = analysis

        return analyses