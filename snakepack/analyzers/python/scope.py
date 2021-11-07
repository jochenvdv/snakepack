from __future__ import annotations

from typing import Union

from libcst import MetadataWrapper
from libcst.metadata import ScopeProvider, ExpressionContextProvider

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst


class ScopeAnalyzer(PythonModuleCstAnalyzer):
    def analyse(self, subject: Union[Asset, AssetGroup]) -> ScopeAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve(ScopeProvider)

            return ScopeAnalyzer.Analysis(
                modules_metadata={
                    subject: metadata
                }
            )
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        pass
