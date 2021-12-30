import sys
from collections import defaultdict
from functools import reduce
from operator import getitem

from pathlib import Path
from site import getsitepackages
from typing import List

from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import ModuleGraph, Package, Node
from stdlib_list import stdlib_list

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.assets._base import FileContentSource
from snakepack.assets.python import PythonModule, PythonApplication, PythonPackage, PythonModuleCst
from snakepack.config.options import Options
from snakepack.config.types import FullyQualifiedPythonName
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
            includes=self._options.includes,
            target_version=self._options.target_version
        )

        self._analysis = analyzer.analyse()
        self._analysis = analyzer.analyse_assets(self._analysis.asset_group)

        return self._analysis.asset_group

    class Options(Options):
        entry_point: Path
        exclude_stdlib: bool = True
        target_version: str = '3.9'
        includes: List[FullyQualifiedPythonName] = []

    __config_name__ = 'import_graph'


class PackageLoader(Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analysis = None

    def load(self) -> PythonPackage:
        pkg_name = self._options.pkg_name.module_path[0]
        pkg_path = self._global_options.source_base_path / pkg_name

        python_pkg = self._load_package(pkg_name, pkg_path)
        analyzer = ImportGraphAnalyzer(
            entry_point_path=None,
            target_version=self._options.target_version
        )
        self._analysis = analyzer.analyse_assets(python_pkg)

        return python_pkg

    @property
    def analysis(self) -> ImportGraphAnalyzer.Analysis:
        return self._analysis

    @staticmethod
    def _load_package(pkg_name, pkg_path: Path):
        subpackages = []
        modules = []
        package = PythonPackage(full_name=pkg_name, subpackages=subpackages, modules=modules)

        for path in pkg_path.iterdir():
            full_name = f'{pkg_name}.{path.stem}'

            if path.is_dir() and (path / '__init__.py').is_file():
                # subpackage
                subpackages.append(PackageLoader._load_package(full_name, path))
            elif path.suffix == '.py':
                # module
                modules.append(
                    PythonModule.from_source(
                        full_name=full_name,
                        source=FileContentSource(path=path, default_content_type=PythonModuleCst)
                    )
                )

        return package

    class Options(Options):
        pkg_name: FullyQualifiedPythonName
        target_version: str = '3.9'

    __config_name__ = 'package'


__all__ = [
    ImportGraphLoader,
    PackageLoader
]