from abc import ABC
from typing import Union, Mapping

from libcst import MetadataWrapper

from snakepack.analyzers import Analyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule


class PythonModuleCstAnalyzer(Analyzer, ABC):
    class Analysis(Analyzer.Analysis):
        def __init__(self, modules_metadata: Mapping[PythonModule, MetadataWrapper]):
            self._modules_metadata = modules_metadata

        def __getitem__(self, item):
            return self._modules_metadata[item]

    __config_name__ = NotImplemented

