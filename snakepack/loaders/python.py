import sys
from collections import defaultdict
from functools import reduce
from operator import getitem

from pathlib import Path
from site import getsitepackages

from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import ModuleGraph, Package, Node
from stdlib_list import stdlib_list

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.assets._base import FileContentSource
from snakepack.assets.python import PythonModule, PythonApplication, PythonPackage
from snakepack.config.options import Options
from snakepack.loaders import Loader


class ImportGraphLoader(Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analysis = None

    @property
    def analysis(self) -> ImportGraphAnalyzer.Analysis:
        return self._analysis

    def load(self) -> PythonApplication:
        entry_point_path = self.global_options.source_base_path / self._options.entry_point
        analyzer = ImportGraphAnalyzer(
            entry_point_path=entry_point_path,
            target_version=self._options.target_version
        )

        self._analysis = analyzer.analyse()

        return self._analysis.application

    class Options(Options):
        entry_point: Path
        exclude_stdlib: bool = True
        target_version: str = '3.9'

    __config_name__ = 'import_graph'


__all__ = [
    ImportGraphLoader
]